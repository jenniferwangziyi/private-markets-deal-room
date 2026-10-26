CREATE SCHEMA IF NOT EXISTS hl_app;
CREATE TABLE IF NOT EXISTS hl_app.approvals (id BIGSERIAL PRIMARY KEY, scope TEXT, ref TEXT, decision TEXT, note TEXT,
  run_by TEXT, run_as TEXT, at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS hl_app.stage_items (investment TEXT, stage INT, item TEXT, status TEXT, valid_until DATE,
  run_by TEXT, run_as TEXT, at TIMESTAMPTZ DEFAULT now(), PRIMARY KEY (investment, stage, item));
CREATE TABLE IF NOT EXISTS hl_app.deal_stage (investment TEXT PRIMARY KEY, stage INT, gate_due DATE, at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS hl_app.threads (id BIGSERIAL PRIMARY KEY, room TEXT, body TEXT, run_by TEXT, run_as TEXT,
  at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS hl_app.payment_forms (id TEXT PRIMARY KEY, data JSONB, state TEXT, updated_at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS hl_app.widget_proposals (id BIGSERIAL PRIMARY KEY, request TEXT, result JSONB, status TEXT,
  run_by TEXT, run_as TEXT, at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS hl_app.rule_versions (version INT PRIMARY KEY, vals JSONB, status TEXT, proposed_by TEXT,
  proposed_as TEXT, approved_as TEXT, at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS hl_app.feedback (id BIGSERIAL PRIMARY KEY, target TEXT, body TEXT, run_by TEXT, run_as TEXT,
  at TIMESTAMPTZ DEFAULT now());
CREATE TABLE IF NOT EXISTS hl_app.uploads (id BIGSERIAL PRIMARY KEY, room TEXT, path TEXT, run_by TEXT, run_as TEXT,
  at TIMESTAMPTZ DEFAULT now());
