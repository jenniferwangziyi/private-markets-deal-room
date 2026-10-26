from harbourline.app.stages import gate_status

def items(**status):
    base = [("NDA", "document", "Mandatory"), ("Pitch deck", "document", "Mandatory"), ("Side letter", "document", "Conditional"),
            ("Org chart", "document", "Optional"), ("Head of Investment approval", "approval", "Mandatory")]
    return [{"item": i, "kind": k, "requirement": r, "status": status.get(i.split()[0], "Missing")} for i, k, r in base]

def test_gate_locked_until_required_approvals():
    g = gate_status(items(NDA="Approved", Pitch="Approved", Side="Waived"))
    assert g["documents_complete"] and not g["can_advance"] and g["missing_approvals"] == ["Head of Investment approval"]
    g = gate_status(items(NDA="Approved", Pitch="Approved", Side="Waived", Head="Approved"))
    assert g["can_advance"] and g["completion_pct"] == 100.0

def test_gaps_block_approval_and_optional_ignored():
    g = gate_status(items(NDA="Approved"))
    assert not g["documents_complete"] and g["gaps"] == ["Pitch deck", "Side letter"] and g["completion_pct"] == 25.0

from harbourline.app.stages import check_item_change

def test_item_change_rules():
    assert "Mandatory" in check_item_change("document", "Mandatory", "Waived", has_file=True)
    assert "no file" in check_item_change("document", "Mandatory", "Approved", has_file=False)
    assert check_item_change("document", "Conditional", "Waived", has_file=False) is None
    assert check_item_change("approval", "Mandatory", "Approved", has_file=False) is None
