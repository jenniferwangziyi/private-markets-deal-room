import json, pytest
from types import SimpleNamespace
from harbourline.ai.llm import extract_json, make_chat, PolicyBlocked

def test_extract_json_variants():
    assert extract_json('{"a": 1}') == {"a": 1}
    fence = "`" * 3
    assert extract_json(f"Here you go:\n{fence}json\n{{\"a\": 2}}\n{fence}") == {"a": 2}
    assert extract_json('Sure! {"a": {"b": 3}} hope that helps') == {"a": {"b": 3}}
    with pytest.raises(ValueError):
        extract_json("no json here")
    with pytest.raises(ValueError):
        extract_json('{"a": 1')

class FakeCompletions:
    def __init__(self, reply="ok", extra=None): self.reply, self.extra, self.calls = reply, extra or {}, []
    def create(self, **kw):
        self.calls.append(kw)
        msg = SimpleNamespace(content=self.reply)
        return SimpleNamespace(choices=[SimpleNamespace(message=msg)], model_extra=self.extra)

def fake_client(**kw):
    comp = FakeCompletions(**kw)
    return SimpleNamespace(chat=SimpleNamespace(completions=comp)), comp

def test_chat_sends_model_tags_and_temperature():
    client, comp = fake_client(reply="hello")
    chat = make_chat("databricks-gpt-oss-120b", client=client)
    assert chat([{"role": "user", "content": "hi"}], {"agent": "widget_builder", "role": "role-business-user"}) == "hello"
    kw = comp.calls[0]
    assert kw["model"] == "databricks-gpt-oss-120b" and kw["temperature"] == 0
    assert json.loads(kw["extra_headers"]["Databricks-Ai-Gateway-Request-Tags"]) == {"agent": "widget_builder", "role": "role-business-user"}

def test_policy_block_raises():
    client, _ = fake_client(reply="Request blocked", extra={"databricks_service_policy": {"result": "DENY", "reason": "Confidential content"}})
    with pytest.raises(PolicyBlocked) as e:
        make_chat("databricks-gpt-oss-120b", client=client)([{"role": "user", "content": "x"}], {})
    assert "Confidential" in e.value.reason
