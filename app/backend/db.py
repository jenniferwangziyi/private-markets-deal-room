"""Data access: governed reads as the caller (OBO token -> SQL warehouse), app-owned writes (app SP), Lakebase app state."""
import json, os, threading, time
from contextlib import contextmanager
from databricks import sql as dbsql
from databricks.sdk import WorkspaceClient

HOST = os.environ.get("DATABRICKS_HOST", "").replace("https://", "")
WAREHOUSE = os.environ["WAREHOUSE_ID"]
CATALOG = os.environ.get("HL_CATALOG", "harbourline")
PG_ENDPOINT = os.environ.get("LAKEBASE_ENDPOINT", "projects/harbourline/branches/production/endpoints/primary")
PG_SCHEMA = "hl_app"

_sp = None
def sp() -> WorkspaceClient:
    """App service principal client — only for app-owned operations (state, jobs, audit writes)."""
    global _sp
    if _sp is None:
        _sp = WorkspaceClient()
    return _sp

def _rows(cur):
    cols = [c[0] for c in cur.description] if cur.description else []
    return [dict(zip(cols, r)) for r in cur.fetchall()] if cols else []

def q_user(token: str, query: str, params: dict | None = None) -> list:
    """Run SQL as the signed-in identity (assumed role) — Unity Catalog row filters apply."""
    with dbsql.connect(server_hostname=HOST, http_path=f"/sql/1.0/warehouses/{WAREHOUSE}", access_token=token) as c:
        with c.cursor() as cur:
            cur.execute(query, params or {})
            return _rows(cur)

def q_app(query: str, params: dict | None = None) -> list:
    """Run SQL as the app SP — only for audited write-backs (status, reviews) with run_by / run_as recorded."""
    w = sp()
    token = w.config.authenticate()["Authorization"].split(" ", 1)[1]
    with dbsql.connect(server_hostname=HOST, http_path=f"/sql/1.0/warehouses/{WAREHOUSE}", access_token=token) as c:
        with c.cursor() as cur:
            cur.execute(query, params or {})
            return _rows(cur)

# ---------------- Lakebase (app state) ----------------
_pg_lock = threading.Lock()
_pg_cred = {"token": None, "exp": 0}

def _pg_password():
    with _pg_lock:
        if time.time() > _pg_cred["exp"] - 300:
            cred = sp().postgres.generate_database_credential(endpoint=PG_ENDPOINT)
            _pg_cred.update(token=cred.token, exp=time.time() + 3000)
        return _pg_cred["token"]

@contextmanager
def pg():
    import psycopg
    conn = psycopg.connect(host=os.environ["PGHOST"], port=int(os.environ.get("PGPORT", 5432)),
                           dbname=os.environ.get("PGDATABASE", "databricks_postgres"),
                           user=os.environ.get("PGUSER") or os.environ["DATABRICKS_CLIENT_ID"],
                           password=_pg_password(), sslmode="require", autocommit=True)
    try:
        yield conn
    finally:
        conn.close()

def pg_q(query: str, params: tuple = ()) -> list:
    with pg() as c, c.cursor() as cur:
        cur.execute(query, params)
        if cur.description:
            cols = [d.name for d in cur.description]
            return [dict(zip(cols, r)) for r in cur.fetchall()]
        return []

def init_schema():
    ddl = open(os.path.join(os.path.dirname(__file__), "schema.sql")).read()
    with pg() as c, c.cursor() as cur:
        cur.execute(ddl)

def log_approval(scope: str, ref: str, decision: str, note: str, run_by: str, run_as: str):
    pg_q("INSERT INTO hl_app.approvals(scope, ref, decision, note, run_by, run_as) VALUES (%s,%s,%s,%s,%s,%s)",
         (scope, ref, decision, note, run_by, run_as))

def jdump(x):
    return json.dumps(x, default=str, ensure_ascii=False)
