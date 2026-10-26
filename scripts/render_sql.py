"""Render sql/*.sql with config names into build/sql/ for bundle sql_task files."""
import pathlib, importlib.util
from harbourline.config import load_names
spec = importlib.util.spec_from_file_location("run_sql", "scripts/run_sql.py"); rs = importlib.util.module_from_spec(spec); spec.loader.exec_module(rs)
n = load_names(); out = pathlib.Path("build/sql"); out.mkdir(parents=True, exist_ok=True)
for f in pathlib.Path("sql").glob("*.sql"):
    (out / f.name).write_text(rs.render(f.read_text(), n))
print("rendered", len(list(out.glob('*.sql'))))
