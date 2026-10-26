import json
from harbourline.ai.widget_spec import MetricView
from harbourline.ai.widget_builder import build_widget
from harbourline.ai.llm import PolicyBlocked

CAT = {"harbourline.semantic.stage3_kpis": MetricView("harbourline.semantic.stage3_kpis", ("Gross MOIC", "Net IRR %"),
                                                  ("Period", "Portfolio"), ("harbourline.vdr.portfolio_kpis",))}
PROMPT = "AVAILABLE METRICS:\n{{catalog}}"
GOOD = {"title": "Gross MOIC by period", "metric": "Gross MOIC", "source": "harbourline.semantic.stage3_kpis",
        "formula": "Value ÷ invested", "grain": "Period", "visual": "line"}

def scripted(*replies):
    calls = []
    def chat(messages, tags):
        calls.append((messages, tags)); return replies[len(calls) - 1]
    return chat, calls

def test_good_reply_ok_and_catalog_in_prompt():
    chat, calls = scripted(json.dumps(GOOD))
    out = build_widget("Show gross MOIC trend", CAT, chat, {"agent": "widget_builder"}, PROMPT)
    assert out["status"] == "ok" and out["spec"]["metric"] == "Gross MOIC" and out["attempts"] == 1
    assert "Gross MOIC" in calls[0][0][0]["content"] and calls[0][1] == {"agent": "widget_builder"}

def test_repair_after_invalid_then_ok():
    bad = dict(GOOD, metric="Revenue per room")
    chat, calls = scripted(json.dumps(bad), json.dumps(GOOD))
    out = build_widget("x", CAT, chat, {}, PROMPT)
    assert out["status"] == "ok" and out["attempts"] == 2
    assert "Revenue per room" in calls[1][0][-1]["content"]          # errors fed back for the repair attempt

def test_unknown_metric_is_rejected_not_invented():
    bad = dict(GOOD, metric="Hotel RevPAR", source="harbourline.hotel.revpar")
    chat, _ = scripted(json.dumps(bad), json.dumps(bad))
    out = build_widget("Show RevPAR", CAT, chat, {}, PROMPT)
    assert out["status"] == "rejected" and any("revpar" in e.lower() for e in out["errors"]) and "spec" not in out

def test_bad_json_twice_is_rejected():
    chat, _ = scripted("I think a bar chart", "still no json")
    assert build_widget("x", CAT, chat, {}, PROMPT)["status"] == "rejected"

def test_policy_block_is_reported():
    def chat(m, t): raise PolicyBlocked("Confidential content")
    out = build_widget("x", CAT, chat, {}, PROMPT)
    assert out == {"status": "blocked", "reason": "Confidential content"}
