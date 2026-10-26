INSERT INTO ${vdr}.checklist_items VALUES ('ZZ Test', 'Fund I', 1, 'Doc A', 'document', 'Mandatory', NULL),
  ('ZZ Test', 'Fund I', 1, 'Doc B', 'document', 'Mandatory', NULL), ('ZZ Test', 'Fund I', 1, 'Doc C', 'document', 'Conditional', NULL),
  ('ZZ Test', 'Fund I', 1, 'Doc D', 'document', 'Optional', NULL), ('ZZ Waived', 'Fund I', 1, 'Side letter', 'document', 'Conditional', NULL);
INSERT INTO ${vdr}.checklist_status VALUES ('ZZ Test', 'Fund I', 1, 'Doc A', 'Approved', DATE'2020-01-01', current_date() + 3, 'test', current_timestamp()),
  ('ZZ Test', 'Fund I', 1, 'Doc C', 'Waived', NULL, current_date() + 3, 'test', current_timestamp()),
  ('ZZ Waived', 'Fund I', 1, 'Side letter', 'Waived', NULL, NULL, 'test', current_timestamp());
SELECT investment, required, approved, completion_pct, size(gaps) AS gaps FROM ${vdr}.deal_status WHERE investment LIKE 'ZZ%' ORDER BY 1;
SELECT investment, alert_type FROM ${vdr}.risk_alerts WHERE investment LIKE 'ZZ%' ORDER BY 2;
DELETE FROM ${vdr}.checklist_items WHERE investment LIKE 'ZZ%';
DELETE FROM ${vdr}.checklist_status WHERE investment LIKE 'ZZ%';
