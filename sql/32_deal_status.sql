CREATE TABLE IF NOT EXISTS ${vdr}.checklist_status (investment STRING, portfolio STRING, stage INT, item STRING, status STRING,
  valid_until DATE, gate_due DATE, updated_by STRING, updated_at TIMESTAMP);
ALTER TABLE ${vdr}.checklist_status ALTER COLUMN portfolio UNSET TAGS ('portfolio');
ALTER TABLE ${vdr}.checklist_status ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
CREATE OR REPLACE VIEW ${vdr}.deal_status COMMENT 'Completion %, gaps per deal-room stage (approved items only; waived/NA excluded)' AS
WITH j AS (
  SELECT c.investment, c.portfolio, c.stage, c.item, c.requirement, coalesce(s.status, 'Missing') AS status
  FROM ${vdr}.checklist_items c
  LEFT JOIN ${vdr}.checklist_status s ON s.investment = c.investment AND s.stage = c.stage AND s.item = c.item),
k AS (SELECT j.*, requirement IN ('Mandatory', 'Conditional') AND status NOT IN ('Waived', 'NotApplicable') AS counted FROM j)
SELECT investment, portfolio, stage,
       count_if(counted) AS required,
       count_if(counted AND status = 'Approved') AS approved,
       count_if(counted AND status = 'Pending') AS pending,
       CASE WHEN count_if(counted) = 0 THEN 100.0
            ELSE round(100.0 * count_if(counted AND status = 'Approved') / count_if(counted), 1) END AS completion_pct,
       collect_list(CASE WHEN counted AND status <> 'Approved' THEN item END) AS gaps
FROM k
GROUP BY investment, portfolio, stage;
CREATE OR REPLACE VIEW ${vdr}.risk_alerts COMMENT 'Deal-room risk alerts: expired documents, missing items near a gate, cross-document figure mismatches' AS
SELECT investment, portfolio, stage, 'expired' AS alert_type, concat(item, ' expired on ', cast(valid_until AS STRING)) AS message
  FROM ${vdr}.checklist_status WHERE status = 'Approved' AND valid_until < current_date()
UNION ALL
SELECT c.investment, c.portfolio, c.stage, 'missing_near_gate', concat(c.item, ' missing with stage gate due ', cast(s.gate_due AS STRING))
  FROM ${vdr}.checklist_items c JOIN (SELECT investment, stage, max(gate_due) gate_due FROM ${vdr}.checklist_status GROUP BY 1, 2) s
    ON s.investment = c.investment AND s.stage = c.stage
  LEFT JOIN ${vdr}.checklist_status st ON st.investment = c.investment AND st.stage = c.stage AND st.item = c.item
  WHERE c.requirement = 'Mandatory' AND coalesce(st.status, 'Missing') = 'Missing' AND datediff(s.gate_due, current_date()) <= 7
UNION ALL
SELECT e.deal_room, max(e.portfolio), NULL, 'figure_mismatch',
       concat('Figure mismatch — ', e.field, ': ', array_join(array_sort(collect_set(e.value)), ' vs '))
  FROM ${vdr}.doc_extracts e
  WHERE e.field IN ('fy2025_revenue_usd_m', 'fy2025_ebitda_usd_m', 'pre_money_valuation_usd_m') AND e.value IS NOT NULL
  GROUP BY e.deal_room, e.field HAVING count(DISTINCT e.value) > 1;
