"""Widget Builder: request + the role's metric catalog -> one validated widget spec (advisory proposal)."""
import json
from dataclasses import asdict
from harbourline.ai.widget_spec import validate_spec
from harbourline.ai.llm import extract_json, PolicyBlocked

def _catalog_text(catalog) -> str:
    return "\n".join(f"- {v.name}: measures [{', '.join(v.measures)}]; dimensions [{', '.join(v.dimensions)}]"
                     for v in catalog.values())

def build_widget(request: str, catalog: dict, chat, tags: dict, prompt: str, max_attempts: int = 2) -> dict:
    messages = [{"role": "system", "content": prompt.replace("{{catalog}}", _catalog_text(catalog))},
                {"role": "user", "content": request}]
    errs = []
    for attempt in range(1, max_attempts + 1):
        try:
            reply = chat(messages, tags)
        except PolicyBlocked as b:
            return {"status": "blocked", "reason": b.reason}
        try:
            raw = extract_json(reply)
            spec, errs = validate_spec(raw, catalog)
        except ValueError as e:
            spec, errs = None, [str(e)]
        if spec:
            return {"status": "ok", "spec": {**asdict(spec), "sources": list(spec.sources)}, "attempts": attempt}
        messages += [{"role": "assistant", "content": reply},
                     {"role": "user", "content": "Fix these problems and return only the JSON object: " + "; ".join(errs)}]
    return {"status": "rejected", "errors": errs, "attempts": max_attempts}
