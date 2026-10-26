"""Synthetic data for Harbourline Capital (fictional): Fund I/II portfolio monitoring tables + deal-room PDFs (Solace Grid Energy)."""
import csv, random
from datetime import date, timedelta
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

FUND1 = "Fund I"; FUND2 = "Fund II"
INVESTMENTS = [  # name, sector, rev_growth, ebitda_margin, moic, vs_plan_pp, status, stage, fund, classification
    ("Kestrel Robotics", "Tech", 17.4, 23.1, 1.57, 1.8, "green", 3, FUND1, "Confidential"),
    ("Lumen BioSciences", "Healthcare", -4.6, -11.2, 0.76, -9.3, "red", 3, FUND1, "Confidential"),
    ("Terrace Materials", "Industrials", 8.9, 18.7, 1.21, -0.6, "grey", 3, FUND1, "Confidential"),
    ("Meridian Freight", "Logistics", 15.2, 21.4, 1.44, 1.6, "green", 3, FUND1, "Confidential"),
    ("Cobalt Data Systems", "Tech", 21.1, 27.9, 1.83, 3.8, "green", 3, FUND1, "Confidential"),
    ("Pier Nine Retail REIT", "Real Estate", 3.8, 58.6, 1.12, 0.4, "green", 3, FUND2, "Confidential"),
    ("Solace Grid Energy", "Energy", 0.0, 0.0, 1.00, 0.0, "grey", 1, FUND1, "Confidential"),
]
KPIS = {"total_invested_usd": "2860000000", "current_value_usd": "3990000000", "gross_return_pct": "39.5",
        "gross_moic": "1.39", "gross_irr_pct": "18.6", "net_return_pct": "31.4", "net_moic": "1.31",
        "net_irr_pct": "15.1", "realized_usd": "1110000000", "unrealized_usd": "2880000000",
        "invested_vs_lq_pct": "2.4", "value_vs_lq_pct": "4.1"}
PHASES = {"A_Pre-NDA": ["Fund Overview - Pitch deck", "PPM - Key Terms Summary (Draft)", "Organization chart",
                        "IC overview", "High-level Track Record", "NDA"],
          "B_Due_Diligence": ["PPM", "LPA", "Subscription Agreement (Draft)", "Side letter template", "DDQ",
                              "Historical IC memos", "Valuation & Financials", "Portfolio asset-level diligence"],
          "C_Investor_Portal": ["Quarterly report Q2 2026", "Capital account statement", "Capital call notice",
                                "Distribution notice", "Financial statements FY2025", "Tax documents", "Investor communication"]}

def _w(path: Path, header, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(data)
    return len(data)

def _pdf(path: Path, title: str, lines):
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4); y = 800
    c.setFont("Helvetica-Bold", 16); c.drawString(60, y, title); y -= 30; c.setFont("Helvetica", 11)
    for ln in lines:
        c.drawString(60, y, ln); y -= 18
    c.save()

def generate(out_dir: Path) -> dict:
    random.seed(7); out_dir = Path(out_dir); counts = {}
    counts["investments"] = _w(out_dir / "investments.csv",
        ["name", "sector", "revenue_growth_pct", "ebitda_margin_pct", "moic_gross", "vs_plan_ebitda_pp", "status",
         "stage", "portfolio", "classification"], INVESTMENTS)
    counts["kpis"] = _w(out_dir / "portfolio_kpis.csv", ["period", "kpi", "value"], [("2026-Q2", k, v) for k, v in KPIS.items()])
    counts["perf"] = _w(out_dir / "performance_summary.csv", ["metric", "actual_ltm_pct", "investment_case_pct", "variance_pp"],
        [("Revenue Growth", 11.8, 10.0, 1.8), ("EBITDA Growth", 14.1, 12.0, 2.1), ("EBITDA Margin", 21.4, 20.0, 1.4),
         ("Net Income Margin", 11.9, 11.0, 0.9), ("ROIC", 17.6, 15.0, 2.6)])
    counts["bridge"] = _w(out_dir / "value_bridge.csv", ["step", "usd_m"],
        [("Opening Value (31 Mar 2026)", 3833), ("Performance", 164), ("Additions", 81), ("Distributions", -88),
         ("Closing Value (30 Jun 2026)", 3990)])
    counts["income"] = _w(out_dir / "income_statement.csv", ["line", "actual_usd_m", "plan_usd_m"],
        [("Revenue", 958, 905), ("EBITDA", 205, 186), ("Net Income", 114, 99)])
    statuses = ["On Time"] * 17 + ["Due Soon"] * 5 + ["Overdue"] * 4 + ["Not Yet Due"] * 2
    names = [i[0] for i in INVESTMENTS[:5]]
    cal = [(names[i % 5], f"Q2 2026 Report #{i + 1}", (date(2026, 7, 18) + timedelta(days=3 * i)).isoformat(), s, FUND1)
           for i, s in enumerate(statuses)]
    counts["calendar"] = _w(out_dir / "reporting_calendar.csv", ["investment", "report", "due_date", "status", "portfolio"], cal)
    counts["risks"] = _w(out_dir / "risks.csv", ["investment", "inherent", "current", "trend", "driver", "portfolio"],
        [("Lumen BioSciences", "High", "High", "flat", "Clinical trial delay", FUND1),
         ("Cobalt Data Systems", "High", "High", "up", "Data-protection regulation", FUND1),
         ("Kestrel Robotics", "Medium", "Medium", "down", "Customer concentration", FUND1),
         ("Terrace Materials", "Medium", "Low", "down", "Raw material volatility", FUND1),
         ("Meridian Freight", "Medium", "Medium", "flat", "Freight rate pressure", FUND1)])
    counts["alerts"] = _w(out_dir / "alerts.csv", ["alert", "count", "detail", "portfolio"],
        [("Investments Below Plan", 3, "Actual EBITDA < Plan by >10%", FUND1), ("Covenant Breaches", 2, "Require immediate attention", FUND1),
         ("Delayed Reports", 4, "Overdue reporting from GPs/Companies", FUND1), ("Material Risks Increased", 5, "Risk rating increased vs last quarter", FUND1),
         ("Upcoming Capital Calls", 2, "Total committed: USD 185M", FUND1)])
    chk = []
    for phase, docs in PHASES.items():
        stage = {"A_Pre-NDA": 1, "B_Due_Diligence": 2, "C_Investor_Portal": 3}[phase]
        for d in docs:
            req = "Conditional" if d in ("Side letter template", "Tax documents") else "Mandatory"
            chk.append(("Solace Grid Energy", stage, d, "document", req, "365" if d in ("NDA", "DDQ") else ""))
        chk.append(("Solace Grid Energy", stage, {1: "Head of Investment approval", 2: "Investment Committee approval",
                                               3: "Executive View review"}[stage], "approval", "Mandatory", ""))
    chk.append(("Solace Grid Energy", 2, "Finance / Legal approval", "approval", "Mandatory", ""))
    counts["checklist"] = _w(out_dir / "checklist_items.csv", ["investment", "stage", "item", "kind", "requirement", "validity_days"], chk)
    counts["scope"] = _w(out_dir / "role_scope.csv", ["principal", "scope_type", "scope_value"],
        [("role-business-user", "portfolio", FUND1),
         ("role-approver", "portfolio", "*"),
         ("role-it-ai-owner", "portfolio", "*"),
         ("role-external-gp", "deal_room", "Solace Grid Energy")])
    n = 0
    for name in ("Solace Grid Energy", "Kestrel Robotics"):
        for phase, docs in PHASES.items():
            if name == "Solace Grid Energy" and phase != "A_Pre-NDA":
                continue                       # Solace Grid starts at Stage 1: only pitch documents exist
            for d in docs:
                lines = [f"Investment: {name}", f"Document type: {d}", "Classification: Confidential",
                         "Prepared for Harbourline Capital Investments — synthetic demo document"]
                if d == "Valuation & Financials":
                    lines += ["Pre-money valuation: USD 48.0M", "FY2025 revenue: USD 6.1M", "FY2025 EBITDA: USD 0.9M"]
                if d == "Historical IC memos":
                    lines += ["FY2025 revenue (per management): USD 5.4M"]          # deliberate mismatch for the risk alert
                _pdf(out_dir / "deal_rooms" / name.replace(" ", "_") / phase / f"{d.replace('/', '-').replace(' ', '_')}.pdf", d, lines)
                n += 1
    # Stage 2 files Solace Grid will receive during the demo (dropped live / uploaded by the GP)
    for d in PHASES["B_Due_Diligence"]:
        lines = [f"Investment: Solace Grid Energy", f"Document type: {d}", "Classification: Confidential"]
        if d == "Valuation & Financials":
            lines += ["Pre-money valuation: USD 48.0M", "FY2025 revenue: USD 6.1M", "FY2025 EBITDA: USD 0.9M"]
        if d == "Historical IC memos":
            lines += ["FY2025 revenue (per management): USD 5.4M"]
        _pdf(out_dir / "staged_uploads" / "Solace_Grid_Energy" / f"{d.replace(' ', '_').replace('&', 'and')}.pdf", d, lines); n += 1
    counts["pdfs"] = n
    return counts

if __name__ == "__main__":
    import sys; print(generate(Path(sys.argv[1])))
