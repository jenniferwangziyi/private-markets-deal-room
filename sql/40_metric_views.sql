CREATE OR REPLACE VIEW ${semantic}.stage3_kpis WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Certified Stage 3 post-investment KPIs for the portfolio monitoring dashboard. USD."
source: ${vdr}.portfolio_kpis
dimensions:
  - name: Period
    expr: period
  - name: Portfolio
    expr: portfolio
measures:
  - name: Total Invested Capital
    expr: MAX(CASE WHEN kpi = 'total_invested_usd' THEN value END)
    synonyms: ["invested capital", "總投資額"]
  - name: Current Portfolio Value
    expr: MAX(CASE WHEN kpi = 'current_value_usd' THEN value END)
  - name: Gross MOIC
    expr: MAX(CASE WHEN kpi = 'gross_moic' THEN value END)
  - name: Gross IRR %
    expr: MAX(CASE WHEN kpi = 'gross_irr_pct' THEN value END)
  - name: Net MOIC
    expr: MAX(CASE WHEN kpi = 'net_moic' THEN value END)
  - name: Net IRR %
    expr: MAX(CASE WHEN kpi = 'net_irr_pct' THEN value END)
  - name: Realized Proceeds
    expr: MAX(CASE WHEN kpi = 'realized_usd' THEN value END)
  - name: Unrealized Value
    expr: MAX(CASE WHEN kpi = 'unrealized_usd' THEN value END)
$$;
CREATE OR REPLACE VIEW ${semantic}.deal_room_completion WITH METRICS LANGUAGE YAML AS $$
version: 1.1
comment: "Deal-room completion per stage: approved required items ÷ required items (waived / not applicable excluded)."
source: ${vdr}.deal_status
dimensions:
  - name: Investment
    expr: investment
  - name: Portfolio
    expr: portfolio
  - name: Stage
    expr: stage
measures:
  - name: Required Items
    expr: SUM(required)
  - name: Approved Items
    expr: SUM(approved)
  - name: Completion %
    expr: CASE WHEN SUM(required) = 0 THEN 100.0 ELSE ROUND(100.0 * SUM(approved) / SUM(required), 1) END
    synonyms: ["completion rate", "完成率"]
  - name: Gaps
    expr: SUM(size(gaps))
$$;
CREATE TABLE IF NOT EXISTS ${semantic}.business_glossary (term STRING, definition STRING, synonyms ARRAY<STRING>, owner STRING, domain STRING);
INSERT OVERWRITE ${semantic}.business_glossary VALUES
  ('Completion %', 'Approved required documents and approvals ÷ required items for the stage, excluding waived / not applicable', array('completion rate', '完成率'), 'role-approver', 'deal room'),
  ('Gap', 'A required document or approval not yet approved for the current stage', array('missing item'), 'role-approver', 'deal room'),
  ('Risk Alert', 'Critical item missing near a stage gate, an expired document, or a figure mismatch across documents', array('red flag'), 'role-approver', 'deal room'),
  ('MOIC', 'Multiple on invested capital = current value + realized proceeds ÷ invested capital', array('multiple', '投資倍數'), 'role-approver', 'deal room'),
  ('Total Invested Capital', 'Cumulative capital Harbourline has deployed into a portfolio''s Stage 3 companies, USD, at the latest reporting period. Certified measure `Total Invested Capital` in semantic.stage3_kpis; used by the Stage 3 dashboard tile, Genie and the Widget Builder', array('invested capital', 'capital deployed', '總投資額', '总投资额'), 'role-approver', 'deal room');
COMMENT ON TABLE ${vdr}.file_register IS 'Every deal-room file with portfolio, room, path, source, classification and status';
