INSERT INTO ${vdr}.doc_parsed
SELECT f.file_id, f.portfolio, f.path,
       ai_parse_document(c.content, map('version', '2.0', 'imageOutputPath', '/Volumes/${catalog}/${vdr_leaf}/deal_rooms/_page_images/')),
       current_timestamp()
FROM ${vdr}.file_register f
JOIN ${vdr}.file_content c ON c.path = f.path
WHERE f.file_id NOT IN (SELECT file_id FROM ${vdr}.doc_parsed);
-- 1) document type (maps to checklist item) + information classification level, each with confidence.
--    Kept as rows in doc_extracts (field ai_document_type / ai_classification) so the app can show them.
INSERT INTO ${vdr}.doc_extracts
WITH c AS (
  SELECT f.file_id, f.portfolio, f.deal_room,
    ai_classify(p.parsed, '["Fund Overview - Pitch deck","PPM - Key Terms Summary (Draft)","Organization chart","IC overview","High-level Track Record","NDA","PPM","LPA","Subscription Agreement (Draft)","Side letter template","DDQ","Historical IC memos","Valuation & Financials","Portfolio asset-level diligence","Quarterly report Q2 2026","Capital account statement","Capital call notice","Distribution notice","Financial statements FY2025","Tax documents","Investor communication"]',
                map('version', '2.1', 'enableConfidenceScores', 'true')) AS doc_type,
    ai_classify(p.parsed, '{"Public":"Approved for public release","Internal":"Standard business information, not public","Confidential":"Sensitive business information: valuations, terms, financials, deal documents","Highly Restricted":"Personal data protected by law (PDPO/GDPR/PIPL) or highly sensitive"}',
                map('version', '2.1', 'enableConfidenceScores', 'true', 'instructions', 'Harbourline Capital 4-level information classification standard.')) AS cls
  FROM ${vdr}.doc_parsed p JOIN ${vdr}.file_register f ON f.file_id = p.file_id
  WHERE p.file_id NOT IN (SELECT file_id FROM ${vdr}.doc_extracts WHERE field = 'ai_document_type'))
SELECT file_id, portfolio, deal_room, 'ai_document_type', doc_type:response[0]:value::STRING,
       doc_type:response[0]:confidence_score::DOUBLE, NULL, NULL, NULL, NULL FROM c
UNION ALL
SELECT file_id, portfolio, deal_room, 'ai_classification', cls:response[0]:value::STRING,
       cls:response[0]:confidence_score::DOUBLE, NULL, NULL, NULL, NULL FROM c;
MERGE INTO ${vdr}.file_register t
USING (
  SELECT file_id, max(IF(field = 'ai_document_type', value, NULL)) AS doc_type, max(IF(field = 'ai_document_type', confidence, NULL)) AS type_conf,
         max(IF(field = 'ai_classification', value, NULL)) AS cls, max(IF(field = 'ai_classification', confidence, NULL)) AS cls_conf
  FROM ${vdr}.doc_extracts WHERE field IN ('ai_document_type', 'ai_classification') GROUP BY file_id) s
ON t.file_id = s.file_id
WHEN MATCHED AND t.status = 'Received' THEN UPDATE SET              -- never re-classify reviewed files
  t.file_type = s.doc_type,
  t.classification = CASE WHEN coalesce(s.cls_conf, 0) >= 0.8 THEN s.cls ELSE 'Confidential' END,   -- unsure -> stay restrictive
  t.status = CASE WHEN least(coalesce(s.type_conf, 0), coalesce(s.cls_conf, 0)) < 0.8 THEN 'Needs review' ELSE 'Classified' END;
-- 2) key figures with confidence + citation (bounding box -> source-file link in the app)
INSERT INTO ${vdr}.doc_extracts
WITH x AS (
  SELECT f.file_id, f.portfolio, f.deal_room,
         ai_extract(p.parsed, '{
           "company_name": {"type": "string", "description": "Investee company the document is about"},
           "pre_money_valuation_usd_m": {"type": "number", "description": "Pre-money valuation in USD millions"},
           "fy2025_revenue_usd_m": {"type": "number", "description": "FY2025 revenue in USD millions"},
           "fy2025_ebitda_usd_m": {"type": "number", "description": "FY2025 EBITDA in USD millions"},
           "document_date": {"type": "string", "description": "Document date, YYYY-MM-DD"}}',
           map('version', '2.1', 'enableConfidenceScores', 'true', 'enableCitations', 'true',
               'instructions', 'Investment deal-room documents for Harbourline Capital Fund & Investment.')) AS r
  FROM ${vdr}.file_register f JOIN ${vdr}.doc_parsed p ON p.file_id = f.file_id
  WHERE f.file_id NOT IN (SELECT DISTINCT file_id FROM ${vdr}.doc_extracts WHERE field NOT LIKE 'ai\\_%'))
SELECT file_id, portfolio, deal_room, k AS field, v:value::STRING AS value, v:confidence_score::DOUBLE AS confidence,
       NULL, NULL, NULL, r:metadata:citations
FROM x LATERAL VIEW explode(cast(r:response AS MAP<STRING, VARIANT>)) t AS k, v
WHERE v:value::STRING IS NOT NULL;
