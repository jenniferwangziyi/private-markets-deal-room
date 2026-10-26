# Lakeflow — ingest raw (synthetic) data
_Captured 2026-10-26 06:33 UTC from workspace `hunter` (catalog `harbourline`) by `scripts/collect_evidence.py`._

## Job runs (Lakeflow Jobs)

| job | last run | state | result | duration (s) |
|---|---|---|---|---|
| [dev jennifer_wang] hl-external-factors | 733238902942440 | TERMINATED | SUCCESS | 60 |
| [dev jennifer_wang] hl-dealroom-ingest | 331364740209467 | TERMINATED | SUCCESS | 223 |

## Raw files landed in the Unity Catalog volume and registered by Auto Loader

| deal_room | stage | source | status | files |
|---|---|---|---|---|
| Kestrel Robotics | 1 | internal | Classified | 4 |
| Kestrel Robotics | 1 | internal | Needs review | 2 |
| Kestrel Robotics | 2 | internal | Classified | 7 |
| Kestrel Robotics | 2 | internal | Needs review | 1 |
| Kestrel Robotics | 3 | internal | Classified | 4 |
| Kestrel Robotics | 3 | internal | Needs review | 3 |
| Solace Grid Energy | 1 | internal | Classified | 5 |
| Solace Grid Energy | 1 | internal | Needs review | 1 |

_8 row(s)_

## Row counts of every table built from the raw data

| table_name | rows |
|---|---|
| file_register | 27 |
| investments | 7 |
| portfolio_kpis | 24 |
| checklist_items | 25 |
| reporting_calendar | 28 |
| risks | 5 |
| alerts | 5 |
| external_factors | 14 |
| file_content | 27 |
| doc_parsed | 27 |
| doc_extracts | 85 |

_11 row(s)_

## External investment factors (daily Lakeflow job: public FRED feed + seed series)

| series | label | value | prev_value | unit | observed_at | source |
|---|---|---|---|---|---|---|
| BOE_BANK_RATE | BoE Bank Rate | 3.75 | 4.0 | pct | 2026-09-18 | https://www.bankofengland.co.uk |
| DEXHKUS | USD/HKD | 7.8478 | 7.847 | fx | 2026-10-16 | https://fred.stlouisfed.org/series/DEXHKUS |
| DFF | Fed funds effective rate | 3.88 | 3.88 | pct | 2026-10-22 | https://fred.stlouisfed.org/series/DFF |
| DGS10 | US Treasury 10Y yield | 4.96 | 5.13 | pct | 2026-10-22 | https://fred.stlouisfed.org/series/DGS10 |
| DGS2 | US Treasury 2Y yield | 4.65 | 4.81 | pct | 2026-10-22 | https://fred.stlouisfed.org/series/DGS2 |
| ECB_DEPOSIT | ECB deposit rate | 2.0 | 2.0 | pct | 2026-09-11 | https://www.ecb.europa.eu |
| HIBOR_3M | 3M HIBOR | 3.85 | 3.92 | pct | 2026-10-10 | https://www.hkab.org.hk |
| HKMA_BASE_RATE | HKMA Base Rate | 4.25 | 4.5 | pct | 2026-10-10 | https://www.hkma.gov.hk |
| HSI | Hang Seng Index | 26150.0 | 25890.0 | index | 2026-10-10 | https://www.hsi.com.hk |
| SP500 | S&P 500 | 7757.17 | 7712.57 | index | 2026-10-21 | https://fred.stlouisfed.org/series/SP500 |
| VIXCLS | VIX | 19.03 | 16.68 | index | 2026-10-22 | https://fred.stlouisfed.org/series/VIXCLS |
| DCOILBRENTEU | Brent crude | 115.22 | 118.82 | usd_bbl | 2026-10-20 | https://fred.stlouisfed.org/series/DCOILBRENTEU |
| DEXCHUS | USD/CNY | 6.6861 | 6.6909 | fx | 2026-10-16 | https://fred.stlouisfed.org/series/DEXCHUS |
| PBOC_LPR_1Y | PBOC 1Y LPR | 3.0 | 3.1 | pct | 2026-09-22 | http://www.pbc.gov.cn |

_14 row(s)_
