import csv, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2] / "data"))
from gen_dealroom import generate

def rows(p): return list(csv.DictReader(open(p)))

def test_generate_matches_mockup(tmp_path):
    counts = generate(tmp_path)
    inv = rows(tmp_path / "investments.csv")
    assert [r["name"] for r in inv][:5] == ["Kestrel Robotics", "Lumen BioSciences", "Terrace Materials",
                                            "Meridian Freight", "Cobalt Data Systems"]
    assert any(r["name"] == "Solace Grid Energy" and r["stage"] == "1" for r in inv)
    k = {r["kpi"]: r["value"] for r in rows(tmp_path / "portfolio_kpis.csv") if r["period"] == "2026-Q2"}
    assert k["total_invested_usd"] == "2860000000" and k["gross_moic"] == "1.39"
    rep = rows(tmp_path / "reporting_calendar.csv")
    assert len(rep) == 28 and sum(r["status"] == "Overdue" for r in rep) == 4
    pdfs = list(tmp_path.rglob("*.pdf"))
    assert counts["pdfs"] == len(pdfs) >= 20
    assert any("Solace_Grid" in str(p) and "A_Pre-NDA" in str(p) for p in pdfs)
    scope = rows(tmp_path / "role_scope.csv")
    assert {"role-business-user", "role-approver", "role-external-gp"} <= {r["principal"] for r in scope}
