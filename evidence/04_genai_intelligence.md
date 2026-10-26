# ML / GenAI — make it intelligent
_Captured 2026-10-26 06:39 UTC from workspace `hunter` (catalog `harbourline`) by `scripts/collect_evidence.py`._

## AI Functions on every raw document: ai_parse_document → ai_classify (type + classification, with confidence) → ai_extract

```sql
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
  
-- (truncated; full file in sql/35_ai_extract.sql)
```

## ai_classify / ai_extract output (real model output, stored in vdr.doc_extracts)

| deal_room | name | field | value | confidence | routed_to |
|---|---|---|---|---|---|
| Kestrel Robotics | Historical_IC_memos.pdf | ai_classification | Confidential | 0.86 | Classified |
| Kestrel Robotics | Historical_IC_memos.pdf | ai_document_type | Historical IC memos | 0.9 | Classified |
| Kestrel Robotics | Historical_IC_memos.pdf | company_name | Kestrel Robotics | 0.95 | Classified |
| Kestrel Robotics | Historical_IC_memos.pdf | fy2025_revenue_usd_m | 5.4 | 1.0 | Classified |
| Kestrel Robotics | Valuation_&_Financials.pdf | ai_classification | Confidential | 0.92 | Classified |
| Kestrel Robotics | Valuation_&_Financials.pdf | ai_document_type | Valuation & Financials | 0.94 | Classified |
| Kestrel Robotics | Valuation_&_Financials.pdf | company_name | Kestrel Robotics | 1.0 | Classified |
| Kestrel Robotics | Valuation_&_Financials.pdf | fy2025_ebitda_usd_m | 0.9 | 1.0 | Classified |
| Kestrel Robotics | Valuation_&_Financials.pdf | fy2025_revenue_usd_m | 6.1 | 1.0 | Classified |
| Kestrel Robotics | Valuation_&_Financials.pdf | pre_money_valuation_usd_m | 48 | 1.0 | Classified |
| Solace Grid Energy | Fund_Overview_-_Pitch_deck.pdf | ai_classification | Confidential | 0.94 | Classified |
| Solace Grid Energy | Fund_Overview_-_Pitch_deck.pdf | ai_document_type | Fund Overview - Pitch deck | 0.92 | Classified |
| Solace Grid Energy | Fund_Overview_-_Pitch_deck.pdf | company_name | Solace Grid Energy | 1.0 | Classified |
| Solace Grid Energy | High-level_Track_Record.pdf | ai_classification | Confidential | 0.85 | Classified |
| Solace Grid Energy | High-level_Track_Record.pdf | ai_document_type | High-level Track Record | 0.93 | Classified |
| Solace Grid Energy | High-level_Track_Record.pdf | company_name | Solace Grid Energy | 1.0 | Classified |
| Solace Grid Energy | IC_overview.pdf | ai_classification | Confidential | 0.85 | Classified |
| Solace Grid Energy | IC_overview.pdf | ai_document_type | IC overview | 0.85 | Classified |
| Solace Grid Energy | IC_overview.pdf | company_name | Solace Grid Energy | 1.0 | Classified |
| Solace Grid Energy | NDA.pdf | ai_classification | Confidential | 0.86 | Classified |
| Solace Grid Energy | NDA.pdf | ai_document_type | NDA | 0.92 | Classified |
| Solace Grid Energy | NDA.pdf | company_name | Solace Grid Energy | 1.0 | Classified |
| Solace Grid Energy | Organization_chart.pdf | ai_classification | Confidential | 0.93 | Classified |
| Solace Grid Energy | Organization_chart.pdf | ai_document_type | Organization chart | 0.96 | Classified |
| Solace Grid Energy | Organization_chart.pdf | company_name | Solace Grid Energy | 1.0 | Classified |
| Solace Grid Energy | PPM_-_Key_Terms_Summary_(Draft).pdf | ai_classification | Confidential | 0.78 | Needs review |
| Solace Grid Energy | PPM_-_Key_Terms_Summary_(Draft).pdf | ai_document_type | PPM - Key Terms Summary (Draft) | 0.92 | Needs review |
| Solace Grid Energy | PPM_-_Key_Terms_Summary_(Draft).pdf | company_name | Solace Grid Energy | 1.0 | Needs review |

_28 row(s)_

## Cross-document check: figure mismatch raised from the AI extraction

| investment | portfolio | stage | alert_type | message |
|---|---|---|---|---|
| Kestrel Robotics | Fund I | NULL | figure_mismatch | Figure mismatch — fy2025_revenue_usd_m: 5.4 vs 6.1 |
| Solace Grid Energy | Fund I | 1 | missing_near_gate | Head of Investment approval missing with stage gate due 2026-10-29 |

_2 row(s)_

## ai_query — market-risk note for a deal (open-weight model)

| risk_note |
|---|
| Key risks include (1) commodity‑price exposure – Brent’s dip to $115.2 bbl could compress Solace Grid’s power‑sale margins; (2) macro‑economic slowdown signals – the US 10‑yr yield’s fall to 4.96% may presage weaker demand and tighter financing conditions; and (3) modest USD/CNY appreciation, which could raise the cost of imported turbine or EPC equipment. Diligence action: run a multi‑scenario cash‑flow stress test incorporating lower oil prices, FX swings and tighter credit spreads to validate debt‑service coverage. |

_1 row(s)_

## Widget Builder agent (LLM → validated widget spec on certified metrics only)

**Request:** Show gross MOIC by period as a bar chart  
**Latency:** 5.2 s

```json
{
  "status": "ok",
  "spec": {
    "title": "Gross MOIC by Period",
    "metric": "Gross MOIC",
    "source": "harbourline.semantic.stage3_kpis",
    "formula": "Shows the gross multiple on invested capital for each period.",
    "grain": "Period",
    "visual": "bar",
    "sources": [
      "harbourline.vdr.portfolio_kpis"
    ]
  },
  "attempts": 1
}
```

Preview query the widget will run (as the viewer):

```sql
SELECT `Period`, MEASURE(`Gross MOIC`) AS value FROM harbourline.semantic.stage3_kpis GROUP BY ALL ORDER BY 1
```

| Period | value |
|---|---|
| 2026-Q1 | 1.3622 |
| 2026-Q2 | 1.39 |

_2 row(s)_

---

**Request:** Total invested capital for Fund I as a KPI tile  
**Latency:** 4.6 s

```json
{
  "status": "ok",
  "spec": {
    "title": "Total Invested Capital",
    "metric": "Total Invested Capital",
    "source": "harbourline.semantic.stage3_kpis",
    "formula": "Total invested capital for Fund I",
    "grain": "Portfolio",
    "visual": "counter",
    "sources": [
      "harbourline.vdr.portfolio_kpis"
    ]
  },
  "attempts": 1
}
```

Preview query the widget will run (as the viewer):

```sql
SELECT `Portfolio`, MEASURE(`Total Invested Capital`) AS value FROM harbourline.semantic.stage3_kpis GROUP BY ALL ORDER BY 1
```

| Portfolio | value |
|---|---|
| Fund I | 2.86E9 |

_1 row(s)_

---

**Request:** Hotel RevPAR by property  
**Latency:** 4.1 s

```json
{
  "status": "ok",
  "spec": {
    "title": "Current Portfolio Value by Portfolio",
    "metric": "Current Portfolio Value",
    "source": "harbourline.semantic.stage3_kpis",
    "formula": "Shows the current value of each portfolio.",
    "grain": "Portfolio",
    "visual": "bar",
    "sources": [
      "harbourline.vdr.portfolio_kpis"
    ]
  },
  "attempts": 1
}
```

Preview query the widget will run (as the viewer):

```sql
SELECT `Portfolio`, MEASURE(`Current Portfolio Value`) AS value FROM harbourline.semantic.stage3_kpis GROUP BY ALL ORDER BY 1
```

| Portfolio | value |
|---|---|
| Fund I | 3.99E9 |

_1 row(s)_
