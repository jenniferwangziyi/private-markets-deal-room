CREATE SCHEMA IF NOT EXISTS ${ai} COMMENT 'AI assets: agent models, prompts, model services, service policies';
GRANT USE SCHEMA ON SCHEMA ${ai} TO `role-business-user`;
GRANT USE SCHEMA ON SCHEMA ${ai} TO `role-approver`;
GRANT USE SCHEMA ON SCHEMA ${ai} TO `role-it-ai-owner`;
GRANT EXECUTE ON SCHEMA ${ai} TO `role-it-ai-owner`;
INSERT OVERWRITE ${governance}.model_register VALUES
  ('databricks-gpt-oss-120b', 'Open-weight model via Databricks Foundation Model APIs', '120b', 'Databricks-hosted (Azure)', true, 'role-it-ai-owner', current_timestamp()),
  ('databricks-gte-large-en', 'Databricks', '1', 'Databricks-hosted (Azure)', true, 'role-it-ai-owner', current_timestamp()),
  ('databricks-gpt-5-4-mini', 'External-class provider (demo stand-in)', '5.4-mini', 'Treated as external: no Confidential data', true, 'role-it-ai-owner', current_timestamp()),
  ('public-consumer-chatbot', 'Public consumer endpoint', 'n/a', 'Unknown', false, NULL, NULL);
GRANT SELECT ON TABLE ${governance}.model_register TO `role-it-ai-owner`;
GRANT SELECT ON TABLE ${governance}.model_register TO `role-approver`;
