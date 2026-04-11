# Vesta Simplification And Refactor Plan

Date: 2026-04-11

This plan is for the production Vesta app in `/home/empathetic/.openclaw/workspace`.

The goal is not a cosmetic cleanup or a broad rewrite. The goal is to reduce operational risk by consolidating duplicated business logic, separating production from demo/dev surfaces, making large React panels easier to change, and adding verification around each slice.

## Current Product Map

- Production API entrypoint: `/home/empathetic/.openclaw/workspace/api/app.py`.
- Active production API routers:
  - `auth.py`
  - `onboard.py`
  - `chat.py`
  - `pipeline.py`
  - `approvals.py`
  - `team_portal.py`
  - `broker_portal.py`
  - `admin.py`
  - `investor.py`
  - `notifications.py`
  - `push.py`
  - `skills.py`
- Demo API router:
  - `demo.py`, currently only registered when `VESTA_DEV_LOGIN` is enabled.
- Production React app:
  - `/home/empathetic/.openclaw/workspace/vesta-app/src`.
- Production deploy target:
  - API static bundle under `/home/empathetic/.openclaw/workspace/api/static`.
  - Public site asset copy under `/home/empathetic/html/vesta-tech`.

## Main Complexity Findings

- The highest-risk backend files are `chat.py`, `broker_portal.py`, and `pipeline.py`; each is carrying endpoint logic, business logic, SQL, and presentation-shaped payload construction in the same file.
- The largest frontend panels are `BrokerPortal.jsx`, `Pipeline.jsx`, `TeamPortal.jsx`, `Settings.jsx`, and `AdminPanel.jsx`; these behave like multiple screens inside one component.
- ROI and GCI logic is duplicated across `pipeline.py`, `broker_portal.py`, `investor.py`, and frontend display code. Stage probability and budget parsing should have one backend source of truth.
- The app already has `api/roi_assumptions.py`, but `pipeline.py` still uses local ROI constants instead of the shared assumptions module.
- Demo/dev code is mostly gated, but demo terminology and old phase-copy still appears in source comments and some production-facing Team/Pipeline copy.
- The database is production-small but schema-wide: 70 tables, 3 users, 2 brokerages, 2 teams, 138 leads, 46 lead scores, 70 email drafts, and 2 broker ROI snapshots at the time of this audit.
- Tests exist and cover several critical guardrails, but many are legacy/integration-style. Before refactors, we need targeted smoke checks for the exact surfaces we touch.

## Phase Roadmap

### P1: Stabilize The Map

P1 is low-risk cleanup and guardrail setup. It should not change product behavior.

- P1Q1: Product Surface Inventory
  - Produce a route map of production API endpoints, protected UI routes, and demo/dev-gated routes.
  - Confirm which routes are live, which are compatibility redirects, and which are intentionally demo-only.
  - Outcome: no code behavior changes, only a verified map.

- P1Q2: Visible Copy And Internal Label Cleanup
  - Remove remaining production-facing phase language such as `Phase 2`, `Phase 3`, and `P3` from Team/Pipeline UI.
  - Keep useful comments only when they help future maintenance.
  - Outcome: user-facing product no longer exposes internal build-phase language.

- P1Q3: Baseline Smoke Harness
  - Create a repeatable smoke checklist for Admin, Broker, Pipeline, Approvals, Investor, Auth, and Health.
  - Prefer a small script if feasible; otherwise document exact curl/API checks.
  - Outcome: every future quarter has a known pass/fail baseline before deploy.

- P1Q4: Complexity Budget And Refactor Boundaries
  - Mark no-go zones where behavior must not change yet: auth/session, admin privacy boundaries, FUB sync, approvals sending, and investor privacy.
  - Define target file-size/component boundaries for later extraction.
  - Outcome: refactor constraints are explicit before moving logic.

### P2: Centralize Business Rules

P2 reduces the risk of truthful numbers drifting between surfaces.

- P2Q1: Shared ROI Math Module
  - Move stage probabilities, budget parsing, commission assumptions, and lead GCI helpers into a shared backend ROI service/module.
  - Make `pipeline.py`, `broker_portal.py`, and `investor.py` read from the same assumptions and helper functions.
  - Outcome: one source of truth for stage probability, home-value fallback, and commission math.

- P2Q2: Revenue Protection Service
  - Extract `_revenue_protection` from `pipeline.py` into a shared module.
  - Keep payload shape stable so Pipeline UI does not change.
  - Outcome: lead-level revenue protection can be reused by Broker/Investor later without copy-paste.

- P2Q3: Broker Rollup Query Boundary
  - Extract broker distinct-FUB rollups and ROI snapshot calculations out of `broker_portal.py`.
  - Keep all endpoint response contracts unchanged.
  - Outcome: broker endpoints become thinner and less fragile.

- P2Q4: Investor Proof Builder Boundary
  - Extract investor snapshot/proof generation from `investor.py` into a focused builder.
  - Preserve aggregate-only privacy guarantees.
  - Outcome: investor proof logic is easier to test without touching share-link routing.

### P3: Split Large Frontend Panels

P3 makes the React product easier to modify without causing accidental UI regressions.

- P3Q1: Shared UI And Formatting Utilities
  - Extract common money/percent/date formatting, status badges, stat cards, and proof tiles used across Broker/Admin/Investor/Pipeline.
  - Avoid redesigning the product in this quarter.
  - Outcome: less repeated JSX and less inconsistent wording.

- P3Q2: Broker Portal Component Split
  - Split `BrokerPortal.jsx` into tab-level components and small broker-specific widgets.
  - Keep the data-loading contract stable first; do not redesign the tab layout yet.
  - Outcome: the largest investor/ROI surface becomes safer to iterate on.

- P3Q3: Pipeline Component Split
  - Split `Pipeline.jsx` into lead list, board view, lead detail, compose modal, revenue protection strip, and keyboard/search helpers.
  - Preserve all current lead actions.
  - Outcome: lead management can evolve without touching every pipeline concern in one file.

- P3Q4: Admin, Team, And Settings Split
  - Split `AdminPanel.jsx`, `TeamPortal.jsx`, and `Settings.jsx` by functional section.
  - Settings should be especially careful because it touches credentials, push, comms, and skills.
  - Outcome: admin/team/settings changes become lower-risk and easier to review.

### P4: Separate Production, Demo, And Automation

P4 reduces confusion about what belongs to the live product versus old demos and background jobs.

- P4Q1: Demo/Dev Route Isolation Review
  - Confirm `demo.py`, `/auth/dev-login`, and `/auth/demo-switch` are unreachable in production when `VESTA_DEV_LOGIN` is off.
  - Add or update tests if needed.
  - Outcome: demo tooling remains available only when intentionally enabled.

- P4Q2: Automation Script Inventory
  - Categorize root-level scripts as active, manual utility, legacy/archive, or unknown.
  - Do not delete first; create an inventory and only archive after verification.
  - Outcome: old automation files stop being a mental tax without breaking background jobs.

- P4Q3: Database Startup/Migration Cleanup
  - Move best-effort `ALTER TABLE` startup work in `api/app.py` toward an explicit migration/bootstrap path.
  - Keep WAL/performance pragmas in startup if still appropriate.
  - Outcome: app startup becomes less surprising and schema changes are easier to audit.

- P4Q4: Active Route And Link Audit
  - Re-run clickable/link audit after refactors: SPA routes, compatibility redirects, investor share links, demo links, login/onboard flows, and public assets.
  - Outcome: no broken links or stale route confusion after cleanup.

### P5: Verification And Operational Hardening

P5 is the final tightening pass after code movement.

- P5Q1: Contract Tests For Core Payloads
  - Add focused tests for Admin system, Broker overview/revenue/health, Pipeline stats/detail, Investor snapshot/share, and Approvals visibility.
  - Outcome: future refactors can prove they did not alter critical payloads accidentally.

- P5Q2: Privacy Regression Tests
  - Add recursive key/content checks around admin and investor endpoints.
  - Ensure system admin still cannot see tenant client records.
  - Outcome: privacy guardrails are automated, not just manually checked.

- P5Q3: Health And Background Job Ownership
  - Make system health identify which background jobs are expected, optional, degraded, or disabled.
  - Outcome: Admin health becomes more actionable and less ambiguous.

- P5Q4: Final Simplification Closeout
  - Run lint, build, deploy, API restart, health smoke, endpoint smoke, route/link smoke, and privacy smoke.
  - Update working memory with final active files, active routes, and remaining known risks.
  - Outcome: simplification/refactor track can be closed cleanly.

## Recommended Starting Point

Start with P1Q1 and P1Q2.

Reason: they reduce confusion without moving business logic. P2 should wait until the route map and smoke checks are stable, because centralizing ROI math is valuable but can affect investor-facing numbers if rushed.

