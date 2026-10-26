"""Run a SQL query on the warehouse and print the result as a Markdown table (used to capture execution evidence).
Usage: python scripts/query.py "SELECT ..." [--profile hunter-business]"""
import argparse, json, subprocess, sys, time
from harbourline.config import load_names

def run(sql: str, profile: str, warehouse_id: str) -> dict:
    body = json.dumps({"warehouse_id": warehouse_id, "statement": sql, "wait_timeout": "50s", "format": "JSON_ARRAY", "disposition": "INLINE"})
    r = json.loads(subprocess.check_output(["databricks", "api", "post", "/api/2.0/sql/statements", "--profile", profile, "--json", body]))
    while r["status"]["state"] in ("PENDING", "RUNNING"):
        time.sleep(2)
        r = json.loads(subprocess.check_output(["databricks", "api", "get", f"/api/2.0/sql/statements/{r['statement_id']}", "--profile", profile]))
    return r

def to_markdown(r: dict, width: int = 1500) -> str:
    if r["status"]["state"] != "SUCCEEDED":
        return f"**{r['status']['state']}**: {r['status'].get('error', {}).get('message', '')[:400]}"
    cols = [c["name"] for c in r["manifest"]["schema"]["columns"]]
    rows = r.get("result", {}).get("data_array") or []
    cell = lambda v: ("NULL" if v is None else str(v)).replace("|", "\\|").replace("\n", " ")[:width]
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(cell(v) for v in row) + " |" for row in rows]
    return "\n".join(out) + f"\n\n_{len(rows)} row(s)_"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("sql"); ap.add_argument("--profile")
    a = ap.parse_args(); n = load_names()
    print(to_markdown(run(a.sql, a.profile or n.profile, n.warehouse_id)))
