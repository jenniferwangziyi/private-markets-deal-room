"""Deal-room Genie agent (serialized_space v2) on certified metric views + governed tables."""
import hashlib, json, pathlib

def _id(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()           # stable 32-hex ids

LANG = ("Always answer in the same language as the question (English, 繁體中文 or 简体中文). "
        "End every answer with 'Source:' followed by the metric view or table you used. ")

def _space(tables, metric_views, instructions, samples, bench):
    sq = sorted(({"id": _id("s:" + q), "question": [q]} for q in samples), key=lambda x: x["id"])
    bq = sorted(({"id": _id("b:" + q), "question": [q], "answer": [{"format": "SQL", "content": [sql]}]} for q, sql in bench),
                key=lambda x: x["id"])
    return {"version": 2, "config": {"sample_questions": sq},
            "data_sources": {"tables": [{"identifier": t} for t in sorted(tables)],
                             "metric_views": [{"identifier": m} for m in sorted(metric_views)]},
            "instructions": {"text_instructions": [{"id": _id("i:" + instructions), "content": [LANG + instructions]}]},
            "benchmarks": {"questions": bq}}

def vdr_space(n) -> dict:
    s, v = n.semantic, n.vdr
    return _space(
        [f"{v}.investments", f"{v}.risks", f"{v}.reporting_calendar", f"{v}.alerts", f"{v}.external_factors", f"{s}.business_glossary"],
        [f"{s}.stage3_kpis", f"{s}.deal_room_completion"],
        "Use stage3_kpis for fund KPIs (latest period '2026-Q2'), deal_room_completion for deal-room completion and gaps. "
        "Completion % counts approved required items only and excludes waived / not applicable items. Amounts are USD. "
        "Use business_glossary for definitions (Total Invested Capital, MOIC, Gap, Risk Alert). "
        "For deal-room completion always filter to the stage the user names; if none is named, report each stage separately.",
        ["What is the total invested capital and gross MOIC this quarter?", "Fund I 的總投資額和總回報倍數是多少？",
         "Solace Grid Energy 各阶段的交易室完成率是多少？", "Which investments are below plan?"],
        [("What is the gross MOIC for 2026-Q2?", f"SELECT MEASURE(`Gross MOIC`) FROM {s}.stage3_kpis WHERE Period = '2026-Q2'"),
         ("How many reports are overdue?", f"SELECT count(*) FROM {v}.reporting_calendar WHERE status = 'Overdue'")])

def upsert(w, title: str, space: dict, warehouse_id: str, parent: str, existing: str | None) -> str:
    body = {"title": title, "warehouse_id": warehouse_id, "parent_path": parent, "serialized_space": json.dumps(space, ensure_ascii=False)}
    if existing:
        w.api_client.do("PATCH", f"/api/2.0/genie/spaces/{existing}", body=body); return existing
    return w.api_client.do("POST", "/api/2.0/genie/spaces", body=body)["space_id"]

if __name__ == "__main__":
    from databricks.sdk import WorkspaceClient
    from harbourline.config import load_names
    n = load_names(); w = WorkspaceClient(profile=n.profile); me = w.current_user.me().user_name
    assert "@" in me, "create Genie agents as your own user"
    cfg = pathlib.Path("config/genie.json"); ids = json.loads(cfg.read_text()) if cfg.exists() else {}
    parent = f"/Users/{me}/harbourline"
    ids["vdr"] = upsert(w, "Harbourline · Deal Room Analyst", vdr_space(n), n.warehouse_id, parent, ids.get("vdr"))
    cfg.write_text(json.dumps(ids, indent=2))
    for k, i in ids.items():
        print(k, i, f"{w.config.host}/embed/genie/rooms/{i}")
