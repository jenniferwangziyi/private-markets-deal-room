INSERT OVERWRITE ${vdr}.investments SELECT name, sector, CAST(revenue_growth_pct AS DOUBLE), CAST(ebitda_margin_pct AS DOUBLE),
  CAST(moic_gross AS DOUBLE), CAST(vs_plan_ebitda_pp AS DOUBLE), status, CAST(stage AS INT), portfolio, classification
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/investments.csv', format => 'csv', header => true);
INSERT OVERWRITE ${vdr}.portfolio_kpis SELECT period, kpi, CAST(value AS DOUBLE), 'Fund I'
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/portfolio_kpis.csv', format => 'csv', header => true);
-- Prior quarter (2026-Q1) so the Stage 3 period filter has a comparison point: Q2 values scaled back ~4% (ratios ~2%).
INSERT INTO ${vdr}.portfolio_kpis SELECT '2026-Q1', kpi,
  round(value * CASE WHEN kpi RLIKE 'moic|pct|irr' THEN 0.98 ELSE 0.96 END, 4), portfolio
  FROM ${vdr}.portfolio_kpis WHERE period = '2026-Q2';
INSERT OVERWRITE ${vdr}.performance_summary SELECT metric, CAST(actual_ltm_pct AS DOUBLE), CAST(investment_case_pct AS DOUBLE),
  CAST(variance_pp AS DOUBLE), 'Fund I'
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/performance_summary.csv', format => 'csv', header => true);
INSERT OVERWRITE ${vdr}.value_bridge SELECT step, CAST(usd_m AS DOUBLE), CAST(monotonically_increasing_id() AS INT), 'Fund I'
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/value_bridge.csv', format => 'csv', header => true);
INSERT OVERWRITE ${vdr}.income_statement SELECT line, CAST(actual_usd_m AS DOUBLE), CAST(plan_usd_m AS DOUBLE), 'Fund I'
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/income_statement.csv', format => 'csv', header => true);
INSERT OVERWRITE ${vdr}.reporting_calendar SELECT investment, report, CAST(due_date AS DATE), status, portfolio
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/reporting_calendar.csv', format => 'csv', header => true);
INSERT OVERWRITE ${vdr}.risks SELECT investment, inherent, current, trend, driver, portfolio
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/risks.csv', format => 'csv', header => true);
INSERT OVERWRITE ${vdr}.alerts SELECT alert, CAST(count AS INT), detail, portfolio
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/alerts.csv', format => 'csv', header => true);
INSERT OVERWRITE ${vdr}.checklist_items SELECT investment, 'Fund I', CAST(stage AS INT), item, kind, requirement,
  CAST(NULLIF(validity_days, '') AS INT)
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/checklist_items.csv', format => 'csv', header => true);
INSERT OVERWRITE ${governance}.role_scope SELECT principal, scope_type, scope_value
  FROM read_files('/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_staging_tables/role_scope.csv', format => 'csv', header => true);
INSERT INTO ${governance}.role_scope VALUES (current_user(), 'portfolio', '*'),
  (current_user(), 'deal_room', '*');
INSERT OVERWRITE ${governance}.model_register VALUES
  ('databricks-gpt-oss-120b', 'Open-weight model via Databricks Foundation Model APIs', '120b', 'Databricks-hosted (Azure)', true, 'role-it-ai-owner', current_timestamp()),
  ('databricks-gte-large-en', 'Databricks', '1', 'Databricks-hosted (Azure)', true, 'role-it-ai-owner', current_timestamp()),
  ('databricks-gpt-5-4-mini', 'External-class provider (demo stand-in)', '5.4-mini', 'Treated as external: no Confidential data', true, 'role-it-ai-owner', current_timestamp()),
  ('public-consumer-chatbot', 'Public consumer endpoint', 'n/a', 'Unknown', false, NULL, NULL);
