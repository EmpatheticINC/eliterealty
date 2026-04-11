# Vesta P2 Business Rules Plan

Date: 2026-04-11

Scope: P2 of the simplification/refactor track.

P2 centralizes ROI and business-rule logic while preserving production behavior. This phase must make the numbers easier to trust without changing the numbers, role boundaries, endpoint payload contracts, or investor privacy posture.

## P2 Principle

Make the math boring.

Every P2 quarter should reduce duplicate business logic, but the live Admin, Broker, Pipeline, and Investor surfaces should continue returning the same shapes and effectively the same values unless a later product decision explicitly changes an assumption.

## Current Business-Rule Surfaces

- `/home/empathetic/.openclaw/workspace/api/roi_assumptions.py`
  - Already stores shared assumption values:
  - `commission_rate`
  - `default_home_value`
  - `quarterly_gci_target`
  - `annual_gci_target`
  - `loaded_hourly_cost`
- `/home/empathetic/.openclaw/workspace/api/routers/pipeline.py`
  - Still has local `_STAGE_PROB`, `_COMMISSION_RATE`, `_DEFAULT_HOME_VALUE`, `_parse_budget`, and `_revenue_protection`.
  - Uses revenue protection in lead list, lead detail, top opportunities, and pipeline stats.
- `/home/empathetic/.openclaw/workspace/api/routers/broker_portal.py`
  - Has `_STAGE_PROB`, `_parse_budget`, `_lead_gci`, broker revenue calculations, broker ROI snapshots, ROI history, and broker pipeline value.
  - Already reads assumption values from `get_roi_assumptions(conn)`.
- `/home/empathetic/.openclaw/workspace/api/routers/investor.py`
  - Builds aggregate-only investor snapshots from `broker_roi_snapshots`.
  - Adds ROI proof points, automation value, approval throughput, CMA job counts, and public share-link snapshot output.

## P2Q1: Shared ROI Math Helper

Goal: one backend source of truth for stage probability, budget parsing, and lead GCI math.

Implementation scope:

- Add or extend a shared backend module near `api/roi_assumptions.py`.
- Move pure math helpers only:
  - stage probability lookup
  - budget parsing with configured fallback home value
  - full commission/GCI estimate
  - weighted GCI estimate
- Convert the lowest-risk caller first, preferably `pipeline.py` revenue-protection math, while preserving its response keys.
- Keep `get_roi_assumptions(conn)` as the source for configurable values where a DB connection is already available.

Do not change:

- ROI assumption default values.
- Broker revenue endpoint response shape.
- Pipeline lead/list/detail response shape.
- Investor snapshot/proof response shape.
- FUB ownership, FUB dedupe, lead scoping, or CRM sync.

Verification:

- Run `python3 scripts/vesta_smoke.py` before implementation.
- Run Python compile checks for touched backend files.
- Run `python3 scripts/vesta_smoke.py` after implementation.
- If only backend source changes, no frontend build/deploy is required.

Done when:

- `pipeline.py` no longer owns separate ROI constants for revenue protection.
- The smoke harness passes with `26 passed, 0 failed`.
- Memory is updated and the commit is pushed to `track-3`.

## P2Q2: Revenue Protection Service Boundary

Goal: make lead-level revenue protection reusable without dragging the full Pipeline router along with it.

Implementation scope:

- Extract `_revenue_protection` from `pipeline.py` into a focused service/helper module.
- Keep `_days_since` behavior stable or move it with the service if needed.
- Preserve the exact `revenue_protection` payload shape:
  - `estimated_home_value`
  - `commission_rate_pct`
  - `stage_probability_pct`
  - `estimated_gci`
  - `weighted_gci`
  - `revenue_at_risk`
  - `sla_status`
  - `sla_label`
  - `days_since_contact`
  - `recommended_action`
- Keep the Pipeline router responsible for auth, DB scoping, and endpoint shape.

Do not change:

- SLA thresholds for hot/warm leads.
- Lead scoring thresholds.
- Pipeline filters, sorting, or scoping.
- Email approval behavior.

Verification:

- Run smoke before and after.
- Compile touched backend modules.
- Add a small pure-helper test only if the repo’s test shape makes that low risk.

Done when:

- Pipeline uses a reusable revenue-protection helper.
- Existing Pipeline/Broker smoke endpoints still pass.
- No frontend deploy is required unless an existing payload contract accidentally changes, which should be avoided.

## P2Q3: Broker Revenue And Snapshot Boundary

Goal: thin `broker_portal.py` around broker ROI rollups while keeping broker and investor numbers stable.

Implementation scope:

- Extract broker revenue/snapshot construction behind a service or helper boundary.
- Keep the router endpoint response contracts unchanged for:
  - `/api/broker/revenue`
  - `/api/broker/roi_history`
  - `/api/broker/pipeline_value`
  - `/api/broker/overview` if it depends on the same rollup data
- Keep distinct-FUB logic intact.
- Keep snapshot upsert/history table behavior intact unless a separate migration phase is explicitly started.

Do not change:

- Deduping rules while John/Jane share the same FUB account.
- `broker_roi_snapshots` schema or write behavior.
- Raw lead row counts versus distinct lead counts.
- Team/agent proportional allocation logic in the same slice as helper extraction.
- Investor snapshot behavior in the same slice.

Verification:

- Run smoke before and after.
- Compile touched backend modules.
- Compare representative broker revenue response keys before/after if feasible.

Done when:

- `broker_portal.py` has less embedded ROI rollup logic.
- Broker revenue, history, health, and pipeline value smoke checks pass.
- Investor snapshot smoke still passes because it relies on broker snapshots.

## P2Q4: Investor Proof Builder Boundary

Goal: make investor aggregate proof easier to test while preserving privacy and public share-link behavior.

Implementation scope:

- Extract `_build_investor_snapshot` internals into a focused aggregate proof builder.
- Keep `investor.py` router responsible for auth, token validation, CSV response, and route wiring.
- Preserve the aggregate-only response structure:
  - `summary`
  - `proof`
  - `brokerages`
  - `history`
  - `assumptions`
  - `privacy`
- Keep public share-token routes behavior-stable.

Do not change:

- Share-token creation, expiration, revocation, or token lookup.
- CSV column meanings.
- Admin privacy boundaries.
- Investor surfaces exposing only aggregate broker ROI snapshots.
- Any client-level data visibility.

Verification:

- Run smoke before and after.
- Compile touched backend modules.
- Run or extend privacy checks if practical.
- Confirm investor snapshot still avoids forbidden client-style keys.

Done when:

- Investor proof construction is behind a builder boundary.
- Admin and investor snapshot smoke checks pass.
- Public share behavior is untouched except for using the extracted builder internally.

## P2 Exit Criteria

- Shared ROI math no longer has duplicate stage probability or budget parsing logic in both Pipeline and Broker surfaces.
- Revenue protection is reusable outside the Pipeline router.
- Broker ROI rollup/snapshot code is behind a boundary, with endpoint shapes unchanged.
- Investor proof construction is behind a boundary, aggregate-only, and smoke verified.
- `python3 scripts/vesta_smoke.py` passes after each quarter.
- `WORKING_MEMORY.md` is updated after each quarter.
- Each quarter is committed and pushed to `track-3`.

## Recommended First Slice

Start with P2Q1 and keep it very small:

- Add shared pure ROI helpers.
- Convert Pipeline revenue-protection math to use the helper.
- Do not convert Broker revenue in the same first commit unless the diff stays extremely small.

Reason: Pipeline has local constants that clearly duplicate the shared assumption values. Moving that first gives us immediate simplification while avoiding broker snapshot/dedup risk.
