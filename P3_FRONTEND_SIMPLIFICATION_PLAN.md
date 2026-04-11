# Vesta P3 Frontend Simplification Plan

Date: 2026-04-11

Scope: P3 of the simplification/refactor track.

P3 reduces frontend risk by splitting large React panels and centralizing repeated UI/formatting logic. This is not a redesign phase. The goal is to make future visual and product work safer without changing live product behavior.

## P3 Principle

Preserve the screen first, then simplify the file.

Each quarter should keep route behavior, data loading, payload assumptions, and visible UI output stable unless a later product request explicitly asks for a design change.

## Current Frontend Complexity Map

Largest frontend files as of this checkpoint:

- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/BrokerPortal.jsx` - 1,935 lines
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/Pipeline.jsx` - 1,916 lines
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/TeamPortal.jsx` - 1,201 lines
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/Settings.jsx` - 1,074 lines
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/AdminPanel.jsx` - 963 lines
- `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/Chat.jsx` - 829 lines

Existing shared components:

- `components/StatCard.jsx`
- `components/Badge.jsx`
- `components/EmptyState.jsx`
- `components/LoadingSpinner.jsx`
- `components/LeadCard.jsx`
- `components/Modal.jsx`
- `components/SvgCharts.jsx`

Observed duplication:

- Money formatting appears separately in `InvestorDashboard.jsx`, `InvestorSharePage.jsx`, `Pipeline.jsx`, and `AdminPanel.jsx`.
- Date/time formatting appears separately in `BrokerPortal.jsx`, `TeamPortal.jsx`, `AdminPanel.jsx`, `InvestorDashboard.jsx`, `InvestorSharePage.jsx`, and `Settings.jsx`.
- Status/tone helpers exist in several page files, including Admin operations tones, Broker CMA tones, Pipeline revenue tones, and local setup/gap badges.
- Investor proof card/tile UI is duplicated between authenticated Investor dashboard and public Investor share page.
- Broker and Team portals have similar setup/gap badge concepts.

## P3Q1: Shared Formatting And Small UI Utilities

Goal: centralize low-risk formatting helpers and small duplicated presentational widgets.

Implementation scope:

- Add shared frontend utility module(s), likely under:
  - `src/utils/format.js`
  - optionally `src/components/ProofCard.jsx` or similar if the first extraction stays small
- Start with pure helpers only:
  - money formatting
  - percent formatting
  - compact date/time formatting
  - safe number fallback formatting
- Convert the lowest-risk callers first:
  - `InvestorDashboard.jsx`
  - `InvestorSharePage.jsx`
  - possibly `AdminPanel.jsx` money/date helpers if the diff stays small
- Keep `StatCard.jsx`, `Badge.jsx`, and route layouts unchanged unless a tiny utility import is clearly safe.

Do not change:

- Page layouts.
- CSS class names for major cards/sections.
- API calls or data-loading flows.
- Investor proof wording.
- Admin privacy surfaces.
- Broker/Pipeline data assumptions.

Verification:

- Run `npm run lint`.
- Run `npm run build`.
- Run `npm run deploy` only if frontend source is changed and the user wants it live immediately.
- Run `python3 scripts/vesta_smoke.py` after deploy or after API is confirmed healthy.

Done when:

- At least two duplicated formatter implementations are replaced by shared utilities.
- No visible product redesign is introduced.
- Frontend build passes.
- Memory is updated and the checkpoint is committed to `track-3`.

## P3Q2: Broker Portal Component Split

Goal: reduce the largest frontend panel risk without changing broker workflow.

Implementation scope:

- Split `BrokerPortal.jsx` by stable sections/tabs.
- Candidate extraction boundaries:
  - Overview command center
  - ROI/revenue proof panel
  - Teams/agents roster sections
  - Health/system sections
  - CMA operations section
  - Small setup/gap/status badge widgets
- Keep data fetching in the parent first, passing props into extracted child components.
- Avoid moving endpoint calls and layout redesign in the same slice.

Do not change:

- Broker tabs, labels, or navigation.
- API endpoints.
- Distinct-FUB and ROI display assumptions.
- CMA file/action visibility.
- Error handling copy unless fixing a verified bug.

Verification:

- Run `npm run lint`.
- Run `npm run build`.
- Deploy if frontend changes are ready to ship.
- Run smoke after deploy.
- Manually spot-check `/broker` if feasible.

Done when:

- `BrokerPortal.jsx` is meaningfully smaller.
- Extracted components have stable props and no new data-fetching behavior.
- Broker smoke endpoints still pass.

## P3Q3: Pipeline Component Split

Goal: reduce Pipeline risk while preserving all lead actions and revenue-protection visibility.

Implementation scope:

- Split `Pipeline.jsx` around stable UX areas:
  - lead list/card wrappers
  - board/list view shell
  - lead detail panel
  - compose/draft email modal
  - revenue protection strip/details
  - search/filter/keyboard helper sections if separable
- Keep lead scoping, filters, sorting, and action behavior unchanged.
- Preserve P2Q2 revenue-protection payload assumptions.

Do not change:

- Lead actions.
- Stage update behavior.
- Approval-gated email flow.
- Revenue-protection labels/math.
- Pipeline filters/sort order.
- Client visibility or role scoping.

Verification:

- Run `npm run lint`.
- Run `npm run build`.
- Deploy if frontend changes are ready to ship.
- Run smoke after deploy.
- Manually spot-check `/pipeline` if feasible.

Done when:

- `Pipeline.jsx` is meaningfully smaller.
- Revenue-protection UI still renders from the same payload keys.
- Pipeline smoke endpoints still pass.

## P3Q4: Admin, Team, Settings, And P3 Closeout

Goal: finish the remaining frontend simplification pass without risking settings/security behavior.

Implementation scope:

- Split smaller but still large panels by stable functional sections:
  - `AdminPanel.jsx`: Overview, Members, System, ROI, Audit
  - `TeamPortal.jsx`: Overview, agents, activity, approvals, trends/briefing
  - `Settings.jsx`: FUB, sender/comms, push, skills, account/preferences
- Settings should be handled most carefully because it touches credentials, comms, push, and skills.
- Add or update small shared UI pieces if P3Q1 created a useful utility foundation.

Do not change:

- Admin no-client-visibility posture.
- Settings credential save/validation flows.
- Push notification setup behavior.
- Skills settings API paths.
- Team lead visibility boundaries.

Verification:

- Run `npm run lint`.
- Run `npm run build`.
- Deploy final P3 bundle.
- Run `python3 scripts/vesta_smoke.py`.
- Record active bundle asset names if deploy changes them.

Done when:

- P3’s main large-file risks are reduced or clearly staged for the next frontend phase.
- Shared formatting utilities are in place.
- Frontend build and smoke checks pass.
- `WORKING_MEMORY.md` is updated.
- Checkpoint is committed and pushed to `track-3`.

## P3 Exit Criteria

- Shared frontend formatting utilities exist and are used by at least the investor proof surfaces.
- `BrokerPortal.jsx` and `Pipeline.jsx` have meaningful component boundaries.
- Admin/Team/Settings have a clear section split or a documented next-slice plan if one proves too risky.
- No route behavior, auth behavior, API payload shape, or privacy boundary is changed accidentally.
- Frontend lint/build pass for each implementation quarter.
- Smoke passes after each deployed frontend slice.

## Recommended First Slice

Start with P3Q1.

Recommended first commit:

- Add `src/utils/format.js`.
- Move money/date formatting out of `InvestorDashboard.jsx` and `InvestorSharePage.jsx`.
- Run lint/build.
- Deploy only after build passes.

Reason: the investor proof pages are smaller than Broker/Pipeline, duplicate the same formatting, and are high-value investor-facing surfaces. This gives us a safe frontend utility foundation before touching the largest panels.
