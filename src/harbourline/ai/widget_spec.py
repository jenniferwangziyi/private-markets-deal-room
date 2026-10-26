"""Widget specs proposed by the Widget Builder agent: validated against the role's metric catalog, converted to Lakeview."""
from dataclasses import dataclass
import yaml

VISUALS = ("counter", "bar", "line", "table", "pie")
_VERSION = {"counter": 2, "bar": 3, "line": 3, "table": 2, "pie": 3}
REQUIRED = ("title", "metric", "source", "formula", "visual")

@dataclass(frozen=True)
class MetricView:
    name: str
    measures: tuple
    dimensions: tuple
    sources: tuple

@dataclass(frozen=True)
class WidgetSpec:
    title: str
    metric: str
    source: str
    formula: str
    grain: str
    visual: str
    sources: tuple

def catalog_from_yaml(view_fqn: str, yaml_text: str) -> MetricView:
    d = yaml.safe_load(yaml_text)
    return MetricView(view_fqn, tuple(m["name"] for m in d.get("measures", [])),
                      tuple(x["name"] for x in d.get("dimensions", [])), (d["source"],))

def validate_spec(raw: dict, catalog: dict):
    errs = [f"missing field: {k}" for k in REQUIRED if not str(raw.get(k) or "").strip()]
    if errs:
        return None, errs
    title, visual, source = raw["title"].strip(), raw["visual"].strip(), raw["source"].strip()
    metric, grain = raw["metric"].strip(), str(raw.get("grain") or "").strip()
    if len(title) > 80:
        errs.append("title longer than 80 characters")
    if visual not in VISUALS:
        errs.append(f"visual '{visual}' not one of {', '.join(VISUALS)}")
    mv = catalog.get(source)
    if mv is None:
        errs.append(f"source '{source}' is not a metric view available to you")
    else:
        if metric not in mv.measures:
            errs.append(f"metric '{metric}' is not a measure of {source}")
        if grain and grain not in mv.dimensions:
            errs.append(f"grain '{grain}' is not a dimension of {source}")
    if visual in VISUALS and visual != "counter" and not grain:
        errs.append(f"visual '{visual}' needs a grain (dimension)")
    if errs:
        return None, errs
    return WidgetSpec(title, metric, source, raw["formula"].strip(), grain, visual, mv.sources), []

def widget_sql(spec: WidgetSpec) -> str:
    """The widget's dataset query — also used for the in-app preview, run as the requesting role."""
    cols = (f"`{spec.grain}`, " if spec.grain else "") + f"MEASURE(`{spec.metric}`) AS value"
    return f"SELECT {cols} FROM {spec.source}" + (" GROUP BY ALL ORDER BY 1" if spec.grain else "")

def to_lakeview_widget(spec: WidgetSpec, dataset_name: str, x: int, y: int):
    q = widget_sql(spec)
    ds = {"name": dataset_name, "displayName": spec.title, "queryLines": [q]}
    fields = ([{"name": spec.grain, "expression": f"`{spec.grain}`"}] if spec.grain else []) + \
             [{"name": "value", "expression": "`value`"}]
    if spec.visual == "counter":
        enc = {"value": {"fieldName": "value", "displayName": spec.metric}}
    elif spec.visual == "table":
        enc = {"columns": [{"fieldName": f["name"]} for f in fields]}
    elif spec.visual == "pie":
        enc = {"angle": {"fieldName": "value", "scale": {"type": "quantitative"}, "displayName": spec.metric},
               "color": {"fieldName": spec.grain, "scale": {"type": "categorical"}, "displayName": spec.grain}}
    else:
        enc = {"x": {"fieldName": spec.grain, "scale": {"type": "categorical"}, "displayName": spec.grain},
               "y": {"fieldName": "value", "scale": {"type": "quantitative"}, "displayName": spec.metric}}
    title = {"value": spec.title, "fields": []} if spec.visual == "table" else spec.title
    widget = {"name": f"w_{dataset_name}",
              "queries": [{"name": "main_query", "query": {"datasetName": dataset_name, "fields": fields, "disaggregated": True}}],
              "spec": {"version": _VERSION[spec.visual], "widgetType": spec.visual, "encodings": enc,
                       "frame": {"showTitle": True, "title": title}, "data": {"queryName": "main_query"}}}
    size = {"width": 2, "height": 3} if spec.visual == "counter" else {"width": 3, "height": 5}
    return ds, {"widget": widget, "position": {"x": x, "y": y, **size}}
