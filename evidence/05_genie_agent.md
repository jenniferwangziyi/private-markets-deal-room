# Genie Agent — natural-language access (as each role)
_Captured 2026-10-26 06:58 UTC from workspace `hunter` (catalog `harbourline`) by `scripts/collect_evidence.py`._

## hunter-business: How many companies do I have access to?

**Q (hunter-business):** How many companies do I have access to?

**Status:** COMPLETED

```sql
SELECT COUNT(DISTINCT `name`) AS `company_count`
FROM `harbourline`.`vdr`.`investments`
WHERE `name` IS NOT NULL
```

**Rows:** `[["6"]]`

**Answer:** You currently have access to **6 companies** based on the distinct non-null company names in `harbourline.vdr.investments`. Source: harbourline.vdr.investments

## hunter-business: How did gross MOIC change from 2026-Q1 to 2026-Q2?

**Q (hunter-business):** How did gross MOIC change from 2026-Q1 to 2026-Q2?

**Status:** COMPLETED

```sql
WITH kpi AS (
  SELECT
    `Period`,
    MEASURE(`Gross MOIC`) AS `gross_moic`
  FROM `harbourline`.`semantic`.`stage3_kpis`
  WHERE `Period` IN ('2026-Q1', '2026-Q2')
    AND `Period` IS NOT NULL
  GROUP BY ALL
), pivoted AS (
  SELECT
    MAX(CASE WHEN `Period` = '2026-Q1' THEN `gross_moic` END) AS `gross_moic_2026_q1`,
    MAX(CASE WHEN `Period` = '2026-Q2' THEN `gross_moic` END) AS `gross_moic_2026_q2`
  FROM kpi
)
SELECT
  `gross_moic_2026_q1`,
  `gross_moic_2026_q2`,
  `gross_moic_2026_q2` - `gross_moic_2026_q1` AS `absolute_change`
FROM pivoted
```

**Rows:** `[["1.3622", "1.39", "0.027799999999999825"]]`

**Answer:** Gross MOIC increased from **1.3622** in **2026-Q1** to **1.39** in **2026-Q2**, a change of **0.0278**. Across the 2 periods in `stage3_kpis`, the movement was **up** quarter over quarter. Source: stage3_kpis

## hunter-business: Fund I 的總投資額是多少？

**Q (hunter-business):** Fund I 的總投資額是多少？

**Status:** COMPLETED

```sql
SELECT MEASURE(`Total Invested Capital`) AS `Total Invested Capital`
FROM `harbourline`.`semantic`.`stage3_kpis`
WHERE `Portfolio` IS NOT NULL
  AND `Portfolio` ILIKE '%Fund I%'
  AND `Period` = '2026-Q2'
GROUP BY ALL
```

**Rows:** `[["2.86E9"]]`

**Answer:** Fund I 的**總投資額**為 **USD 2,860,000,000**，期間為 **2026-Q2**。這筆結果只有 **1 筆**，顯示在目前資料中，Fund I 對應的總投資額為 **USD 2,860,000,000**。 Source: stage3_kpis

## hunter-business: How is Total Invested Capital defined?

**Q (hunter-business):** How is Total Invested Capital defined?

**Status:** COMPLETED

```sql
SELECT `term`, `definition`
FROM `harbourline`.`semantic`.`business_glossary`
WHERE `term` ILIKE '%Total Invested Capital%'
  AND `term` IS NOT NULL
```

**Rows:** `[["Total Invested Capital", "Cumulative capital Harbourline has deployed into a portfolios Stage 3 companies, USD, at the latest reporting period. Certified measure `Total Invested Capital` in semantic.stage3_kpis; used by the Stage 3 dashboard tile, Genie and the Widget Builder"]]`

**Answer:** **Total Invested Capital** is defined in `business_glossary` as **cumulative capital Harbourline has deployed into a portfolio’s Stage 3 companies, in USD, at the latest reporting period**. The `business_glossary` entry also states that **Total Invested Capital** is the certified measure in `semantic.stage3_kpis` and is used by the Stage 3 dashboard tile, Genie, and the Widget Builder.

Source: business_glossary

## hunter-approver: How many companies do I have access to?

**Q (hunter-approver):** How many companies do I have access to?

**Status:** COMPLETED

```sql
SELECT COUNT(DISTINCT `name`) AS `company_count`
FROM `harbourline`.`vdr`.`investments`
WHERE `name` IS NOT NULL
```

**Rows:** `[["7"]]`

**Answer:** You currently have access to **7 companies** based on the count of distinct non-null company names in `harbourline.vdr.investments`. Source: harbourline.vdr.investments
