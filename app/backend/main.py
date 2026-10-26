"""Harbourline Capital Deal Room — FastAPI backend. Governed reads run as the signed-in role (OBO); app state + serving tables in Lakebase."""
import json, os, re, time, datetime as dt
from dataclasses import asdict
from functools import lru_cache
import requests
from fastapi import FastAPI, Request, HTTPException, UploadFile, File
from fastapi.responses import FileResponse, Response, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend import db
from harbourline.app import stages, inbox
from harbourline.ai.widget_spec import catalog_from_yaml, to_lakeview_widget, widget_sql, WidgetSpec

app = FastAPI(title="Harbourline Capital · Deal Room")

@app.exception_handler(Exception)
async def _errors(request: Request, exc: Exception):
    msg = str(exc)
    if any(k in msg for k in ("INSUFFICIENT_PERMISSIONS", "PERMISSION_DENIED", "does not have", "Can View")):
        return JSONResponse({"detail": "Not visible to your role (Unity Catalog): " + msg.split("SQLSTATE")[0][-300:]}, status_code=403)
    print("unhandled:", repr(exc)[:500])
    return JSONResponse({"detail": msg[:300]}, status_code=500)
C = db.CATALOG
VDR, SEM, GOV, AI = (f"{C}.vdr", f"{C}.semantic", f"{C}.governance", f"{C}.ai")
CFG = json.load(open(os.path.join(os.path.dirname(__file__), "demo_ids.json")))
HOST = "https://" + db.HOST
ROLE_PAGES = {
    "role-business-user": ["tasks", "dealroom", "stage3"],
    "role-approver": ["tasks", "dealroom", "stage3", "audit"],
    "role-it-ai-owner": ["tasks", "audit"],
    "role-external-gp": ["portal"],
}

@app.on_event("startup")
def _startup():
    try:
        db.init_schema()
    except Exception as e:                       # app still serves governed pages; state pages report the error
        print("lakebase init failed:", e)

# ---------------- identity ----------------
@lru_cache(maxsize=256)
def _who(token: str) -> str:
    return db.q_user(token, "SELECT current_user() AS u")[0]["u"]

class Ctx:
    def __init__(self, request: Request):
        self.token = request.headers.get("x-forwarded-access-token") or os.environ.get("GE_DEV_TOKEN")   # dev only: never set in app.yaml
        if not self.token:
            raise HTTPException(401, "User authorization token missing — open the app from Databricks (never falls back to the app identity)")
        self.email = request.headers.get("x-forwarded-email", "")
        self.role = _who(self.token)                 # assumed role name, or the user's email when no role is active
        self.is_role = self.role.startswith("role-")

    def q(self, query, params=None):
        return db.q_user(self.token, query, params)

    def require(self, *roles):
        if self.role not in roles:
            raise HTTPException(403, f"{self.role} cannot do this (needs {', '.join(roles)})")

def ctx(request: Request) -> Ctx:
    return Ctx(request)

def user_file(c: Ctx, path: str) -> bytes:
    r = requests.get(f"{HOST}/api/2.0/fs/files{path}", headers={"Authorization": f"Bearer {c.token}"}, timeout=120)
    if r.status_code != 200:
        raise HTTPException(403 if r.status_code in (401, 403, 404) else r.status_code, f"not visible to {c.role}")
    return r.content

def user_dir(c: Ctx, path: str) -> list:
    r = requests.get(f"{HOST}/api/2.0/fs/directories{path}", headers={"Authorization": f"Bearer {c.token}"}, timeout=60)
    if r.status_code != 200:
        raise HTTPException(403, f"not visible to {c.role}")
    return r.json().get("contents", [])

@app.get("/api/me")
def me(request: Request):
    c = ctx(request)
    return {"email": c.email, "role": c.role, "is_role": c.is_role, "pages": ROLE_PAGES.get(c.role, ["tasks"]),
            "host": HOST, "workspace_id": CFG["workspace_id"], "role_ids": CFG["roles"]}

# ---------------- My tasks ----------------
def _app_state():
    st = {"stage_pending": [], "agent_versions_awaiting": []}
    st["feedback"] = db.pg_q("SELECT body, extract(day FROM now() - at)::int AS age_days FROM hl_app.feedback ORDER BY at DESC LIMIT 5")
    return st

@app.get("/api/tasks")
def tasks(request: Request):
    c = ctx(request)
    st = _app_state()
    if c.role in ("role-approver", "role-business-user"):
        if c.role == "role-approver":
            st.pop("feedback", None)          # executive instructions go to the deal-room controller (business user)
        for inv in ("Solace Grid Energy",):
            d = _dealroom(c, inv)
            g = d["gate"]
            if g["documents_complete"] and g["missing_approvals"]:
                st["stage_pending"].append({"investment": inv, "stage": d["stage"], "approval": g["missing_approvals"][0]})
    return {"role": c.role, "tasks": inbox.tasks_for(c.role, st)}

# ---------------- Deal rooms (deal room) ----------------
def _dealroom(c: Ctx, inv: str) -> dict:
    stage_row = db.pg_q("SELECT stage, gate_due FROM hl_app.deal_stage WHERE investment = %s", (inv,))
    stage = stage_row[0]["stage"] if stage_row else 1
    items = c.q(f"SELECT stage, item, kind, requirement, validity_days FROM {VDR}.checklist_items WHERE investment = :inv ORDER BY stage, kind DESC, item",
                {"inv": inv})
    status = {(r["stage"], r["item"]): r for r in db.pg_q("SELECT * FROM hl_app.stage_items WHERE investment = %s", (inv,))}
    files = c.q(f"SELECT file_id, name, file_type, stage, source, classification, status, received_at, path FROM {VDR}.file_register WHERE deal_room = :inv ORDER BY received_at",
                {"inv": inv})
    ext = c.q(f"SELECT file_id, field, value, confidence, reviewed_by, corrected_value FROM {VDR}.doc_extracts WHERE deal_room = :inv", {"inv": inv})
    by_type = {}
    for f in files:
        by_type.setdefault(f["file_type"], []).append(f)
    rows = []
    for it in items:
        s = status.get((it["stage"], it["item"]))
        f = (by_type.get(it["item"]) or [None])[-1]
        st = s["status"] if s else ("Received" if f else "Missing")
        rows.append({**it, "status": st, "file": f, "updated": s and {"by": s["run_by"], "as": s["run_as"], "at": s["at"]}})
    cur = [r for r in rows if r["stage"] == stage]
    gate = stages.gate_status([{"item": r["item"], "kind": r["kind"], "requirement": r["requirement"],
                                "status": r["status"]} for r in cur])
    alerts = [a for a in c.q(f"SELECT stage, alert_type, message FROM {VDR}.risk_alerts WHERE investment = :inv", {"inv": inv})
              if a["stage"] is None or int(a["stage"]) == stage]                      # current stage + cross-document alerts
    return {"investment": inv, "stage": stage, "gate_due": stage_row[0]["gate_due"] if stage_row else None,
            "items": rows, "gate": gate, "files": files, "extracts": ext, "alerts": alerts}

@app.get("/api/dealroom/{inv}")
def dealroom(inv: str, request: Request):
    return _dealroom(ctx(request), inv)

@app.post("/api/dealroom/{inv}/item")
async def dealroom_item(inv: str, request: Request):
    """Approve / waive / mark NA a checklist item (approver), or approve a document (approver)."""
    c = ctx(request); b = await request.json()
    c.require("role-approver")
    stage, item, status = int(b["stage"]), b["item"], b["status"]
    if status not in ("Approved", "Waived", "NotApplicable", "Pending", "Missing"):
        raise HTTPException(400, "bad status")
    d = _dealroom(c, inv)
    it = next((r for r in d["items"] if r["stage"] == stage and r["item"] == item), None)
    if not it:
        raise HTTPException(404, "item not found")
    why = stages.check_item_change(it["kind"], it["requirement"], status, has_file=bool(it["file"]))
    if why:
        raise HTTPException(409, why)
    if it["kind"] == "approval" and status == "Approved" and stage == d["stage"] and not d["gate"]["documents_complete"]:
        raise HTTPException(409, "Stage approval is locked until all required documents are approved: " + ", ".join(d["gate"]["gaps"]))
    valid = (dt.date.today() + dt.timedelta(days=int(it["validity_days"]))) if it.get("validity_days") and status == "Approved" else None
    db.pg_q("""INSERT INTO hl_app.stage_items(investment, stage, item, status, valid_until, run_by, run_as) VALUES (%s,%s,%s,%s,%s,%s,%s)
               ON CONFLICT (investment, stage, item) DO UPDATE SET status = EXCLUDED.status, valid_until = EXCLUDED.valid_until,
               run_by = EXCLUDED.run_by, run_as = EXCLUDED.run_as, at = now()""", (inv, stage, item, status, valid, c.email, c.role))
    db.log_approval("stage_item", f"{inv}|{stage}|{item}", status, b.get("note", ""), c.email, c.role)
    try:                                         # sync back to Delta for dashboards / Genie / audit
        db.q_app(f"""MERGE INTO {VDR}.checklist_status t USING (SELECT :inv investment, 'Fund I' portfolio, :st stage, :it item, :s status,
                    CAST(:v AS DATE) valid_until, CAST(:g AS DATE) gate_due, :by updated_by, current_timestamp() updated_at) s
                    ON t.investment = s.investment AND t.stage = s.stage AND t.item = s.item
                    WHEN MATCHED THEN UPDATE SET * WHEN NOT MATCHED THEN INSERT *""",
                 {"inv": inv, "st": stage, "it": item, "s": status, "v": str(valid) if valid else None,
                  "g": str(d["gate_due"]) if d["gate_due"] else None, "by": f"{c.email} as {c.role}"})
    except Exception as e:
        print("delta sync failed:", e)
    return _dealroom(c, inv)

@app.post("/api/dealroom/{inv}/advance")
def dealroom_advance(inv: str, request: Request):
    c = ctx(request); c.require("role-approver")
    d = _dealroom(c, inv)
    if not d["gate"]["can_advance"]:
        raise HTTPException(409, {"gaps": d["gate"]["gaps"], "missing_approvals": d["gate"]["missing_approvals"]})
    if d["stage"] >= 3:
        raise HTTPException(409, "already at the final stage")
    nxt = d["stage"] + 1
    db.pg_q("""INSERT INTO hl_app.deal_stage(investment, stage, gate_due) VALUES (%s,%s,%s)
               ON CONFLICT (investment) DO UPDATE SET stage = EXCLUDED.stage, gate_due = EXCLUDED.gate_due, at = now()""",
            (inv, nxt, dt.date.today() + dt.timedelta(days=5)))
    db.log_approval("stage_gate", f"{inv}|{d['stage']}->{nxt}", "Advanced", "", c.email, c.role)
    return _dealroom(c, inv)

@app.get("/api/files/{file_id}")
def file_preview(file_id: str, request: Request):
    c = ctx(request)
    rows = c.q(f"SELECT path, name FROM {VDR}.file_register WHERE file_id = :f", {"f": file_id})
    if not rows:
        raise HTTPException(404, "not visible to you")
    if rows[0]["path"].startswith("https://"):       # SharePoint file: bytes were ingested into file_content (same row filter applies)
        blob = c.q(f"SELECT content FROM {VDR}.file_content WHERE file_id = :f", {"f": file_id})
        if not blob:
            raise HTTPException(404, "not visible to you")
        return Response(bytes(blob[0]["content"]), media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="{rows[0]["name"]}"'})
    path = rows[0]["path"].replace("dbfs:", "")
    r = requests.get(f"{HOST}/api/2.0/fs/files{path}", headers={"Authorization": f"Bearer {c.token}"}, timeout=60)
    if r.status_code != 200:
        raise HTTPException(r.status_code, r.text[:200])
    return Response(r.content, media_type="application/pdf", headers={"Content-Disposition": f'inline; filename="{rows[0]["name"]}"'})

@app.post("/api/extract/{file_id}/review")
async def extract_review(file_id: str, request: Request):
    c = ctx(request); b = await request.json()
    c.require("role-approver", "role-business-user")
    if not c.q(f"SELECT 1 FROM {VDR}.file_register WHERE file_id = :f", {"f": file_id}):
        raise HTTPException(404, "not visible to you")
    db.q_app(f"""UPDATE {VDR}.doc_extracts SET reviewed_by = :by, reviewed_at = current_timestamp(), corrected_value = :v
                 WHERE file_id = :f AND field = :field""",
             {"by": f"{c.email} as {c.role}", "v": b.get("corrected_value"), "f": file_id, "field": b["field"]})
    db.log_approval("extract", f"{file_id}|{b['field']}", "Corrected" if b.get("corrected_value") else "Confirmed",
                    b.get("corrected_value") or "", c.email, c.role)
    return {"ok": True}

@app.post("/api/dealroom/{inv}/drop")
def dealroom_drop(inv: str, request: Request):
    """The Stage 2 pack arrives in the deal-room landing zone (as a document-management export would); Auto Loader picks it up."""
    c = ctx(request); c.require("role-approver", "role-business-user")
    import io
    room = inv.replace(" ", "_"); w = db.sp(); n = 0
    for e in w.files.list_directory_contents(f"/Volumes/{C}/vdr/portal_uploads/_staged/{room}"):
        if e.name.endswith(".pdf") and not e.name.startswith(("Historical", "Valuation")):   # the GP uploads those two
            data = w.files.download(e.path).contents.read()
            w.files.upload(f"/Volumes/{C}/vdr/deal_rooms/{room}/B_Due_Diligence/{e.name}", io.BytesIO(data), overwrite=True); n += 1
    run = _run_job("hl-dealroom-ingest", {})
    db.log_approval("ingest", inv, "Stage 2 pack received", f"{n} files; ingest run {run}", c.email, c.role)
    return {"files": n, "run_id": run}

@app.get("/api/dealrooms")
def dealrooms(request: Request):
    """Deals the signed-in role can see (row filters decide), with file counts; Solace Grid's live stage from Lakebase."""
    c = ctx(request)
    files = {r["deal_room"]: r for r in c.q(f"""SELECT deal_room, count(*) AS files, sum(IF(status = 'Needs review', 1, 0)) AS needs_review,
                                                    max(received_at) AS last_file FROM {VDR}.file_register GROUP BY deal_room""")}
    live = {r["investment"]: r["stage"] for r in db.pg_q("SELECT investment, stage FROM hl_app.deal_stage")}
    rooms = set(r["investment"] for r in c.q(f"SELECT DISTINCT investment FROM {VDR}.checklist_items"))
    out = []
    for i in c.q(f"SELECT name, sector, portfolio, stage, status FROM {VDR}.investments ORDER BY stage, name"):
        f = files.get(i["name"], {})
        out.append({**i, "stage": live.get(i["name"], i["stage"]), "files": f.get("files", 0), "needs_review": f.get("needs_review", 0),
                    "last_file": f.get("last_file"), "has_room": i["name"] in rooms})
    return sorted(out, key=lambda r: (not r["has_room"], int(r["stage"]), r["name"]))

@app.get("/api/factors")
def factors(request: Request):
    """Market factor board — served from Lakebase (synced table serving.external_factors, kept in sync from Delta)."""
    ctx(request)
    try:
        rows = db.pg_q("""SELECT series, label, value, prev_value, unit, observed_at::text AS observed_at, source, tag
                          FROM serving.external_factors ORDER BY tag, series""")
        return [{**r, "served_from": "lakebase"} for r in rows]
    except Exception as e:                         # e.g. sync still provisioning: fall back to the Delta table
        print("lakebase factors:", e)
        return [{**r, "served_from": "delta"} for r in db.q_app(f"SELECT series, label, value, prev_value, unit, observed_at, source, tag FROM {VDR}.external_factors ORDER BY tag, series")]

FACTOR_MODEL = "databricks-gpt-oss-120b"       # open-weight model, served by Databricks
_NOTES: dict = {}

@app.get("/api/dealroom/{inv}/factor-note")
def factor_note(inv: str, request: Request, refresh: bool = False):
    """ai_query over today's external factors + the deal's extracted figures → one advisory risk paragraph."""
    c = ctx(request)
    key = (inv, c.role, dt.date.today().isoformat())
    if key in _NOTES and not refresh:
        return _NOTES[key]
    deal = c.q(f"SELECT name, sector, portfolio, stage FROM {VDR}.investments WHERE name = :inv", {"inv": inv})
    if not deal:
        raise HTTPException(404, "not visible to you")
    d = deal[0]
    fx = c.q(f"""SELECT label, value, prev_value, unit, observed_at, tag FROM {VDR}.external_factors
                 WHERE tag IN (:p, :s)""", {"p": f"portfolio:{d['portfolio']}", "s": f"sector:{d['sector']}"})
    figs = c.q(f"SELECT DISTINCT field, coalesce(corrected_value, value) AS value FROM {VDR}.doc_extracts WHERE deal_room = :inv AND field NOT LIKE 'ai\\\\_%' AND field <> 'company_name'",
               {"inv": inv})
    lines = "\n".join(f"- {x['label']}: {x['value']} {x['unit']} (previous {x['prev_value']}, as of {x['observed_at']})" for x in fx)
    facts = "; ".join(f"{x['field']} = {x['value']}" for x in figs) or "no key figures extracted yet"
    prompt = (f"You are a risk analyst at Harbourline Capital's Fund & Investment team. Deal: {d['name']} ({d['sector']}, {d['portfolio']}, "
              f"stage {d['stage']}). Extracted figures: {facts}.\nExternal factors (latest vs previous):\n{lines}\n\n"
              "Write ONE paragraph (max 110 words) for the deal team: the 2-3 risks these moves create for THIS deal (rates and "
              "financing cost, FX, energy prices, valuation multiples), naming the factor and its move, then one concrete diligence "
              "action. Plain text, no bullet points, no preamble. Advisory only — do not recommend approving or rejecting.")
    r = c.q("SELECT ai_query(:m, :p) AS note", {"m": FACTOR_MODEL, "p": prompt})
    _NOTES[key] = {"note": r[0]["note"], "model": FACTOR_MODEL, "factors": len(fx), "as_of": max((str(x["observed_at"]) for x in fx), default=None)}
    return _NOTES[key]

# ---------------- threads + portal ----------------
@app.get("/api/threads/{room}")
def threads(room: str, request: Request):
    c = ctx(request)
    if c.role == "role-external-gp" and room != "Solace Grid Energy":
        raise HTTPException(403, "not your deal room")
    return db.pg_q("SELECT body, run_by, run_as, at FROM hl_app.threads WHERE room = %s ORDER BY at", (room,))

@app.post("/api/threads/{room}")
async def thread_post(room: str, request: Request):
    c = ctx(request); b = await request.json()
    if c.role == "role-external-gp" and room != "Solace Grid Energy":
        raise HTTPException(403, "not your deal room")
    db.pg_q("INSERT INTO hl_app.threads(room, body, run_by, run_as) VALUES (%s,%s,%s,%s)", (room, b["body"][:4000], c.email, c.role))
    return threads(room, request)

@app.get("/api/portal")
def portal(request: Request):
    c = ctx(request)
    files = c.q(f"SELECT file_id, name, file_type, classification, status, received_at, uploaded_by FROM {VDR}.file_register WHERE deal_room = 'Solace Grid Energy' ORDER BY received_at")
    ups = db.pg_q("SELECT path, run_as, at FROM hl_app.uploads WHERE room = 'Solace Grid Energy' ORDER BY at")
    return {"files": files, "uploads": ups, "role": c.role}

@app.post("/api/portal/upload")
async def portal_upload(request: Request, file: UploadFile = File(...)):
    c = ctx(request)
    c.require("role-external-gp", "role-business-user")
    name = re.sub(r"[^A-Za-z0-9_.&-]", "_", file.filename or "upload.pdf")
    path = f"/Volumes/{C}/vdr/portal_uploads/Solace_Grid_Energy/{name}"
    data = await file.read()
    r = requests.put(f"{HOST}/api/2.0/fs/files{path}?overwrite=true", data=data,
                     headers={"Authorization": f"Bearer {c.token}", "Content-Type": "application/octet-stream"}, timeout=120)
    if r.status_code not in (200, 204):
        raise HTTPException(r.status_code, f"upload refused for {c.role}: {r.text[:200]}")
    db.pg_q("INSERT INTO hl_app.uploads(room, path, run_by, run_as) VALUES (%s,%s,%s,%s)", ("Solace Grid Energy", path, c.email, c.role))
    run = _run_job("hl-dealroom-ingest", {})
    return {"path": path, "ingest_run": run}

@app.post("/api/portal/stage-gp-files")
def portal_stage(request: Request):
    """Demo helper for the GP: upload the two staged Stage-2 documents (Valuation & Financials, Historical IC memos)."""
    c = ctx(request); c.require("role-external-gp")
    w = db.sp(); out = []
    for e in w.files.list_directory_contents(f"/Volumes/{C}/vdr/portal_uploads/_staged/Solace_Grid_Energy"):
        if e.name.startswith(("Historical", "Valuation")):
            data = w.files.download(e.path).contents.read()
            path = f"/Volumes/{C}/vdr/portal_uploads/Solace_Grid_Energy/{e.name}"
            r = requests.put(f"{HOST}/api/2.0/fs/files{path}?overwrite=true", data=data,
                             headers={"Authorization": f"Bearer {c.token}", "Content-Type": "application/octet-stream"}, timeout=120)
            if r.status_code in (200, 204):
                db.pg_q("INSERT INTO hl_app.uploads(room, path, run_by, run_as) VALUES (%s,%s,%s,%s)", ("Solace Grid Energy", path, c.email, c.role))
                out.append(e.name)
    run = _run_job("hl-dealroom-ingest", {})
    return {"uploaded": out, "ingest_run": run}

def mark_portal_uploads():
    """After ingest: stamp uploaded_by on portal files so the GP sees their own uploads (row filter rule)."""
    for u in db.pg_q("SELECT path, run_as FROM hl_app.uploads"):
        db.q_app(f"UPDATE {VDR}.file_register SET uploaded_by = :r WHERE path IN (:p, concat('dbfs:', :p)) AND uploaded_by IS NULL",
                 {"r": u["run_as"], "p": u["path"]})

@app.post("/api/portal/refresh")
def portal_refresh(request: Request):
    ctx(request); mark_portal_uploads(); return {"ok": True}

# ---------------- Stage 3 + marketplace widget ----------------
def _ai_parts(body: dict):
    """Agent-added datasets + layout items (names ai_w<id> / w_ai_w<id>)."""
    ds = [x for x in body["datasets"] if x["name"].startswith("ai_w")]
    items = [it for pg_ in body["pages"] for it in pg_["layout"] if it["widget"]["name"].startswith("w_ai_w")]
    return ds, items

def _strip_ai(did: str):
    """Remove agent-added widgets from a dashboard and republish (viewer credentials)."""
    from databricks.sdk.service.dashboards import Dashboard
    w = db.sp(); d = w.lakeview.get(did); body = json.loads(d.serialized_dashboard)
    body["datasets"] = [x for x in body["datasets"] if not x["name"].startswith("ai_w")]
    for pg_ in body["pages"]:
        pg_["layout"] = [it for it in pg_["layout"] if not it["widget"]["name"].startswith("w_ai_w")]
    w.lakeview.update(did, Dashboard(display_name=d.display_name, serialized_dashboard=json.dumps(body), warehouse_id=d.warehouse_id))
    w.lakeview.publish(did, warehouse_id=db.WAREHOUSE, embed_credentials=False)

@app.get("/api/stage3")
def stage3(request: Request):
    c = ctx(request); c.require("role-business-user", "role-approver", "role-it-ai-owner")
    return {"dashboard_embed": f"{HOST}/embed/dashboardsv3/{CFG['dashboards']['stage3']}",
            "proposals": db.pg_q("SELECT id, request, result, status, run_as, at FROM hl_app.widget_proposals ORDER BY id DESC LIMIT 10")}

def _role_catalog(c: Ctx) -> dict:
    cat = {}
    for v in ("stage3_kpis", "deal_room_completion"):
        try:
            d = json.loads(c.q(f"DESCRIBE TABLE EXTENDED {SEM}.{v} AS JSON")[0]["json_metadata"])
            mv = catalog_from_yaml(f"{SEM}.{v}", d["view_text"])
            cat[mv.name] = mv
        except Exception as e:
            print("catalog skip", v, e)
    return cat

def _widget_builder(body: dict) -> dict:
    """Widget Builder agent: request + the metric views this role can read -> a validated widget spec (LLM: open-weight FM API)."""
    from harbourline.ai.llm import make_chat
    from harbourline.ai.widget_spec import MetricView
    from harbourline.ai.widget_builder import build_widget
    ci = body.get("custom_inputs") or {}
    prompt = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prompts", "widget_builder.txt"), encoding="utf-8").read()
    catalog = {m["name"]: MetricView(m["name"], tuple(m["measures"]), tuple(m["dimensions"]), tuple(m["sources"])) for m in ci.get("catalog", [])}
    text = next(i["content"] for i in reversed(body["input"]) if i.get("role") == "user")
    out = build_widget(text, catalog, make_chat(CFG.get("llm_model", "databricks-gpt-oss-120b")),
                       {"agent": "widget_builder", "role": ci.get("role", ""), "portfolio": ci.get("portfolio", "")}, prompt)
    out["prompt_uri"] = "ai/prompts/widget_builder.txt"
    return out

@app.post("/api/stage3/propose")
async def stage3_propose(request: Request):
    c = ctx(request); b = await request.json()
    cat = _role_catalog(c)
    out = _widget_builder({"input": [{"role": "user", "content": b["request"]}],
                  "custom_inputs": {"catalog": [{"name": m.name, "measures": list(m.measures), "dimensions": list(m.dimensions),
                                                 "sources": list(m.sources)} for m in cat.values()],
                                    "role": c.role, "portfolio": "Fund I"}})
    pid = db.pg_q("INSERT INTO hl_app.widget_proposals(request, result, status, run_by, run_as) VALUES (%s,%s,%s,%s,%s) RETURNING id",
                  (b["request"], db.jdump(out), "proposed" if out.get("status") == "ok" else out.get("status"), c.email, c.role))[0]["id"]
    preview = None
    if out.get("status") == "ok":                 # same query the widget will run, as this role (row filters apply)
        s = out["spec"]
        try:
            preview = c.q(widget_sql(WidgetSpec(s["title"], s["metric"], s["source"], s["formula"], s["grain"], s["visual"], tuple(s["sources"]))) + " LIMIT 30")
        except Exception as e:
            preview = {"error": str(e)[:200]}
    return {"id": pid, **out, "preview": preview}

@app.post("/api/stage3/accept/{pid}")
def stage3_accept(pid: int, request: Request):
    """Accept a proposal: add the widget to the Executive View dashboard DRAFT (not published)."""
    c = ctx(request); c.require("role-business-user", "role-approver")
    p = db.pg_q("SELECT result FROM hl_app.widget_proposals WHERE id = %s", (pid,))
    if not p or p[0]["result"].get("status") != "ok":
        raise HTTPException(404, "no valid proposal")
    if db.pg_q("SELECT status FROM hl_app.widget_proposals WHERE id = %s", (pid,))[0]["status"] != "proposed":
        raise HTTPException(409, "already accepted")
    s = p[0]["result"]["spec"]
    spec = WidgetSpec(s["title"], s["metric"], s["source"], s["formula"], s["grain"], s["visual"], tuple(s["sources"]))
    w = db.sp(); did = CFG["dashboards"]["executive"]
    d = w.lakeview.get(did); body = json.loads(d.serialized_dashboard)
    page = body["pages"][0]
    y = max([it["position"]["y"] + it["position"]["height"] for it in page["layout"]] or [0])
    ds, item = to_lakeview_widget(spec, f"ai_w{pid}", 0, y)
    item["widget"]["spec"]["frame"]["description"] = f"Proposed by Widget Builder ({p[0]['result'].get('prompt_uri')}) for {c.role}"
    body["datasets"].append(ds); page["layout"].append(item)
    from databricks.sdk.service.dashboards import Dashboard
    w.lakeview.update(did, Dashboard(display_name=d.display_name, serialized_dashboard=json.dumps(body), warehouse_id=d.warehouse_id))
    w.lakeview.publish(did, warehouse_id=db.WAREHOUSE, embed_credentials=False)   # the preview is a published dashboard: owner + approver can open it
    db.pg_q("UPDATE hl_app.widget_proposals SET status = 'in preview' WHERE id = %s", (pid,))
    db.log_approval("widget", str(pid), "Accepted into preview (pending approval)", s["title"], c.email, c.role)
    return {"ok": True, "embed": f"{HOST}/embed/dashboardsv3/{did}"}

@app.post("/api/stage3/publish")
def stage3_publish(request: Request):
    """Approve the preview: copy the agent's widgets into the official Stage 3 dashboard and publish it."""
    c = ctx(request); c.require("role-approver")
    from databricks.sdk.service.dashboards import Dashboard
    w = db.sp()
    pv = json.loads(w.lakeview.get(CFG["dashboards"]["executive"]).serialized_dashboard)
    ds, items = _ai_parts(pv)
    if not items:
        raise HTTPException(409, "Nothing in the preview to approve")
    sid = CFG["dashboards"]["stage3"]; d = w.lakeview.get(sid); body = json.loads(d.serialized_dashboard)
    have = {x["name"] for x in body["datasets"]}
    page = body["pages"][0]
    y = max([it["position"]["y"] + it["position"]["height"] for it in page["layout"]] or [0]); x = 0; added = []
    for it in sorted(items, key=lambda i: (i["position"]["y"], i["position"]["x"])):
        dsn = it["widget"]["queries"][0]["query"]["datasetName"]
        if dsn in have:
            continue
        wd = it["position"]["width"]
        if x + wd > 6:
            x = 0; y += 5
        body["datasets"].append(next(z for z in ds if z["name"] == dsn))
        page["layout"].append({**it, "position": {**it["position"], "x": x, "y": y}}); x += wd; added.append(dsn)
    w.lakeview.update(sid, Dashboard(display_name=d.display_name, serialized_dashboard=json.dumps(body), warehouse_id=d.warehouse_id))
    w.lakeview.publish(sid, warehouse_id=db.WAREHOUSE, embed_credentials=False)
    db.pg_q("UPDATE hl_app.widget_proposals SET status = 'approved' WHERE status = 'in preview'")
    db.log_approval("executive_view", sid, "Approved preview → published to Stage 3 Monitoring", ", ".join(added), c.email, c.role)
    return {"ok": True, "added": added}

@app.get("/api/stage3/executive")
def stage3_exec(request: Request):
    ctx(request); return {"embed": f"{HOST}/embed/dashboardsv3/{CFG['dashboards']['executive']}"}

@app.post("/api/feedback")
async def feedback(request: Request):
    c = ctx(request); b = await request.json()
    db.pg_q("INSERT INTO hl_app.feedback(target, body, run_by, run_as) VALUES (%s,%s,%s,%s)", (b.get("target", "executive_view"), b["body"], c.email, c.role))
    db.log_approval("feedback", b.get("target", "executive_view"), "Instruction to controller", b["body"], c.email, c.role)
    return {"ok": True}

# ---------------- Audit & FinOps ----------------
@app.get("/api/audit")
def audit(request: Request):
    c = ctx(request); c.require("role-approver", "role-it-ai-owner")
    out = {"approvals": db.pg_q("SELECT scope, ref, decision, note, run_by, run_as, at FROM hl_app.approvals ORDER BY at DESC LIMIT 200")}
    return out

# ---------------- admin ----------------
@app.post("/api/admin/reset")
def admin_reset(request: Request):
    c = ctx(request)
    if c.is_role:
        raise HTTPException(403, "reset must be run as the presenter's own user, not a role")
    sqltext = open(os.path.join(os.path.dirname(__file__), "reset.sql")).read()
    with db.pg() as conn, conn.cursor() as cur:
        cur.execute(sqltext)
    db.q_app(f"DELETE FROM {VDR}.checklist_status WHERE investment = 'Solace Grid Energy'")
    for r in db.pg_q("SELECT investment, stage, item, status FROM hl_app.stage_items"):          # mirror the seed into Delta
        db.q_app(f"""INSERT INTO {VDR}.checklist_status VALUES (:i, 'Fund I', :s, :it, :st, NULL, current_date() + 3, 'seed', current_timestamp())""",
                 {"i": r["investment"], "s": r["stage"], "it": r["item"], "st": r["status"]})
    for did in (CFG["dashboards"]["executive"], CFG["dashboards"]["stage3"]):   # drop agent-added widgets (preview + official)
        _strip_ai(did)
    _run_job("hl-reset-data", {})
    return {"ok": True}

# ---------------- jobs ----------------
@lru_cache(maxsize=32)
def _job_id(suffix: str) -> int:
    for j in db.sp().jobs.list(name=None):
        name = (j.settings.name or "") if j.settings else ""
        if name == suffix or name.endswith("] " + suffix):
            return j.job_id
    raise HTTPException(500, f"job {suffix} not found / not shared with the app")

def _run_job(suffix: str, params: dict):
    return db.sp().jobs.run_now(job_id=_job_id(suffix), job_parameters=params or None).run_id

@app.get("/api/jobs/{run_id}")
def job_status(run_id: int, request: Request):
    c = ctx(request); c.require("role-business-user", "role-approver", "role-it-ai-owner", "role-external-gp")
    r = db.sp().jobs.get_run(run_id)
    done = r.state and r.state.result_state is not None
    if done and str(r.state.result_state).endswith("SUCCESS") and "dealroom" in (r.run_name or ""):
        try:
            mark_portal_uploads()
        except Exception as e:
            print("mark uploads:", e)
    return {"state": str(r.state.life_cycle_state), "result": str(r.state.result_state), "name": r.run_name,
            "message": r.state.state_message}

# ---------------- static ----------------
FRONT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=FRONT), name="static")

BUILD = str(int(time.time()))  # cache-buster: a new deploy forces browsers to fetch the new app.js / styles.css

@app.get("/")
def index():
    html = open(os.path.join(FRONT, "index.html"), encoding="utf-8").read()
    html = html.replace("/static/app.js", f"/static/app.js?v={BUILD}").replace("/static/styles.css", f"/static/styles.css?v={BUILD}")
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})
