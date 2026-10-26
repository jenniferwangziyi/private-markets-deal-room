"""Run a SQL file against the demo warehouse via the Statement Execution API (databricks CLI auth)."""
import argparse, json, re, subprocess, sys, time
from harbourline.config import load_names

def render(text, n):
    for k in ("vdr", "semantic", "governance", "ai"):
        text = text.replace("${" + k + "}", getattr(n, k))
    text = text.replace("${app_sp}", n.app_sp)
    text = text.replace("${sharepoint_url}", n.sharepoint.get("url", "")).replace("${sharepoint_connection}", n.sharepoint.get("connection", ""))
    text = text.replace("${vdr_leaf}", f"{n.prefix}vdr").replace("${prefix}", n.prefix)
    return text.replace("${catalog}", n.catalog)

def split_statements(text):
    body = "\n".join(l for l in text.splitlines() if not l.strip().startswith("--"))
    parts = re.split(r";\s*\n", body)
    return [p.strip().rstrip(";") for p in parts if p.strip()]

def execute(stmt, n, profile):
    payload = json.dumps({"statement": stmt, "warehouse_id": n.warehouse_id, "wait_timeout": "50s"})
    out = subprocess.run(["databricks", "api", "post", "/api/2.0/sql/statements", "--profile", profile, "--json", payload],
                         capture_output=True, text=True)
    res = json.loads(out.stdout or "{}")
    while res.get("status", {}).get("state") in ("PENDING", "RUNNING"):
        time.sleep(3)
        res = json.loads(subprocess.run(["databricks", "api", "get", f"/api/2.0/sql/statements/{res['statement_id']}",
                                         "--profile", profile], capture_output=True, text=True).stdout)
    return res

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("file"); ap.add_argument("--profile")
    a = ap.parse_args(); n = load_names()
    for stmt in split_statements(render(open(a.file).read(), n)):
        res = execute(stmt, n, a.profile or n.profile)
        state = res.get("status", {}).get("state")
        print(f"[{state}] {stmt.splitlines()[0][:100]}")
        if state != "SUCCEEDED":
            print(json.dumps(res.get("status"), indent=2)); sys.exit(1)
        rows = res.get("result", {}).get("data_array")
        if rows:
            for r in rows[:20]: print("   ", r)

if __name__ == "__main__":
    main()
