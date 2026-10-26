import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("run_sql", pathlib.Path(__file__).resolve().parents[1] / "scripts/run_sql.py")
run_sql = importlib.util.module_from_spec(spec); spec.loader.exec_module(run_sql)
from harbourline.config import Names

def test_render_and_split():
    n = Names("harbourline", "", "w", "hunter")
    text = "CREATE SCHEMA ${vdr};\n-- comment\nCREATE TABLE ${semantic}.t (a STRING);\n"
    stmts = run_sql.split_statements(run_sql.render(text, n))
    assert stmts == ["CREATE SCHEMA harbourline.vdr", "CREATE TABLE harbourline.semantic.t (a STRING)"]

def test_split_keeps_function_bodies():
    text = "CREATE FUNCTION f(x STRING) RETURNS BOOLEAN RETURN x = 'a;b';\nSELECT 1;\n"
    assert len(run_sql.split_statements(text)) == 2

def test_render_vdr_leaf():
    assert run_sql.render("/Volumes/${catalog}/${vdr_leaf}/x", Names("jennifer_wang", "hl_", "w", "h")) == "/Volumes/jennifer_wang/hl_vdr/x"

def test_render_ai_schema():
    assert run_sql.render("${ai}.x", Names("harbourline", "", "w", "h")) == "harbourline.ai.x"
