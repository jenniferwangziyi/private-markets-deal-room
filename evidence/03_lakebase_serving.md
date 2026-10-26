# Lakebase — operational serving
_Captured 2026-10-26 06:34 UTC from workspace `hunter` (catalog `harbourline`) by `scripts/collect_evidence.py`._

## Synced table Delta → Lakebase (status)

```json
{
  "name": "synced_tables/harbourline_serving.serving.external_factors",
  "synced_table_id": "harbourline_serving.serving.external_factors",
  "status": {
    "detailed_state": "SYNCED_TABLE_ONLINE_NO_PENDING_UPDATE",
    "last_sync": {
      "delta_table_sync_info": {
        "delta_commit_time": "2026-10-26T06:26:00.933Z",
        "delta_commit_version": 2
      },
      "sync_end_time": "2026-10-26T06:27:09.848617Z",
      "sync_start_time": "2026-10-26T06:26:51.559398Z"
    },
    "message": "Synced table creation succeeded using Delta Live Tables: https://adb-3311028655009738.18.azuredatabricks.net#joblist/pipelines/0fee06e7-98e0-467d-8b9b-6781c86c85b6/updates/c8983509-7b48-4f64-a79a-74ba8fb88c7e.",
    "pipeline_id": "0fee06e7-98e0-467d-8b9b-6781c86c85b6",
    "project": "projects/harbourline",
    "unity_catalog_provisioning_state": "ACTIVE"
  },
  "spec": null
}
```

## The app's market-factor board reads Lakebase (serving.external_factors)

| series | label | value | prev_value | unit | observed_at |
|---|---|---|---|---|---|
| BOE_BANK_RATE | BoE Bank Rate | 3.75 | 4.0 | pct | 2026-09-18 |
| DCOILBRENTEU | Brent crude | 115.22 | 118.82 | usd_bbl | 2026-10-20 |
| DEXCHUS | USD/CNY | 6.6861 | 6.6909 | fx | 2026-10-16 |
| DEXHKUS | USD/HKD | 7.8478 | 7.847 | fx | 2026-10-16 |
| DFF | Fed funds effective rate | 3.88 | 3.88 | pct | 2026-10-22 |
| DGS10 | US Treasury 10Y yield | 4.96 | 5.13 | pct | 2026-10-22 |
| DGS2 | US Treasury 2Y yield | 4.65 | 4.81 | pct | 2026-10-22 |
| ECB_DEPOSIT | ECB deposit rate | 2.0 | 2.0 | pct | 2026-09-11 |
| HIBOR_3M | 3M HIBOR | 3.85 | 3.92 | pct | 2026-10-10 |
| HKMA_BASE_RATE | HKMA Base Rate | 4.25 | 4.5 | pct | 2026-10-10 |
| HSI | Hang Seng Index | 26150.0 | 25890.0 | index | 2026-10-10 |
| PBOC_LPR_1Y | PBOC 1Y LPR | 3.0 | 3.1 | pct | 2026-09-22 |
| SP500 | S&P 500 | 7757.17 | 7712.57 | index | 2026-10-21 |
| VIXCLS | VIX | 19.03 | 16.68 | index | 2026-10-22 |

_14 row(s), 390 ms from Postgres_

## App operational state in Lakebase (schema hl_app, owned by the app's service principal)

| t | count |
|---|---|
| deal_stage | 1 |
| stage_items | 6 |
| approvals | 0 |
| widget_proposals | 0 |
| threads | 1 |

_5 row(s), 186 ms from Postgres_

## Deal-room gate state served to the app

| investment | stage | item | status | run_as |
|---|---|---|---|---|
| Solace Grid Energy | 1 | Fund Overview - Pitch deck | Approved | role-approver |
| Solace Grid Energy | 1 | High-level Track Record | Approved | role-approver |
| Solace Grid Energy | 1 | IC overview | Approved | role-approver |
| Solace Grid Energy | 1 | NDA | Approved | role-approver |
| Solace Grid Energy | 1 | Organization chart | Approved | role-approver |
| Solace Grid Energy | 1 | PPM - Key Terms Summary (Draft) | Approved | role-approver |

_6 row(s), 209 ms from Postgres_
