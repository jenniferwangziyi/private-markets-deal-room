"""Build the Stage 3 post-investment monitoring dashboard (6 KPI tiles + 8 widgets) and its preview copy from certified metric views."""
import json, pathlib

def _w(name, ds, kind, fields, enc, title, x, y, w, h):
    t = {"value": title, "fields": []} if kind == "table" else title
    v = {"counter": 2, "bar": 3, "line": 3, "table": 2, "pie": 3}[kind]
    return {"widget": {"name": name,
                       "queries": [{"name": "main_query", "query": {"datasetName": ds, "disaggregated": True,
                                    "fields": [{"name": f, "expression": f"`{f}`"} for f in fields]}}],
                       "spec": {"version": v, "widgetType": kind, "encodings": enc,
                                "frame": {"showTitle": True, "title": t}, "data": {"queryName": "main_query"}}},
            "position": {"x": x, "y": y, "width": w, "height": h}}

def _counter(name, ds, field, title, x, y):
    return _w(name, ds, "counter", [field], {"value": {"fieldName": field, "displayName": title}}, title, x, y, 1, 3)

def _table(name, ds, cols, title, x, y, w=3, h=6):
    return _w(name, ds, "table", cols, {"columns": [{"fieldName": c} for c in cols]}, title, x, y, w, h)

def _bar(name, ds, xf, yf, title, x, y, color=None, w=3, h=6):
    enc = {"x": {"fieldName": xf, "scale": {"type": "categorical"}, "displayName": xf},
           "y": {"fieldName": yf, "scale": {"type": "quantitative"}, "displayName": yf}}
    fields = [xf, yf]
    if color:
        enc["color"] = {"fieldName": color, "scale": {"type": "categorical"}, "displayName": color}; fields.append(color)
    return _w(name, ds, "bar", fields, enc, title, x, y, w, h)

def _filter(name, field, datasets, title, x, y, single=None, w=2, h=2):
    qs = [{"name": f"{name}_{d}", "query": {"datasetName": d, "disaggregated": False,
           "fields": [{"name": field, "expression": f"`{field}`"}]}} for d in datasets]
    spec = {"version": 2, "widgetType": "filter-single-select" if single else "filter-multi-select",
            "encodings": {"fields": [{"fieldName": field, "displayName": title, "queryName": q["name"]} for q in qs]},
            "frame": {"showTitle": True, "title": title}}
    if single:
        spec["selection"] = {"defaultSelection": {"values": {"dataType": "STRING", "values": [{"value": single}]}}}
    return {"widget": {"name": name, "queries": qs, "spec": spec}, "position": {"x": x, "y": y, "width": w, "height": h}}

def stage3_dashboard(n) -> dict:
    s, v = n.semantic, n.vdr
    ds = [
        {"name": "kpis", "displayName": "Stage 3 KPIs", "queryLines": [
            f"SELECT MEASURE(`Total Invested Capital`) / 1e9 AS `Total Invested (USD B)`, MEASURE(`Current Portfolio Value`) / 1e9 AS `Current Value (USD B)`, "
            f"MEASURE(`Gross MOIC`) AS `Gross MOIC`, MEASURE(`Net MOIC`) AS `Net MOIC`, MEASURE(`Realized Proceeds`) / 1e9 AS `Realized (USD B)`, "
            f"MEASURE(`Unrealized Value`) / 1e9 AS `Unrealized (USD B)`, Period, Portfolio FROM {s}.stage3_kpis GROUP BY Period, Portfolio"]},
        {"name": "perf", "displayName": "Performance summary", "queryLines": [
            f"SELECT metric AS Metric, actual_ltm_pct AS `Actual (LTM) %`, investment_case_pct AS `Investment Case %`, variance_pp AS `Variance (pp)` FROM {v}.performance_summary"]},
        {"name": "bridge", "displayName": "Value bridge", "queryLines": [
            f"SELECT step AS Step, usd_m AS `USD M` FROM {v}.value_bridge ORDER BY step_order"]},
        {"name": "alerts", "displayName": "Alerts", "queryLines": [
            f"SELECT alert AS Alert, count AS `Count`, detail AS Detail FROM {v}.alerts"]},
        {"name": "by_inv", "displayName": "Performance by investment", "queryLines": [
            f"SELECT name AS Investment, sector AS Sector, revenue_growth_pct AS `Revenue Growth %`, ebitda_margin_pct AS `EBITDA Margin %`, "
            f"moic_gross AS `MOIC (Gross)`, vs_plan_ebitda_pp AS `vs Plan (EBITDA pp)`, status AS Status, portfolio AS Portfolio FROM {v}.investments WHERE stage = 3"]},
        {"name": "income", "displayName": "Income statement", "queryLines": [
            f"SELECT line AS Line, 'Actual' AS Series, actual_usd_m AS `USD M` FROM {v}.income_statement UNION ALL "
            f"SELECT line, 'Plan', plan_usd_m FROM {v}.income_statement"]},
        {"name": "reporting", "displayName": "Reporting status", "queryLines": [
            f"SELECT status AS Status, count(*) AS Reports, portfolio AS Portfolio FROM {v}.reporting_calendar GROUP BY status, portfolio"]},
        {"name": "calendar", "displayName": "Upcoming reporting", "queryLines": [
            f"SELECT due_date AS `Due`, investment AS Investment, report AS Report, datediff(due_date, DATE'2026-07-15') AS `Due in (days)`, portfolio AS Portfolio "
            f"FROM {v}.reporting_calendar WHERE due_date >= DATE'2026-07-15' ORDER BY due_date LIMIT 5"]},
        {"name": "risks", "displayName": "Risk heat map", "queryLines": [
            f"SELECT investment AS Investment, inherent AS `Inherent Risk`, current AS `Current Risk`, trend AS Trend, driver AS `Top Risk Driver`, portfolio AS Portfolio FROM {v}.risks LIMIT 5"]},
        {"name": "updated", "displayName": "Last updated", "queryLines": [
            f"SELECT date_format(from_utc_timestamp(max(received_at), 'Asia/Hong_Kong'), 'yyyy-MM-dd HH:mm') AS `Last updated (HKT)` FROM {v}.file_register"]},
    ]
    k = ["Total Invested (USD B)", "Current Value (USD B)", "Gross MOIC", "Net MOIC", "Realized (USD B)", "Unrealized (USD B)"]
    layout = [_filter("f_portfolio", "Portfolio", ["kpis", "by_inv", "reporting", "calendar", "risks"], "Investment portfolio", 0, 0),
              _filter("f_period", "Period", ["kpis"], "Reporting period", 2, 0, single="2026-Q2"),
              _table("updated", "updated", ["Last updated (HKT)"], "Last updated · currency USD", 4, 0, 2, 2)]
    layout += [_counter(f"t{i}", "kpis", f, f, i, 2) for i, f in enumerate(k)]
    layout += [
        _table("perf", "perf", ["Metric", "Actual (LTM) %", "Investment Case %", "Variance (pp)"], "Portfolio Performance Summary", 0, 5, 2, 6),
        _bar("bridge", "bridge", "Step", "USD M", "Portfolio Value Bridge (USD M)", 2, 5, w=2),
        _table("alerts", "alerts", ["Alert", "Count", "Detail"], "Key Alerts & Exceptions", 4, 5, 2, 6),
        _table("by_inv", "by_inv", ["Investment", "Sector", "Revenue Growth %", "EBITDA Margin %", "MOIC (Gross)", "vs Plan (EBITDA pp)", "Status"],
               "Performance by Investment (LTM)", 0, 11, 2, 6),
        _bar("income", "income", "Line", "USD M", "Income Statement Snapshot (USD M)", 2, 11, color="Series", w=2),
        _w("reporting", "reporting", "pie", ["Status", "Reports"],
           {"angle": {"fieldName": "Reports", "scale": {"type": "quantitative"}, "displayName": "Reports"},
            "color": {"fieldName": "Status", "scale": {"type": "categorical"}, "displayName": "Status"}},
           "Reporting Status", 4, 11, 2, 6),
        _table("calendar", "calendar", ["Due", "Investment", "Report", "Due in (days)"], "Upcoming Reporting Calendar", 0, 17, 3, 5),
        _table("risks", "risks", ["Investment", "Inherent Risk", "Current Risk", "Trend", "Top Risk Driver"], "Top 5 Risk Heat Map", 3, 17, 3, 5),
    ]
    return {"datasets": ds, "pages": [{"name": "stage3", "displayName": "Post-Investment Monitoring", "layout": layout}]}

def publish(w, title: str, body: dict, warehouse_id: str, parent: str) -> str:
    from databricks.sdk.service.dashboards import Dashboard
    for d in w.lakeview.list():
        if d.display_name == title:
            w.lakeview.trash(d.dashboard_id)
    d = w.lakeview.create(Dashboard(display_name=title, warehouse_id=warehouse_id, parent_path=parent,
                                    serialized_dashboard=json.dumps(body)))
    w.lakeview.publish(d.dashboard_id, warehouse_id=warehouse_id, embed_credentials=False)
    return d.dashboard_id

if __name__ == "__main__":
    from databricks.sdk import WorkspaceClient
    from harbourline.config import load_names
    n = load_names(); w = WorkspaceClient(profile=n.profile); me = w.current_user.me().user_name
    assert "@" in me, "publish as your own user"
    parent = f"/Users/{me}/harbourline"; w.workspace.mkdirs(parent)
    ids = {"stage3": publish(w, "Harbourline · Post-Investment Monitoring", stage3_dashboard(n), n.warehouse_id, parent),
           # the preview dashboard: agent widgets land here first; the approver promotes them into stage3
           "executive": publish(w, "Harbourline · Executive View (preview)", stage3_dashboard(n), n.warehouse_id, parent)}
    pathlib.Path("config/dashboards.json").write_text(json.dumps(ids, indent=2))
    for k, i in ids.items():
        print(k, i, f"{w.config.host}/embed/dashboardsv3/{i}")
