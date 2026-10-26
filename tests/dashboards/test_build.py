import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("dash", pathlib.Path(__file__).resolve().parents[2] / "ai/dashboards/build.py")
dash = importlib.util.module_from_spec(spec); spec.loader.exec_module(dash)
from harbourline.config import Names

N = Names("harbourline", "", "w", "hunter")
VERSIONS = {"counter": 2, "bar": 3, "line": 3, "table": 2, "pie": 3, "filter-single-select": 2, "filter-multi-select": 2}

def widgets(d):
    return [it for p in d["pages"] for it in p["layout"]]

def check_rules(d):
    names = {ds["name"] for ds in d["datasets"]}
    for ds in d["datasets"]:
        assert isinstance(ds["queryLines"], list) and len(ds["queryLines"]) == 1
    cells = set()
    for it in widgets(d):
        w, pos = it["widget"], it["position"]
        assert w["spec"]["version"] == VERSIONS[w["spec"]["widgetType"]]
        for q in w["queries"]:
            assert q["query"]["datasetName"] in names
        if not w["spec"]["widgetType"].startswith("filter"):
            assert w["queries"][0]["name"] == "main_query" and w["spec"]["data"] == {"queryName": "main_query"}
        assert 0 <= pos["x"] and pos["x"] + pos["width"] <= 6
        for x in range(pos["x"], pos["x"] + pos["width"]):
            for y in range(pos["y"], pos["y"] + pos["height"]):
                assert (x, y) not in cells, f"overlap at {(x, y)}"
                cells.add((x, y))

def test_stage3_matches_mockup():
    d = dash.stage3_dashboard(N); check_rules(d)
    types = [it["widget"]["spec"]["widgetType"] for it in widgets(d) if it["widget"]["name"] != "updated"]  # + last-updated tile
    assert types.count("counter") == 6 and sum(t not in ("counter",) and not t.startswith("filter") for t in types) == 8
    titles = " ".join(str(it["widget"]["spec"]["frame"]["title"]) for it in widgets(d))
    for t in ("Portfolio Performance Summary", "Portfolio Value Bridge", "Key Alerts", "Performance by Investment",
              "Income Statement", "Reporting Status", "Upcoming Reporting Calendar", "Top 5 Risk"):
        assert t in titles
    assert all("harbourline." in ds["queryLines"][0] for ds in d["datasets"])

