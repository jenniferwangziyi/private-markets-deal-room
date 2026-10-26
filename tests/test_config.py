from harbourline.config import load_names

def test_names_with_prefix(tmp_path):
    p = tmp_path / "demo.yml"
    p.write_text("profile: hunter\nwarehouse_id: w1\ncatalog: jennifer_wang\nschema_prefix: hl_\nroles: {role-approver: '42'}\n")
    n = load_names(p)
    assert n.vdr == "jennifer_wang.hl_vdr"
    assert n.governance == "jennifer_wang.hl_governance"
    assert n.roles["role-approver"] == "42"

def test_names_without_prefix(tmp_path):
    p = tmp_path / "demo.yml"
    p.write_text("profile: hunter\nwarehouse_id: w1\ncatalog: harbourline\nschema_prefix: ''\nroles: {}\n")
    assert load_names(p).vdr == "harbourline.vdr"

def test_ai_names(tmp_path):
    p = tmp_path / "demo.yml"
    p.write_text("profile: hunter\nwarehouse_id: w1\ncatalog: harbourline\nschema_prefix: ''\nroles: {}\n"
                 "ai: {llm_model: databricks-gpt-oss-120b, eval_threshold: 0.8}\n")
    n = load_names(p)
    assert n.ai == "harbourline.ai" and n.ai_cfg["llm_model"] == "databricks-gpt-oss-120b" and n.ai_cfg["eval_threshold"] == 0.8
