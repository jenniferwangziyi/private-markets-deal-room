# Harbourline Capital · AI deal room on Databricks

**Industry:** private-markets investment (fund manager). **Customer problem:** deal teams lose days per deal chasing,
classifying and cross-checking due-diligence documents across email, spreadsheets and data rooms; stage gates stall on
missing items and approvals; portfolio KPIs are rebuilt (and disagree) for every report; AI is blocked by governance.

**Outcome (planning assumptions, see `deck/`):** stage-gate cycle time ~10 → ~4 days, document triage 15 → 3 min/document,
100 % of extracted figures cross-checked on arrival, quarterly pack 3 weeks → 3 days — ≈ 960 analyst hours a year.

_Harbourline Capital is fictional. All data is synthetic (`data/gen_dealroom.py`) or public (FRED market series)._

## The integrated data journey

| Stage | Built with | Code | Execution evidence (text) |
|---|---|---|---|
| **1 · Lakeflow — ingest** | Lakeflow Jobs: Auto Loader over the deal-room landing-zone volume (35 synthetic PDFs, portal uploads); daily job pulling public FRED + central-bank series | `jobs/dealroom_ingest.py`, `jobs/external_factors.py`, `databricks.yml`, `data/gen_dealroom.py`, `scripts/load_data.sh` | `evidence/01_lakeflow_ingest.md`, `evidence/logs/01_*`–`05_*` |
| **2 · Unity Catalog — govern** | One role-scope table + `scope_match` row-filter function + tag-based ABAC policy `portfolio_rows`; file row filter for the external GP; classification tags; metric views + glossary; lineage | `sql/20_governance.sql`, `sql/40_metric_views.sql`, `sql/60_app_grants.sql` | `evidence/02_unity_catalog_governance.md` (same query run as 3 roles), `evidence/logs/02*` |
| **3 · Lakebase — operational serving** | Lakebase Postgres (Autoscaling) project `harbourline`: app state (`hl_app`: gates, approvals, threads, proposals) + **synced table** `serving.external_factors` (Delta → Postgres, triggered/CDF) read by the app's market board | `app/backend/db.py`, `app/backend/schema.sql`, `app/backend/main.py` (`/api/factors`) | `evidence/03_lakebase_serving.md`, `evidence/logs/06_lakebase_synced_table.log` |
| **4 · GenAI — make it intelligent** | `ai_parse_document → ai_classify → ai_extract` (with confidence; < 0.80 routed to a person); cross-document figure-mismatch alert; `ai_query` market-risk note; Widget Builder agent (open-weight `databricks-gpt-oss-120b`) that only builds on certified metric views | `sql/35_ai_extract.sql`, `sql/32_deal_status.sql`, `src/harbourline/ai/*`, `ai/prompts/widget_builder.txt` | `evidence/04_genai_intelligence.md` (real model output) |
| **5 · Genie Agent — natural language** | Genie agent *Harbourline · Deal Room Analyst* on the metric views + glossary (EN / 繁 / 简) | `ai/genie/build.py` | `evidence/05_genie_agent.md` (questions → SQL → rows → answer, per role) |
| **6 · Databricks App — surface it** | `harbourline-dealroom` (FastAPI + JS): my deals, deal-room stage gate, AI file drawer, market board + AI risk note, embedded AI/BI dashboard, Widget Builder preview → approval → publish, GP portal. Every read runs **as the signed-in user** (on-behalf-of), so Unity Catalog decides what each role sees | `app/`, `ai/dashboards/build.py`, `scripts/deploy_app.sh` | `evidence/06_databricks_app.md` |

Business deck: `deck/harbourline_deal_room.md` (text) / `deck/harbourline_deal_room.pdf`.

## Personas (account groups, used with "switch role")

| Role | Persona | Sees |
|---|---|---|
| `role-business-user` | Fund I owner / deal-team lead | Fund I only |
| `role-approver` | Head of Investment / IC | all portfolios; approves stage gates and widgets |
| `role-it-ai-owner` | IT & AI owner | audit trail |
| `role-external-gp` | Solace Grid's GP | only its own uploads in its deal room |

## Run it

```bash
uv run --extra dev pytest -q                                   # unit tests
for f in 00_catalog 10_tables; do uv run python scripts/run_sql.py sql/$f.sql; done
bash scripts/load_data.sh                                       # synthetic raw data -> UC volumes
for f in 30_load 32_deal_status 20_governance 40_metric_views 50_ai 60_app_grants; do uv run python scripts/run_sql.py sql/$f.sql; done
uv run python scripts/render_sql.py && databricks bundle deploy && databricks bundle run hl_dealroom_ingest && databricks bundle run hl_external_factors
uv run --extra ai python ai/genie/build.py && uv run --extra ai python ai/dashboards/build.py
bash scripts/deploy_app.sh
uv run --extra ai --with "psycopg[binary]" python scripts/collect_evidence.py   # regenerates evidence/*.md
```

Configuration: `config/demo.yml` (workspace profile, warehouse, catalog, roles, app service principal, model).
