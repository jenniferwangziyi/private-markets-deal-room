"""Chat calls to a Foundation Model API endpoint (or a Unity Gateway model service), with request tags for cost attribution."""
import json, re

TAG_HEADER = "Databricks-Ai-Gateway-Request-Tags"

class PolicyBlocked(Exception):
    def __init__(self, reason: str):
        super().__init__(reason); self.reason = reason

def extract_json(text: str) -> dict:
    t = re.sub("`" * 3 + r"(?:json)?", "", text or "")      # strip code fences
    dec = json.JSONDecoder()
    for i, ch in enumerate(t):
        if ch == "{":
            try:
                obj, _ = dec.raw_decode(t[i:])
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    raise ValueError("no JSON object in model reply")

def make_chat(model: str, client=None):
    def chat(messages, tags):
        c = client
        if c is None:
            from databricks.sdk import WorkspaceClient
            from openai import OpenAI
            w = WorkspaceClient()
            token = w.config.authenticate()["Authorization"].split(" ", 1)[1]
            # catalog.schema.name = Unity Gateway model service; otherwise a Model Serving / Foundation Model API endpoint
            base = "/ai-gateway/mlflow/v1" if model.count(".") == 2 else "/serving-endpoints"
            c = OpenAI(api_key=token, base_url=f"{w.config.host}{base}")
        try:
            r = c.chat.completions.create(model=model, messages=messages, temperature=0,
                                          extra_headers={TAG_HEADER: json.dumps(tags)})
        except Exception as e:                       # some models (e.g. reasoning models) only accept the default temperature
            if "temperature" not in str(e):
                raise
            r = c.chat.completions.create(model=model, messages=messages, extra_headers={TAG_HEADER: json.dumps(tags)})
        pol = (getattr(r, "model_extra", None) or {}).get("databricks_service_policy")
        if pol and str(pol.get("result", "")).upper() == "DENY":
            raise PolicyBlocked(pol.get("reason") or "blocked by service policy")
        return r.choices[0].message.content
    return chat
