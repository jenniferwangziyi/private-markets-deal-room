"""Work queue: one queue per active role, derived from app state.
Each item: kind, title, page, owner, status, age_days, severity (High/Medium/Low), next_action."""

def _t(kind, title, page, owner, status, age, severity, next_action):
    return {"kind": kind, "title": title, "page": page, "owner": owner, "status": status,
            "age_days": age, "severity": severity, "next_action": next_action}

def tasks_for(role: str, s: dict) -> list:
    t = []
    if role == "role-approver":
        for g in s.get("stage_pending", []):
            t.append(_t("stage_approval", f"{g['approval']} — {g['investment']} stage {g['stage']}", "dealroom", "Head of Investment",
                        "awaiting approval", None, "Medium", "Record the stage approval"))
    elif role == "role-business-user":
        for f in s.get("feedback", []):
            t.append(_t("exec_instruction", f"Executive instruction: {f['body']}", "stage3", "Deal-room controller", "open",
                        f.get("age_days"), "Medium", "Action it and reply in the deal-room thread"))
    elif role == "role-it-ai-owner":
        for v in s.get("agent_versions_awaiting", []):
            t.append(_t("agent_approval", f"Approve agent {v['model'].rsplit('.', 1)[-1]} v{v['version']}", "marketplace", "IT & AI owner",
                        "evaluated", None, "Low", "Review evaluation evidence, then Approve"))
    return t
