# Harbourline Capital · From document chase to investment decision

**An AI-assisted, governed deal room on the Databricks Data Intelligence Platform**

Private-markets investment · Deal origination, due diligence and post-investment monitoring

_Harbourline Capital is a fictional Hong Kong private-markets investor; all data in this build is synthetic._

---

## The outcome in one slide

| | Today | With the AI deal room |
|---|---|---|
| **Stage-gate cycle time** (Stage 1 → 2) | ~10 business days | **~4 days (-60 %)** |
| **Analyst time on document triage** | ~15 min / document | **~3 min / document (-80 %)** |
| **Cross-document figure checks** | sampled, late (in IC pack prep) | **100 % of extracted figures, on arrival** |
| **Quarterly portfolio pack** | ~3 weeks of consolidation | **~3 days, one certified number** |
| **External-party document exchange** | email attachments | **governed portal — the GP sees only its own uploads** |

**≈ 960 analyst hours a year back (≈ 0.5 FTE, ≈ US$ 90k)** and investment-committee decisions about **6 days sooner per deal** — on one governed platform, no extra BI, workflow or AI tools.

_Baseline and targets are planning assumptions for a fund house running ~40 active deals a year with ~60 diligence documents each (see "How we sized it")._

---

## Why this matters — two owners, one platform

**Executive sponsor — COO / Head of Investment**

- Faster, better-evidenced IC decisions: no stage advances until every required document **and** the named approval are in.
- Lower operational and conduct risk: one access model for people, dashboards, AI and outside parties; every action and AI call audited.
- Cost you can see: one platform bill instead of a document tool + BI tool + AI tool + workflow tool.

**Domain owner — Deal-team lead / Investment operations**

- The AI files, labels and reads every document, with a confidence score — the team reviews exceptions, not everything.
- Live completion %, gaps and risk alerts per deal room; no spreadsheet tracker.
- Self-service answers in English or Chinese (Genie) and AI-built report widgets on certified metrics — no ticket to the data team.

---

## The problem today

1. **Documents arrive from many channels** — internal teams, the GP, email — and are classified and checked by hand.
2. **Completeness and approvals live in spreadsheets and inboxes**; nobody can see which deal is blocked and why.
3. **Figures disagree across documents** (e.g. FY revenue 5.4 vs 6.1 USD m) and are caught late — in IC pack preparation.
4. **KPIs are rebuilt for every report**; the dashboard, the board pack and ad-hoc answers do not always match.
5. **AI is blocked by governance**: who may see which portfolio, and what may an AI model read?

---

## How we sized it (assumptions, to be validated in the pilot)

| Driver | Assumption | Annual effect |
|---|---|---|
| Deal volume | 40 active deals / year × 60 diligence documents | 2,400 documents |
| Document triage | 15 → 3 min / document (AI classifies + extracts; humans review < 0.8 confidence) | **≈ 480 h saved** |
| Quarterly monitoring pack | 120 → 0 h of consolidation per quarter (certified metric views feed dashboard, Genie, reports) | **≈ 480 h saved** |
| Stage-gate wait | 10 → 4 business days (live gaps, routed approvals, gate due-date alerts) | **≈ 6 days faster per deal** |
| Loaded analyst cost | US$ 95 / hour | **≈ US$ 90k / year** |
| Platform run cost (pilot scope) | serverless, pay per use; one shared SQL warehouse, scale-to-zero Lakebase | measured live in system tables |

---

## The solution — one integrated data journey

| Stage | What runs | What the business gets |
|---|---|---|
| **1 · Lakeflow — ingest** | Auto Loader picks up every deal-room PDF from the landing zone (and optionally SharePoint); a daily Lakeflow job pulls public market factors (FRED + central-bank series) | Every document and market signal arrives without manual uploads |
| **2 · Unity Catalog — govern** | One role-scope table + one row-filter function + a tag-based ABAC policy; classification tags; lineage and audit | Define access once — the same rule protects the app, dashboards, Genie, AI and the GP portal |
| **3 · Lakebase — operational serving** | Postgres for the app's live state (gates, approvals, threads, proposals) + a synced table serving market factors from Delta | Millisecond reads and transactional approvals inside the app |
| **4 · GenAI — make it intelligent** | `ai_parse_document → ai_classify → ai_extract` with confidence; cross-document mismatch check; `ai_query` market-risk note; Widget Builder agent on an open-weight model | Documents filed, labelled and read automatically; risks surfaced with reasons |
| **5 · Genie Agent — ask in natural language** | Genie on certified metric views + a business glossary (EN / 繁 / 简) | "How did gross MOIC change this quarter?" — answered from the same definition as the dashboard |
| **6 · Databricks App — surface it** | The Harbourline Deal Room app: my deals, deal-room gate, AI file drawer, market board, Stage 3 dashboard, widget preview → approval, GP portal | One place for the deal team, the Head of Investment and the outside GP |

---

## A day in the deal room (the demo storyline)

1. **Deal-team lead** opens *My deals* → *Solace Grid Energy*: 6 of 7 Stage 1 items done (85.7 %), locked on the Head of Investment approval.
2. Opens a file: the AI says *IC overview, 0.85* and *Confidential, 0.85* — auto-filed; a 0.78 score went to review.
3. **Head of Investment** sees **one more deal** than the Fund I owner (7 vs 6), approves, advances to Stage 2. The diligence pack lands; Auto Loader + AI file it; a **figure mismatch** alert appears.
4. The **market board** (served from Lakebase) and an **AI risk note** flag what moved for this deal.
5. On the Stage 3 dashboard and in **Genie**, the Fund I owner sees **5 companies**, the Head of Investment **6** — same dashboard, one policy. Genie answers *gross MOIC 1.36 → 1.39* with the certified measure.
6. The Fund I owner asks the **Widget Builder** for a KPI tile → live preview → the Head of Investment approves → it is published to the official dashboard.
7. The **external GP** logs in: sees **0** Harbourline documents, uploads its pack, sees only its own files.

---

## Trust by design

- **Define access once, apply everywhere** — row filters on the portfolio tag decide what the app, AI/BI dashboard, Genie and the agent see. _Evidence: the same query returns 6 companies for the Fund I owner, 7 for the Head of Investment, and 0 Harbourline files for the GP._
- **AI is advisory** — confidence scores on every classification and extraction; under 0.80 a person decides; nothing is approved by AI.
- **One audit trail** — every approval (person + role) in Lakebase; every query in system tables; lineage from file to dashboard tile.
- **Open and portable** — Delta tables, open-weight model, standard Postgres; no proprietary lock-in.

---

## Architecture

```
 Raw sources                    Lakeflow                 Unity Catalog (governed)                        Serve & act
 ────────────                   ────────                 ────────────────────────                        ───────────
 Deal-room PDFs (landing zone)  Auto Loader job   ──►    vdr: file_register, file_content,               Databricks App (FastAPI)
 GP portal uploads              (hl-dealroom-ingest)      doc_parsed, doc_extracts, checklist,      ──►   · deal rooms, gate, AI drawer
 Public market data (FRED, CB)  Daily factors job        investments, KPIs, external_factors              · market board  ◄── Lakebase
 Synthetic fund / KPI tables    (hl-external-factors)    semantic: metric views + glossary                 · Stage 3 dashboard + widget preview
                                                         governance: role_scope, scope_match, ABAC         · GP portal
                                AI Functions on SQL      ai_parse_document · ai_classify ·                Genie Agent (metric views)
                                warehouse                ai_extract · ai_query                            AI/BI dashboards (viewer credentials)
                                                         Lakebase: app state (hl_app) + synced table (serving.external_factors)
```

---

## Rollout plan

| Weeks | Scope | Success criteria |
|---|---|---|
| 1–2 | Connect the real deal-room library and two live deals; map the 4-level classification | ≥ 90 % of documents auto-filed at ≥ 0.80 confidence |
| 3–4 | Stage gates + approvals for one fund; Genie for the deal team | Stage 1 → 2 in ≤ 5 days on pilot deals; zero manual tracker |
| 5–6 | Quarterly monitoring pack from certified metrics; GP portal for one GP | Pack in ≤ 3 days; dashboard = Genie = report to the cent |

---

## Next steps

1. Agree the KPI baseline with the deal team (cycle time, triage minutes, pack effort) — two weeks of measurement.
2. Nominate the executive sponsor and a deal-team lead as domain owner.
3. Start the 6-week pilot on two live deals.
