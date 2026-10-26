TRUNCATE hl_app.approvals, hl_app.stage_items, hl_app.deal_stage, hl_app.threads, hl_app.payment_forms,
         hl_app.widget_proposals, hl_app.rule_versions, hl_app.feedback, hl_app.uploads;
INSERT INTO hl_app.deal_stage(investment, stage, gate_due) VALUES ('Solace Grid Energy', 1, current_date + 3);
INSERT INTO hl_app.stage_items(investment, stage, item, status, valid_until, run_by, run_as) VALUES
  ('Solace Grid Energy', 1, 'Fund Overview - Pitch deck', 'Approved', NULL, 'seed', 'role-approver'),
  ('Solace Grid Energy', 1, 'Organization chart', 'Approved', NULL, 'seed', 'role-approver'),
  ('Solace Grid Energy', 1, 'High-level Track Record', 'Approved', NULL, 'seed', 'role-approver'),
  ('Solace Grid Energy', 1, 'IC overview', 'Approved', NULL, 'seed', 'role-approver'),
  ('Solace Grid Energy', 1, 'NDA', 'Approved', NULL, 'seed', 'role-approver'),
  ('Solace Grid Energy', 1, 'PPM - Key Terms Summary (Draft)', 'Approved', NULL, 'seed', 'role-approver');   -- only the Head of Investment approval is left
INSERT INTO hl_app.threads(room, body, run_by, run_as) VALUES
  ('Solace Grid Energy', 'Welcome to the Solace Grid Energy deal room. Please upload the Stage 2 diligence pack here.', 'seed', 'role-business-user');
