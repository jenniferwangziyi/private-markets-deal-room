SELECT 'unfiltered_portfolio_tables' AS check, concat_ws(',', sort_array(collect_list(c.table_name))) AS result
FROM ${catalog}.information_schema.columns c
LEFT JOIN ${catalog}.information_schema.column_tags t
  ON t.schema_name = c.table_schema AND t.table_name = c.table_name AND t.column_name = c.column_name AND t.tag_name = 'domain_portfolio_management'
JOIN ${catalog}.information_schema.tables tb ON tb.table_schema = c.table_schema AND tb.table_name = c.table_name AND tb.table_type <> 'VIEW'
WHERE c.table_schema = '${vdr_leaf}' AND c.column_name = 'portfolio' AND t.tag_name IS NULL AND c.table_name <> 'file_register';
SELECT 'doc_parsed_has_portfolio', cast(count(*) AS STRING) FROM ${catalog}.information_schema.columns
WHERE table_schema = '${vdr_leaf}' AND table_name = 'doc_parsed' AND column_name = 'portfolio';
SELECT 'scope_type_checked', cast(NOT ${governance}.scope_match('zz_no_such_type', 'x') AS STRING);
