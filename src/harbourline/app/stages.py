"""Deal-room stage gate: approvals can be recorded once documents are complete; advance when all approvals exist."""
COUNTED = ("Mandatory", "Conditional")
EXCLUDED = ("Waived", "NotApplicable")

def gate_status(items: list) -> dict:
    req = [i for i in items if i["requirement"] in COUNTED and i["status"] not in EXCLUDED]
    docs = [i for i in req if i["kind"] == "document"]
    approvals = [i for i in req if i["kind"] == "approval"]
    gaps = [i["item"] for i in docs if i["status"] != "Approved"]
    missing = [i["item"] for i in approvals if i["status"] != "Approved"]
    done = sum(i["status"] == "Approved" for i in req)
    return {"completion_pct": round(100.0 * done / len(req), 1) if req else 100.0, "gaps": gaps,
            "missing_approvals": missing, "documents_complete": not gaps, "can_advance": not gaps and not missing}

def check_item_change(kind: str, requirement: str, status: str, has_file: bool):
    """Reason the change is refused, or None. Mandatory items cannot be waived; a document needs a file to be approved."""
    if status in EXCLUDED and requirement == "Mandatory":
        return "Mandatory items cannot be waived or marked not applicable"
    if status == "Approved" and kind == "document" and not has_file:
        return "Cannot approve a document with no file received"
    return None
