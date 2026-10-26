from harbourline.app.inbox import tasks_for

STATE = {
    "stage_pending": [{"investment": "Solace Grid Energy", "stage": 1, "approval": "Head of Investment approval"}],
    "agent_versions_awaiting": [{"model": "harbourline.ai.widget_builder", "version": "2"}],
    "feedback": [{"body": "Please add IRR vs plan", "age_days": 0}],
}

def kinds(role): return sorted(t["kind"] for t in tasks_for(role, STATE))

def test_inbox_per_role():
    assert kinds("role-approver") == ["stage_approval"]
    assert kinds("role-business-user") == ["exec_instruction"]
    assert kinds("role-it-ai-owner") == ["agent_approval"]
    assert kinds("role-external-gp") == []

def test_queue_fields():
    for role in ("role-approver", "role-business-user", "role-it-ai-owner"):
        for t in tasks_for(role, STATE):
            assert {"owner", "status", "age_days", "severity", "next_action"} <= t.keys()
