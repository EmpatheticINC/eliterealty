# Vesta Refactor Boundaries

Date: 2026-04-11

Scope: P1Q4 complexity budget and refactor constraints for the production Vesta app.

This file defines what can change, what must not change yet, and what must be verified before moving from P1 into P2. It exists to keep simplification/refactor work surgical.

## Refactor Principle

Refactor by preserving behavior first, then simplifying structure.

The next phases should reduce duplicated logic and large-file risk, but they should not introduce product redesigns, role-policy changes, data cleanup, or new investor-facing math without a clear verification gate.

## Absolute No-Go Zones Before P2 Completion

- Do not change OAuth, cookie, JWT, or session lifetime behavior unless the user explicitly asks for an auth/security task.
- Do not change `system_admin` access boundaries or allow system admin to see tenant/client pipeline records.
- Do not change investor privacy posture: investor surfaces must remain aggregate-only and must not expose client names, phone numbers, addresses, email bodies, recipient emails, CMA file URLs, or lead-level records.
- Do not change approval send behavior: approval-gated emails must not become direct-send flows.
- Do not delete or deduplicate live CRM/FUB lead rows while John/Jane are intentionally pointed at the same FUB account.
- Do not change FUB sync ownership/matching behavior in the same slice as ROI math extraction.
- Do not delete demo/dev code just because it contains the word `demo`; demo API routing is intentionally gated and public demo behavior must be evaluated separately.
- Do not edit generated bundles in `api/static/assets` or `/home/empathetic/html/vesta-tech/assets` manually; update source and deploy.
- Do not restart or modify `vesta-platform.service`; production uses `vesta-api.service`.
- Do not run destructive git or database commands unless the user explicitly approves them.

## High-Risk Files

These files can be refactored, but only in small scoped quarters with smoke checks before and after:

- `/home/empathetic/.openclaw/workspace/api/routers/chat.py`
- `/home/empathetic/.openclaw/workspace/api/routers/broker_portal.py`
- `/home/empathetic/.openclaw/workspace/api/routers/pipeline.py`
- `/home/empathetic/.openclaw/workspace/api/routers/investor.py`
- `/home/empathetic/.openclaw/workspace/api/routers/admin.py`
- `/home/empathetic/.openclaw/workspace/api/routers/approvals.py`
- `/home/empathetic/.openclaw/workspace/api/fub_sync.py`
- `/home/empathetic/.openclaw/workspace/auth/session.py`
- `/home/empathetic/.openclaw/workspace/api/deps.py`

High-risk frontend files:

- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/BrokerPortal.jsx`
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/Pipeline.jsx`
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/TeamPortal.jsx`
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/Settings.jsx`
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/AdminPanel.jsx`
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/InvestorDashboard.jsx`
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/InvestorSharePage.jsx`

## Safe Refactor Moves

- Extract pure helper functions without changing return values.
- Move duplicated constants into shared modules when all callers keep the same effective output.
- Split React sections into child components while keeping props and UI output stable.
- Add tests, smoke scripts, route maps, and documentation.
- Rename internal comments and variable names when behavior stays unchanged.
- Add validation around privacy, aggregate proof, and route gating.
- Add small adapter functions that preserve old endpoint response shapes while moving implementation behind them.

## Unsafe Refactor Moves

- Combining unrelated backend routes in one commit.
- Moving ROI math and changing assumptions in the same slice.
- Splitting frontend components and redesigning visual layout in the same slice.
- Touching FUB sync and broker ROI dedupe in the same slice.
- Changing public investor share-link token flow while moving investor proof logic.
- Changing database startup/migration behavior while also changing endpoint payloads.
- Deleting “legacy” automation scripts before inventorying active timers/services/processes.

## Complexity Budget Targets

These are directional targets, not hard blockers:

- Backend route files should trend toward thin route handlers plus imported services/helpers.
- Shared business rules should live outside route files when they are used by more than one route.
- ROI assumptions, budget parsing, stage probabilities, and GCI helpers should have one backend source of truth.
- React page files above 1,000 lines should be split by tab/section before major feature work continues in those files.
- Frontend formatting helpers for money, percent, dates, status badges, and proof cards should be shared rather than copied.
- Endpoint response contracts should remain stable unless a later phase explicitly changes them.

## P2 Entry Criteria

P2 may begin only when:

- `PRODUCT_SURFACE_INVENTORY.md` exists and matches current route reality.
- `BASELINE_SMOKE_CHECKLIST.md` exists.
- `scripts/vesta_smoke.py` passes against the local production API.
- `WORKING_MEMORY.md` includes the latest P1 checkpoint.
- There are no known uncommitted changes in `/home/empathetic/eliterealty.homes`.
- The first P2 slice is limited to a single boundary, preferably shared ROI helper extraction.

## P2 Execution Guard

For every P2 quarter:

- Run `python3 scripts/vesta_smoke.py` before implementation when the API is up.
- Make the smallest behavior-preserving code move possible.
- Run language/build checks for touched surfaces:
  - Python compile checks for touched backend modules.
  - `npm run lint` and `npm run build` for touched frontend source.
  - `npm run deploy` only when frontend deploy is required.
- Run `python3 scripts/vesta_smoke.py` after implementation.
- Update `WORKING_MEMORY.md`.
- Commit the checkpoint to `track-3`.

## First Recommended P2 Slice

Start with P2Q1, but split it into a narrow first commit:

- Create a shared backend ROI math helper for:
  - stage probability lookup
  - budget parsing
  - lead GCI calculation
- Keep existing endpoint response shapes unchanged.
- Convert only one low-risk caller first if possible, then run smoke checks.

Do not change assumptions values during the extraction. The goal is structural consolidation, not new math.
