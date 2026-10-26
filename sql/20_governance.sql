CREATE OR REPLACE FUNCTION ${governance}.scope_match(p_type STRING, p_val STRING) RETURNS BOOLEAN
  COMMENT 'Row visible when the active identity (assumed role via current_user()) has that scope in role_scope'
  RETURN EXISTS (SELECT 1 FROM ${governance}.role_scope s
                 WHERE s.principal = current_user() AND s.scope_type = p_type AND (s.scope_value = '*' OR s.scope_value = p_val));
CREATE OR REPLACE FUNCTION ${governance}.file_visible(portfolio STRING, deal_room STRING, classification STRING, uploaded_by STRING)
  RETURNS BOOLEAN
  RETURN ${governance}.scope_match('portfolio', portfolio)
      OR (${governance}.scope_match('deal_room', deal_room)
          AND (classification IN ('Public', 'Internal') OR uploaded_by = current_user()));
ALTER TABLE ${vdr}.file_register SET TAGS ('data_classification' = 'confidential');
ALTER TABLE ${vdr}.doc_extracts SET TAGS ('data_classification' = 'confidential');
ALTER TABLE ${vdr}.investments SET TAGS ('data_classification' = 'confidential');
ALTER TABLE ${vdr}.investments ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.portfolio_kpis ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.performance_summary ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.value_bridge ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.income_statement ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.reporting_calendar ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.risks ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.alerts ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.checklist_items ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.file_content ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.doc_extracts ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.doc_parsed ALTER COLUMN portfolio SET TAGS ('domain_portfolio_management');
ALTER TABLE ${vdr}.doc_parsed SET TAGS ('data_classification' = 'confidential');
ALTER TABLE ${vdr}.file_content SET TAGS ('data_classification' = 'confidential');
CREATE OR REPLACE FUNCTION ${governance}.scope_match_portfolio(p STRING) RETURNS BOOLEAN
  RETURN ${governance}.scope_match('portfolio', p);
CREATE OR REPLACE POLICY portfolio_rows ON SCHEMA ${vdr}
  ROW FILTER ${governance}.scope_match_portfolio
  TO `account users` EXCEPT `jennifer.wang@databricks.com`
  FOR TABLES MATCH COLUMNS has_tag('domain_portfolio_management') AS p USING COLUMNS (p);
ALTER TABLE ${vdr}.file_register SET ROW FILTER ${governance}.file_visible ON (portfolio, deal_room, classification, uploaded_by);
GRANT USE CATALOG ON CATALOG ${catalog} TO `role-business-user`;
GRANT USE CATALOG ON CATALOG ${catalog} TO `role-approver`;
GRANT USE CATALOG ON CATALOG ${catalog} TO `role-it-ai-owner`;
GRANT USE CATALOG ON CATALOG ${catalog} TO `role-external-gp`;
GRANT USE SCHEMA, SELECT ON SCHEMA ${vdr} TO `role-business-user`;
GRANT USE SCHEMA, SELECT ON SCHEMA ${vdr} TO `role-approver`;
GRANT USE SCHEMA, SELECT ON SCHEMA ${vdr} TO `role-it-ai-owner`;
GRANT USE SCHEMA, SELECT ON SCHEMA ${vdr} TO `role-external-gp`;
GRANT USE SCHEMA, SELECT ON SCHEMA ${semantic} TO `role-business-user`;
GRANT USE SCHEMA, SELECT ON SCHEMA ${semantic} TO `role-approver`;
GRANT USE SCHEMA, SELECT ON SCHEMA ${semantic} TO `role-it-ai-owner`;
GRANT USE SCHEMA, EXECUTE ON SCHEMA ${governance} TO `role-business-user`;
GRANT USE SCHEMA, EXECUTE ON SCHEMA ${governance} TO `role-approver`;
GRANT USE SCHEMA, EXECUTE ON SCHEMA ${governance} TO `role-it-ai-owner`;
GRANT USE SCHEMA, EXECUTE ON SCHEMA ${governance} TO `role-external-gp`;
GRANT READ VOLUME ON VOLUME ${vdr}.deal_rooms TO `role-business-user`;
GRANT READ VOLUME ON VOLUME ${vdr}.deal_rooms TO `role-approver`;
GRANT READ VOLUME, WRITE VOLUME ON VOLUME ${vdr}.portal_uploads TO `role-external-gp`;
GRANT READ VOLUME, WRITE VOLUME ON VOLUME ${vdr}.portal_uploads TO `role-business-user`;
