from harbourline.ai.widget_spec import catalog_from_yaml, validate_spec, to_lakeview_widget, WidgetSpec

YAML = """
version: 1.1
source: harbourline.vdr.portfolio_kpis
dimensions:
  - name: Period
    expr: period
  - name: Portfolio
    expr: portfolio
measures:
  - name: Gross MOIC
    expr: MAX(CASE WHEN kpi = 'gross_moic' THEN value END)
  - name: Total Invested Capital
    expr: MAX(CASE WHEN kpi = 'total_invested_usd' THEN value END)
"""

def cat():
    mv = catalog_from_yaml("harbourline.semantic.stage3_kpis", YAML)
    return {mv.name: mv}

def ok_raw(**kw):
    d = {"title": "Gross MOIC by period", "metric": "Gross MOIC", "source": "harbourline.semantic.stage3_kpis",
         "formula": "Current value + realized ÷ invested", "grain": "Period", "visual": "bar"}
    d.update(kw); return d

def test_catalog_from_yaml():
    mv = cat()["harbourline.semantic.stage3_kpis"]
    assert mv.measures == ("Gross MOIC", "Total Invested Capital") and mv.dimensions == ("Period", "Portfolio")
    assert mv.sources == ("harbourline.vdr.portfolio_kpis",)

def test_valid_spec_fills_sources():
    spec, errs = validate_spec(ok_raw(), cat())
    assert errs == [] and spec.sources == ("harbourline.vdr.portfolio_kpis",)

def test_unknown_metric_source_visual_and_grain_are_errors():
    _, errs = validate_spec(ok_raw(metric="Net IRR %", visual="radar", grain="Sector"), cat())
    assert any("Net IRR %" in e for e in errs) and any("radar" in e for e in errs) and any("Sector" in e for e in errs)
    _, errs = validate_spec(ok_raw(source="harbourline.vdr.secret_view"), cat())
    assert any("secret_view" in e for e in errs)

def test_counter_needs_no_grain_but_charts_do():
    assert validate_spec(ok_raw(visual="counter", grain=""), cat())[1] == []
    assert validate_spec(ok_raw(visual="bar", grain=""), cat())[1] != []

def test_missing_fields_and_long_title():
    _, errs = validate_spec({"metric": "Gross MOIC"}, cat())
    assert any("title" in e for e in errs)
    assert validate_spec(ok_raw(title="x" * 81), cat())[1] != []

def test_to_lakeview_bar_and_counter():
    spec, _ = validate_spec(ok_raw(), cat())
    ds, item = to_lakeview_widget(spec, "ds_w1", 0, 0)
    assert len(ds["queryLines"]) == 1 and "MEASURE(`Gross MOIC`)" in ds["queryLines"][0] and "GROUP BY ALL" in ds["queryLines"][0]
    w = item["widget"]
    assert w["queries"][0]["name"] == "main_query" and w["spec"]["version"] == 3 and w["spec"]["widgetType"] == "bar"
    assert w["spec"]["encodings"]["x"]["fieldName"] == "Period" and w["spec"]["data"] == {"queryName": "main_query"}
    c, _ = validate_spec(ok_raw(visual="counter", grain=""), cat())
    _, citem = to_lakeview_widget(c, "ds_w2", 0, 5)
    assert citem["widget"]["spec"]["version"] == 2 and citem["position"] == {"x": 0, "y": 5, "width": 2, "height": 3}
