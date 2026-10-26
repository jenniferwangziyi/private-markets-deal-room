"""Collect execution evidence as TEXT into evidence/*.md: real query results, AI/agent outputs, Lakebase reads, Genie transcripts.
Run after the build:  uv run --extra ai python scripts/collect_evidence.py [section ...]
Sections: lakeflow governance lakebase genai genie app   (default: all). Role sections need the hunter-<role> profiles."""
import datetime as dt, json, pathlib, subprocess, sys, time
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from query import run, to_markdown
from harbourline.config import load_names

N = load_names(); OUT = pathlib.Path("evidence"); OUT.mkdir(exist_ok=True)
ROLES = {"role-business-user": "hunter-business", "role-approver": "hunter-approver", "role-external-gp": "hunter-gp"}

def q(sql, profile=None):
    return to_markdown(run(sql, profile or N.profile, N.warehouse_id))

def write(name, title, parts):
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = [f"# {title}", f"_Captured {stamp} from workspace `{N.profile}` (catalog `{N.catalog}`) by `scripts/collect_evidence.py`._", ""]
    for h, content in parts:
        body += [f"## {h}", "", content, ""]
    (OUT / name).write_text("\n".join(body)); print("wrote", OUT / name)

def fence(sql):
    return "```sql\n" + sql.strip() + "\n```"

def lakeflow():
    jobs = json.loads(subprocess.check_output(["databricks", "jobs", "list", "--profile", N.profile, "-o", "json"]))
    rows = ["| job | last run | state | result | duration (s) |", "|---|---|---|---|---|"]
    for j in jobs:
        name = j["settings"]["name"]
        if "hl-" not in name:
            continue
        runs = json.loads(subprocess.check_output(["databricks", "jobs", "list-runs", "--job-id", str(j["job_id"]), "--limit", "1",
                                                   "--profile", N.profile, "-o", "json"]))
        for r in runs:
            st = r["state"]; dur = (r.get("end_time", 0) - r["start_time"]) / 1000 if r.get("end_time") else None
            rows.append(f"| {name} | {r['run_id']} | {st.get('life_cycle_state')} | {st.get('result_state')} | {dur and round(dur)} |")
    write("01_lakeflow_ingest.md", "Lakeflow — ingest raw (synthetic) data", [
        ("Job runs (Lakeflow Jobs)", "\n".join(rows)),
        ("Raw files landed in the Unity Catalog volume and registered by Auto Loader", q(
            f"SELECT deal_room, stage, source, status, count(*) AS files FROM {N.vdr}.file_register GROUP BY ALL ORDER BY 1, 2, 4")),
        ("Row counts of every table built from the raw data", q(" UNION ALL ".join(
            f"SELECT '{t}' AS table_name, count(*) AS rows FROM {N.vdr}.{t}" for t in
            ("investments", "portfolio_kpis", "checklist_items", "reporting_calendar", "risks", "alerts", "external_factors",
             "file_register", "file_content", "doc_parsed", "doc_extracts")))),
        ("External investment factors (daily Lakeflow job: public FRED feed + seed series)", q(
            f"SELECT series, label, value, prev_value, unit, observed_at, source FROM {N.vdr}.external_factors ORDER BY tag, series")),
    ])

def governance():
    parts = [("Access is defined once: role scopes (governance.role_scope)", q(f"SELECT * FROM {N.governance}.role_scope ORDER BY principal")),
             ("Row-filter function", fence(f"DESCRIBE FUNCTION EXTENDED {N.governance}.scope_match") + "\n\n" +
              q(f"DESCRIBE FUNCTION EXTENDED {N.governance}.scope_match")),
             ("Tag-based ABAC policy on the vdr schema + file row filter", q(
                 f"SELECT table_name, column_name, tag_name FROM {N.catalog}.information_schema.column_tags WHERE schema_name = 'vdr' ORDER BY 1, 2"))]
    contrast = f"""SELECT current_user() AS identity,
  (SELECT count(*) FROM {N.vdr}.investments) AS companies_visible,
  (SELECT count(DISTINCT portfolio) FROM {N.vdr}.investments) AS portfolios_visible,
  (SELECT count(*) FROM {N.vdr}.file_register WHERE deal_room = 'Solace Grid Energy') AS solace_grid_files_visible,
  (SELECT round(max(value) / 1e9, 2) FROM {N.vdr}.portfolio_kpis WHERE kpi = 'total_invested_usd' AND period = '2026-Q2') AS total_invested_usd_bn"""
    parts.append(("The same query, run as each role (row filters applied by Unity Catalog, no app code)", fence(contrast)))
    for role, prof in ROLES.items():
        parts.append((f"as {role}", q(contrast, prof)))
    write("02_unity_catalog_governance.md", "Unity Catalog — govern it", parts)

def lakebase():
    st = json.loads(subprocess.check_output(["databricks", "postgres", "get-synced-table", "synced_tables/harbourline_serving.serving.external_factors",
                                             "--profile", N.profile, "-o", "json"]))
    from databricks.sdk import WorkspaceClient
    import psycopg
    w = WorkspaceClient(profile=N.profile); ep = "projects/harbourline/branches/production/endpoints/primary"
    conn = psycopg.connect(host=w.postgres.get_endpoint(name=ep).status.hosts.host, port=5432, dbname="databricks_postgres",
                           user=w.current_user.me().user_name, password=w.postgres.generate_database_credential(endpoint=ep).token, sslmode="require")
    def pg(sql):
        with conn.cursor() as c:
            t0 = time.time(); c.execute(sql); rows = c.fetchall(); ms = (time.time() - t0) * 1000; cols = [d.name for d in c.description]
        out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)] + ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
        return "\n".join(out) + f"\n\n_{len(rows)} row(s), {ms:.0f} ms from Postgres_"
    write("03_lakebase_serving.md", "Lakebase — operational serving", [
        ("Synced table Delta → Lakebase (status)", "```json\n" + json.dumps({k: st.get(k) for k in ("name", "synced_table_id", "status", "spec")}, indent=2, default=str)[:3000] + "\n```"),
        ("The app's market-factor board reads Lakebase (serving.external_factors)", pg(
            "SELECT series, label, value, prev_value, unit, observed_at FROM serving.external_factors ORDER BY series")),
        ("App operational state in Lakebase (schema hl_app, owned by the app's service principal)", pg(
            "SELECT 'deal_stage' t, count(*) FROM hl_app.deal_stage UNION ALL SELECT 'stage_items', count(*) FROM hl_app.stage_items "
            "UNION ALL SELECT 'approvals', count(*) FROM hl_app.approvals UNION ALL SELECT 'widget_proposals', count(*) FROM hl_app.widget_proposals "
            "UNION ALL SELECT 'threads', count(*) FROM hl_app.threads")),
        ("Deal-room gate state served to the app", pg("SELECT investment, stage, item, status, run_as FROM hl_app.stage_items ORDER BY stage, item")),
    ])

def genai():
    from harbourline.ai.llm import make_chat
    from harbourline.ai.widget_spec import MetricView, WidgetSpec, widget_sql
    from harbourline.ai.widget_builder import build_widget
    cat = {f"{N.semantic}.stage3_kpis": MetricView(f"{N.semantic}.stage3_kpis", ("Total Invested Capital", "Current Portfolio Value", "Gross MOIC",
           "Net MOIC", "Gross IRR %", "Net IRR %", "Realized Proceeds", "Unrealized Value"), ("Period", "Portfolio"), (f"{N.vdr}.portfolio_kpis",))}
    prompt = pathlib.Path("ai/prompts/widget_builder.txt").read_text(); chat = make_chat(N.ai_cfg["llm_model"])
    agent = []
    for req in ("Show gross MOIC by period as a bar chart", "Total invested capital for Fund I as a KPI tile", "Hotel RevPAR by property"):
        t0 = time.time(); out = build_widget(req, cat, chat, {"agent": "widget_builder", "role": "evidence"}, prompt); sec = time.time() - t0
        block = f"**Request:** {req}  \n**Latency:** {sec:.1f} s\n\n```json\n{json.dumps(out, indent=2, ensure_ascii=False)}\n```"
        if out.get("status") == "ok":
            s = out["spec"]; sql = widget_sql(WidgetSpec(s["title"], s["metric"], s["source"], s["formula"], s["grain"], s["visual"], tuple(s["sources"])))
            block += "\n\nPreview query the widget will run (as the viewer):\n\n" + fence(sql) + "\n\n" + q(sql)
        agent.append(block)
    write("04_genai_intelligence.md", "ML / GenAI — make it intelligent", [
        ("AI Functions on every raw document: ai_parse_document → ai_classify (type + classification, with confidence) → ai_extract",
         fence(pathlib.Path("sql/35_ai_extract.sql").read_text()[:1800] + "\n-- (truncated; full file in sql/35_ai_extract.sql)")),
        ("ai_classify / ai_extract output (real model output, stored in vdr.doc_extracts)", q(
            f"SELECT f.deal_room, f.name, e.field, e.value, round(e.confidence, 2) AS confidence, f.status AS routed_to FROM {N.vdr}.doc_extracts e "
            f"JOIN {N.vdr}.file_register f USING (file_id) WHERE f.deal_room = 'Solace Grid Energy' OR f.name LIKE 'Valuation%' OR f.name LIKE 'Historical%' ORDER BY 1, 2, 3")),
        ("Cross-document check: figure mismatch raised from the AI extraction", q(f"SELECT * FROM {N.vdr}.risk_alerts ORDER BY investment")),
        ("ai_query — market-risk note for a deal (open-weight model)", q(
            "SELECT ai_query('" + N.ai_cfg["llm_model"] + "', 'You are a risk analyst at a private-markets investor. Deal: Solace Grid Energy (Energy, Fund I, stage 1). "
            "External factors (latest vs previous): Brent crude 115.2 (prev 118.8) USD/bbl; 3M HIBOR 3.85% (prev 3.92%); USD/CNY 6.686 (prev 6.691); "
            "US 10Y 4.96% (prev 5.13%). In ONE paragraph (max 90 words) name the 2-3 risks for this deal and one diligence action. Advisory only.') AS risk_note")),
        ("Widget Builder agent (LLM → validated widget spec on certified metrics only)", "\n\n---\n\n".join(agent)),
    ])

def genie():
    from databricks.sdk import WorkspaceClient
    space = json.loads(pathlib.Path("config/genie.json").read_text())["vdr"]
    def ask(profile, question):
        w = WorkspaceClient(profile=profile)
        m = w.api_client.do("POST", f"/api/2.0/genie/spaces/{space}/start-conversation", body={"content": question})
        for _ in range(60):
            r = w.api_client.do("GET", f"/api/2.0/genie/spaces/{space}/conversations/{m['conversation_id']}/messages/{m['message_id']}")
            if r.get("status") in ("COMPLETED", "FAILED", "CANCELLED"):
                break
            time.sleep(3)
        out = [f"**Q ({profile}):** {question}", f"**Status:** {r.get('status')}"]
        for a in r.get("attachments") or []:
            if a.get("query"):
                out.append(fence(a["query"]["query"]))
                try:
                    res = w.api_client.do("GET", f"/api/2.0/genie/spaces/{space}/conversations/{m['conversation_id']}/messages/{m['message_id']}"
                                                 f"/attachments/{a['attachment_id']}/query-result")
                    out.append("**Rows:** `" + json.dumps(res["statement_response"]["result"].get("data_array"))[:600] + "`")
                except Exception as e:
                    out.append(f"rows: n/a ({str(e)[:80]})")
            if a.get("text"):
                out.append("**Answer:** " + a["text"]["content"])
        return "\n\n".join(out)
    parts = []
    for prof, qs in (("hunter-business", ["How many companies do I have access to?", "How did gross MOIC change from 2026-Q1 to 2026-Q2?",
                                          "Fund I 的總投資額是多少？", "How is Total Invested Capital defined?"]),
                     ("hunter-approver", ["How many companies do I have access to?"])):
        for question in qs:
            parts.append((f"{prof}: {question}", ask(prof, question)))
    write("05_genie_agent.md", "Genie Agent — natural-language access (as each role)", parts)

def app():
    a = json.loads(subprocess.check_output(["databricks", "apps", "get", "harbourline-dealroom", "--profile", N.profile, "-o", "json"]))
    keep = {k: a.get(k) for k in ("name", "url", "app_status", "compute_status", "active_deployment", "resources", "user_api_scopes")}
    tests = subprocess.run(["uv", "run", "--extra", "dev", "pytest", "-q"], capture_output=True, text=True).stdout
    write("06_databricks_app.md", "Databricks App — surface it to the business", [
        ("Deployed app (status from the Apps API)", "```json\n" + json.dumps(keep, indent=2)[:4000] + "\n```"),
        ("Unit tests (gate logic, widget spec validation, LLM client, ingest path parsing, data generator)", "```\n" + tests[-2000:] + "\n```"),
    ])

if __name__ == "__main__":
    want = sys.argv[1:] or ["lakeflow", "governance", "lakebase", "genai", "genie", "app"]
    for s in want:
        try:
            globals()[s]()
        except Exception as e:
            print(f"section {s} failed: {e}")
