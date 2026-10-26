CREATE TABLE IF NOT EXISTS ${vdr}.file_register (file_id STRING, portfolio STRING, deal_room STRING, name STRING, file_type STRING,
  path STRING, stage INT, received_at TIMESTAMP, source STRING, uploaded_by STRING, classification STRING, status STRING)
  COMMENT 'Every deal-room file: portfolio, room, path, source, classification, processing status';
CREATE TABLE IF NOT EXISTS ${vdr}.file_content (file_id STRING, portfolio STRING, path STRING, content BINARY)
  COMMENT 'Raw bytes of each ingested deal-room file (input to ai_parse_document)';
CREATE TABLE IF NOT EXISTS ${vdr}.doc_parsed (file_id STRING, portfolio STRING, path STRING, parsed VARIANT, parsed_at TIMESTAMP)
  COMMENT 'ai_parse_document output per deal-room file';
CREATE TABLE IF NOT EXISTS ${vdr}.doc_extracts (file_id STRING, portfolio STRING, deal_room STRING, field STRING, value STRING,
  confidence DOUBLE, reviewed_by STRING, reviewed_at TIMESTAMP, corrected_value STRING, citation VARIANT);
CREATE TABLE IF NOT EXISTS ${vdr}.checklist_items (investment STRING, portfolio STRING, stage INT, item STRING, kind STRING,
  requirement STRING, validity_days INT);
CREATE TABLE IF NOT EXISTS ${vdr}.investments (name STRING, sector STRING, revenue_growth_pct DOUBLE, ebitda_margin_pct DOUBLE,
  moic_gross DOUBLE, vs_plan_ebitda_pp DOUBLE, status STRING, stage INT, portfolio STRING, classification STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.portfolio_kpis (period STRING, kpi STRING, value DOUBLE, portfolio STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.performance_summary (metric STRING, actual_ltm_pct DOUBLE, investment_case_pct DOUBLE, variance_pp DOUBLE, portfolio STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.value_bridge (step STRING, usd_m DOUBLE, step_order INT, portfolio STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.income_statement (line STRING, actual_usd_m DOUBLE, plan_usd_m DOUBLE, portfolio STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.reporting_calendar (investment STRING, report STRING, due_date DATE, status STRING, portfolio STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.risks (investment STRING, inherent STRING, current STRING, trend STRING, driver STRING, portfolio STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.alerts (alert STRING, count INT, detail STRING, portfolio STRING);
CREATE TABLE IF NOT EXISTS ${vdr}.external_factors (series STRING, label STRING, value DOUBLE, unit STRING, observed_at DATE,
  source STRING, tag STRING, loaded_at TIMESTAMP, prev_value DOUBLE);
CREATE TABLE IF NOT EXISTS ${governance}.role_scope (principal STRING, scope_type STRING, scope_value STRING);
CREATE TABLE IF NOT EXISTS ${governance}.model_register (model STRING, provider STRING, version STRING, hosting STRING,
  approved BOOLEAN, approved_by STRING, approved_at TIMESTAMP);
