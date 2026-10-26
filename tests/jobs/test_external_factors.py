import importlib.util, pathlib
spec = importlib.util.spec_from_file_location("xf", pathlib.Path(__file__).resolve().parents[2] / "jobs/external_factors.py")
xf = importlib.util.module_from_spec(spec); spec.loader.exec_module(xf)

def test_latest_value_skips_missing():
    text = "observation_date,DGS10\n2026-10-08,4.11\n2026-10-09,4.15\n2026-10-10,.\n"
    assert xf.parse_fred_csv(text, "DGS10") == ("2026-10-09", 4.15, 4.11)   # latest + previous observation

def test_empty_returns_none():
    assert xf.parse_fred_csv("observation_date,DGS10\n", "DGS10") is None

def test_series_cover_minimum_set():
    assert {"DFF", "DGS2", "DGS10", "DEXHKUS", "DEXCHUS", "SP500", "VIXCLS"} <= set(xf.FRED_SERIES)
