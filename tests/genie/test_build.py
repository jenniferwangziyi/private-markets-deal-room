import importlib.util, pathlib, re
spec = importlib.util.spec_from_file_location("genie", pathlib.Path(__file__).resolve().parents[2] / "ai/genie/build.py")
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
from harbourline.config import Names
N = Names("harbourline", "", "w", "hunter")

def check(s):
    assert s["version"] == 2
    ids = [q["id"] for q in s["config"]["sample_questions"]] + [q["id"] for q in s["benchmarks"]["questions"]]
    assert all(re.fullmatch(r"[0-9a-f]{32}", i) for i in ids) and len(ids) == len(set(ids))
    for key in ("tables", "metric_views"):
        idents = [t["identifier"] for t in s["data_sources"].get(key, [])]
        assert idents == sorted(idents)
    assert [q["id"] for q in s["config"]["sample_questions"]] == sorted(q["id"] for q in s["config"]["sample_questions"])
    assert len(s["instructions"]["text_instructions"]) == 1
    text = " ".join(s["instructions"]["text_instructions"][0]["content"])
    assert "same language" in text and "source" in text.lower()

def test_vdr_space():
    s = g.vdr_space(N); check(s)
    mv = [t["identifier"] for t in s["data_sources"]["metric_views"]]
    assert "harbourline.semantic.stage3_kpis" in mv and "harbourline.semantic.deal_room_completion" in mv
    qs = " ".join(q["question"][0] for q in s["config"]["sample_questions"])
    assert re.search(r"[一-鿿]", qs)                     # includes a Chinese sample question

