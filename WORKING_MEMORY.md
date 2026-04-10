# Working Memory

This file is the durable project memory for the production build. It exists so work does not depend on chat continuity.

## Current Focus

- Production side of the app is the active track.
- Demo was already completed before this point.
- We should treat production work as the source of truth going forward.

## Recovery Notes

- A previous thread was closed unexpectedly, so conversational context was lost.
- To avoid repeating that failure mode, every meaningful step should be recorded here as work progresses.
- If a future session resumes cold, start by reading this file first.

## Known Repo State

Date: 2026-04-10

- Repo: `eliterealty.homes`
- Active branch: `track-3`
- Remote branch exists: `origin/track-3`
- Current pushed commit: `6887432` - `Add Track 3 listing experience assets`
- Demo is considered complete.
- Production implementation is the active workstream.

## Important Context

- `index.html` is still the simpler landing page currently tracked on top of the original site.
- `api/build-listings.py`, `api/listings.json`, `css/style.css`, and `js/app.js` contain a richer listings-oriented experience that appears to be part of the production build direction.
- The relationship between the current `index.html` and the newer production assets still needs to be reconciled intentionally.

## Action Log

### 2026-04-10

- Recovered the correct git repo at `/home/empathetic/eliterealty.homes`.
- Verified there was no remote `track-3` branch yet.
- Created branch `track-3`.
- Added and committed production-related assets:
  - `.gitignore`
  - `api/build-listings.py`
  - `api/listings.json`
  - `css/style.css`
  - `js/app.js`
- Removed accidental Python bytecode from the commit.
- Pushed `track-3` to GitHub.
- Confirmed with user that the real priority is production, not demo.
- Added this file so project memory persists in the repo.
- Reviewed the current production app in `/home/empathetic/.openclaw/workspace/vesta-app` with an investor-ROI lens.
- Confirmed broker and lead workflows are materially built, but the app still presents more like an operator console than an investor-value product.
- Identified the main product gap as proof of financial return, payback, conversion lift, and retained revenue not being surfaced prominently enough.
- Identified the main implementation gap as revenue evidence being present in the broker portal but fragmented across tabs and not turned into a simple executive value story.
- Implemented Phase 1 in the production app: executive ROI layer added to Broker Portal overview using live metrics already available in `/api/broker/overview`, `/api/broker/pipeline_value`, and `/api/broker/revenue`.
- Implemented Phase 2 in the production app: team efficiency ROI layer added to Team Portal overview using existing team metrics for load per agent, hot lead pressure, actions per agent, approval load, stale rate, and sender readiness.
- Verified both Phase 1 and Phase 2 changes with `npm run build` and `npm run lint` in `/home/empathetic/.openclaw/workspace/vesta-app`.
- Reworked the production Admin panel in `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/AdminPanel.jsx` to focus on system operations instead of pipeline/client access.
- Shifted Admin toward a cleaner operations view with:
  - platform health
  - active member counts
  - brokerage/team structure
  - member roster controls
  - audit visibility
- Removed the need for Admin to view client-specific pipelines; the page now reads more like an org operations console than a sales workspace.
- Verified the new Admin panel with `npm run build` and `npm run lint` in `/home/empathetic/.openclaw/workspace/vesta-app`.
- Deployed the production Admin panel to the live app static bundle served by `https://vesta-tech.net/admin`.
- Verified the live `/admin` route now loads `/api/ui/assets/index-Bt6_cxVV.js`, which contains the `Platform Operations` Admin upgrade.
- Removed old `Michigan Top Producers`, `Elite Team`, and `Elite Real Estate Teams` branding from active production app, API, demo prompt defaults, static app metadata, and current public bundles.
- Updated the app deploy script to clear stale `index-*` JS/CSS bundles before copying the current build so old branded bundles do not remain publicly accessible after deploys.
- Removed the old public `index.v1.0.backup.html` file because it contained retired brokerage/team branding and was still web-accessible.
- Gracefully reloaded the running Uvicorn API parent with `SIGHUP`; health check remained OK afterward.
- Removed stale legacy app entrypoints that could confuse production testing:
  - `/home/empathetic/.openclaw/workspace/api/static/app.html`
  - `/home/empathetic/html/vesta-tech/app/app.html`
  - `/home/empathetic/html/vesta-tech/app/index.html`
- Updated `/app` and `/app/*` compatibility routes in `/home/empathetic/.openclaw/workspace/api/app.py` so old links redirect into the current production React app instead of legacy static shells.
- Restarted the Uvicorn API process so the compatibility redirects are active.
- Verified `https://vesta-tech.net/app/app.html` now resolves to `https://vesta-tech.net/chat`, and `https://vesta-tech.net/admin` still loads the upgraded `index-Bt6_cxVV.js` bundle.
- Completed final Phase 2 Admin polish:
  - added visible `System Admin only`, `No client pipeline access`, and `Current route: /admin` badges
  - added Admin actions for reviewing pending users, opening the audit trail, exporting the filtered audit CSV, and copying the active `/admin` URL
  - redeployed the production React bundle to `https://vesta-tech.net/admin`
  - verified the live Admin route now loads `/api/ui/assets/index-Dh-46mQT.js`
  - verified lint/build pass and the API health check remains OK
- Fixed the live Admin `Loading…` / stale behavior report:
  - Confirmed the real production admin account is `aiden@vesta-tech.net`.
  - Confirmed `aiden.h.huynh@gmail.com` and `empathetic.inc@gmail.com` are test accounts, not production master admins.
  - Removed `empathetic.inc@gmail.com` from the master-admin allowlist in `/home/empathetic/.openclaw/workspace/auth/session.py`.
  - Updated OAuth session routing in `/home/empathetic/.openclaw/workspace/api/routers/auth.py` so `system_admin` users land on `/admin` instead of `/chat`.
  - Updated `/home/empathetic/.openclaw/workspace/vesta-app/src/App.jsx` so a `system_admin` session redirects to `/admin` before tenant pages such as Chat can mount.
  - Kept the earlier Layout guard in `/home/empathetic/.openclaw/workspace/vesta-app/src/components/Layout.jsx` so system admins do not poll tenant pipeline/onboarding/SSE endpoints.
  - Rebuilt and redeployed the production React bundle; live `/admin` now serves `/api/ui/assets/index-CcYHGCXs.js`.
  - Restarted the Uvicorn API with `setsid`; health check returned `{"status":"ok","db":"ok","version":"1.0.0"}`.
  - Verified a generated `aiden@vesta-tech.net` system-admin session can call `/auth/me`, `/api/admin/stats`, `/api/admin/system`, and `/api/admin/users` with HTTP 200.
  - Verified `/app/app.html` still redirects to `https://vesta-tech.net/chat`.
- Added another Admin portal upgrade for account visibility and truthful metrics:
  - Verified Jane Doe (`empathetic.inc@gmail.com`) and John Doe (`aiden.h.huynh@gmail.com`) were not deleted and still exist as test accounts.
  - Added an Admin `Identity Control Center` that separates the real production admin (`aiden@vesta-tech.net`) from the two dummy accounts.
  - Added Admin `Access Guardrails` with system-admin count, inactive member count, and clickable role distribution.
  - Added `Show Jane / John` and `Show Admin` quick filters in the member roster.
  - Reworked Admin labels to avoid ambiguous or inflated KPI language; counts now say `DB Users`, `Active User Records`, `Active Agents`, and `Live DB counts`.
  - Expanded `/api/admin/stats` to return live SQLite-derived values with `source=live_sqlite` and `generated_at`.
  - Verified the live Admin stats API matches direct SQL exactly: `77` total users, `75` active users, `2` inactive users, `59` active agents, `8` teams, `4` brokerages, `1` pending user, and `2` test accounts.
  - Fixed the `vesta-platform` service status signal so the running API reports active instead of falsely depending on a mismatched user systemd unit.
  - Deployed the updated Admin bundle to `https://vesta-tech.net/admin`; current bundle is `/api/ui/assets/index-AyhKiC9Q.js`.
- Added Admin control for deleting pending platform members:
  - Added backend route `POST /api/admin/users/delete-pending`.
  - The route is system-admin only, re-checks the master admin email, and only allows deleting users with `role='pending'` and no `onboarded_at`.
  - The route blocks non-pending users, system admin, Jane Doe, John Doe, and onboarded accounts from this delete path.
  - It safely detaches/deletes pending-user session/activity references and writes an `admin_pending_user_deleted` audit event.
  - Added a `Delete Pending` button to pending rows in the Admin member roster.
  - Added the audit label `Pending user deleted` and included this event in the Admin audit feed.
  - Verified with a disposable pending smoke account: delete returned HTTP 200, the row was removed, the audit event was written, and deleting John Doe returned HTTP 403.
  - Redeployed the Admin bundle; current live bundle is `/api/ui/assets/index-BO89WjB5.js`.
- Cleaned remaining live Admin/database branding bleed:
  - Updated the default brokerage label in the app database from `Michigan Top Producers` to `Vesta Platform`.
  - Updated the default admin team label in the app database from `Elite Team` to `Core Operations`.
  - Verified the Admin users API no longer returns `Michigan Top Producers` or `Elite Team`.
  - Removed stale public `Junk` signature HTML files under `/home/empathetic/html/vesta-tech/Junk` that still contained old affiliation text.
  - Re-ran an active-path branding search across production app source, API static bundle, and the public marketing directory; no active matches remained for `Michigan Top Producers`, `Elite Team`, `Elite Real Estate Teams`, `Built for Elite`, or `Top Producers`.
- Replaced placeholder branding on `vesta-tech.net` with a proper reusable logo system:
  - `logo-mark.svg`
  - `logo-wordmark.svg`
  - `logo-mark-192.png`
  - `logo-mark-512.png`
  - `og-logo.png`
- Updated the live marketing site to use the new logo in nav, mobile menu, footer, social preview metadata, manifest icons, and service worker notification icons.
- Audited and cleaned live-site demo links so active demo CTAs now route to `https://vesta-tech.net/demo.html`, and removed dead `dev-login` / `demo-switch` marketing links.
- Confirmed `vesta-tech.net` DNS is hosted on Cloudflare nameservers:
  - `kareem.ns.cloudflare.com`
  - `selah.ns.cloudflare.com`
- Checked public TXT records for `vesta-tech.net` and confirmed the OpenAI domain verification TXT record is not published yet.
- OpenAI verification token to add at the root domain:
  - `openai-domain-verification=dv-Nz0VOpJk3FDB6xVDYTGJcdfD`
- Current blocker: no Cloudflare credentials are available in this environment, so DNS can be verified from here after publication, but not created from this machine today.

## Operating Rule Going Forward

- Before ending a work session, update this file with:
  - what changed
  - current branch and commit
  - what is done
  - what is next
  - any open questions or risks

## Next Recommended Step

- Prioritize an investor-facing ROI layer inside the production app:
  - executive summary strip
  - retained revenue / revenue at risk delta
  - automation savings in dollars, not only hours
  - conversion lift and response-time proof
  - simple payback framing per team and per seat

## ROI Phases

- Phase 1: Executive ROI Layer — complete
- Phase 2: Team Efficiency ROI — complete
- Phase 3: Lead-Level Revenue Protection — started
- Phase 4: Market Positioning + Product Proof — pending

## Immediate Next Steps

- In Cloudflare DNS for `vesta-tech.net`, add a TXT record at `@` with value `openai-domain-verification=dv-Nz0VOpJk3FDB6xVDYTGJcdfD`.
- After DNS propagation, re-check the public TXT record and complete the OpenAI-side verification.
- Continue production work with Phase 3 by expanding the revenue-protection layer into stronger broker/admin rollups and trend proof.

## 2026-04-10 P3 Revenue Protection Build

- Built the first P3 slice: Lead-Level Revenue Protection for the production Pipeline.
- Backend file changed: `/home/empathetic/.openclaw/workspace/api/routers/pipeline.py`.
- Frontend file changed: `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/Pipeline.jsx`.
- Added live per-lead `revenue_protection` data based on actual lead budget, stage probability, score, and last-contact SLA, not fabricated demo values.
- Revenue model:
  - estimated home value = parsed lead budget, falling back to `320000` only when no usable budget exists
  - commission rate = `2.5%`
  - stage probability varies by real stage, from `4%` new to `100%` closed
  - weighted GCI = home value x commission rate x stage probability
  - revenue at risk only appears when warm/hot leads breach the last-contact SLA
- Added aggregate `revenue_protection` data to `/api/pipeline/stats`:
  - `revenue_at_risk`
  - `critical_revenue_at_risk`
  - `at_risk_leads`
  - `protected_weighted_gci`
  - `source=budget_x_commission_x_stage_probability`
- Added revenue-protection pills to hot leads, board cards, and list rows when a lead has revenue at risk.
- Added a Pipeline `Revenue Protection` stats strip with at-risk dollars, SLA flags, and protected weighted GCI.
- Added a lead-detail `Revenue Protection` card showing estimated GCI, stage weight, last touch, SLA label, and recommended action.
- Verification completed:
  - `python3 -m compileall -q /home/empathetic/.openclaw/workspace/api /home/empathetic/.openclaw/workspace/auth`
  - `npm run lint`
  - `npm run build`
  - `npm run deploy`
  - API restart and `/health` check passed
  - Live `/pipeline?fresh=p3` serves `/api/ui/assets/index-3QRCBEe5.js`
  - Live bundle contains `Revenue Protection`, `Revenue at risk`, `lead SLA flags`, `budget x`, and `revenue_protection`
  - John Doe test scope verified through API token: `79` leads, `0` at-risk dollars, `0` SLA flags, and `$177,906` protected weighted GCI
- Important truthfulness note: John Doe's current scoped data correctly shows `$0` revenue at risk because his hot leads are recently contacted/protected; this should stay truthful rather than padded.

## 2026-04-10 Admin/Broker Integration Pass

- Reworked the production Admin panel into a cleaner left-nav control center:
  - Overview
  - Members
  - System
  - Audit
- Removed the previous large explanatory Admin hero text and the unnecessary `Show Jane / John` / `Show Admin` quick-filter buttons.
- Members now use a normal search/filter flow and show role, brokerage, team, onboarding timestamp, active status, and controls.
- Added a dedicated Admin `System` panel with service health, AI/Qdrant vector status, pending approvals, active sessions, DB size, memory use, auth coverage, and table-count visibility.
- Tightened the Admin audit trail UI and changed the backend audit feed to exclude client-level email/lead events so the system admin surface does not expose client names or pipeline details.
- Preserved only the three intended active member accounts in the users table:
  - `aiden@vesta-tech.net` — system admin
  - `aiden.h.huynh@gmail.com` — John Doe test broker
  - `empathetic.inc@gmail.com` — Jane Doe test team lead
- Removed seeded/demo users, demo teams, demo brokerages, team invites, demo lead artifacts, old AI routing logs, old demo memory directives, and old-branded email signatures.
- Database backup created before cleanup:
  - `/home/empathetic/.openclaw/workspace/vesta.pre-demo-cleanup.20260410T212714Z.db`
- Current remaining org labels:
  - Admin: `Vesta Platform` / `Core Operations`
  - Test accounts: `Vesta Sandbox` / `Sandbox Team`
- Old branding/database scan is clean for:
  - `Michigan Top Producers`
  - `Elite Team`
  - `Top Producers`
  - `John Doe (Sample Lead)`
  - `michigantopproducers.com`
- Broker overview audit:
  - Reproduced all Broker overview widget endpoint calls as John Doe.
  - `/api/broker/overview`, `/teams`, `/activity`, `/leaderboard`, `/health`, `/trends`, `/pipeline_value`, `/revenue`, and `/briefing` all returned HTTP 200.
  - Replaced the vague Broker frontend warning with a widget-specific message: `Broker widgets unavailable: <names>. Core overview is live.`
  - Fixed Broker briefing revenue math so it scopes revenue snapshot leads by the acting broker's brokerage.
- Verified Claude/frontend integration:
  - `npm run lint` passed.
  - `npm run build` passed.
  - `npm run deploy` passed.
  - API compile check passed.
  - API restarted and `/health` returned OK.
  - Live bundle: `/api/ui/assets/index-Bz6nMiIC.js`.
- Open product risk:
  - Active background CRM monitors (`fub-inbound-monitor.py`, `email-monitor.py`, `speed-to-lead.py`) re-import live CRM/FUB lead data after demo cleanup.
  - Current DB has `90` leads and `45` duplicate `fub_id` groups because the same FUB contacts are being imported for both John and Jane.
  - This appears to be live CRM/import behavior rather than the old seeded `.test` demo users.
  - Next fix should de-duplicate broker/team lead rollups by `fub_id` and/or adjust `api/fub_sync.py` ownership matching so the same FUB contact is not counted twice at brokerage/team level.

## 2026-04-10 P3 Broker Revenue Dedupe

- Continued P3 by making broker/investor-facing ROI math truthful when CRM contacts are imported under multiple owners.
- Backend file changed: `/home/empathetic/.openclaw/workspace/api/routers/broker_portal.py`.
- Frontend file changed: `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/BrokerPortal.jsx`.
- Added a broker rollup CTE that chooses one canonical row per `fub_id` for brokerage-level lead/revenue math.
- Updated Broker Overview, management risk signals, Trends stage counts, Pipeline Value, Revenue, and Briefing revenue snapshot to dedupe by distinct FUB contacts where appropriate.
- Added `data_quality` / `lead_count_basis=distinct_fub_contacts` metadata to broker overview/revenue surfaces.
- Broker UI now shows the data-quality trust signal in the Executive ROI Snapshot:
  - `46 distinct CRM contacts from 92 owner rows`
- Verification:
  - `python3 -m compileall -q api/routers/broker_portal.py`
  - `npm run lint`
  - `npm run build`
  - `npm run deploy`
  - API restarted and `/health` returned OK
  - Live bundle: `/api/ui/assets/index-_9YKxYq3.js`
  - John Doe broker API verification: `/overview`, `/trends`, `/pipeline_value`, `/revenue`, `/briefing`, `/teams`, `/activity`, `/leaderboard`, and `/health` all returned HTTP 200.
  - Verified P3 dedupe numbers:
    - raw lead rows: `92`
    - distinct FUB contacts: `46`
    - overview total leads: `46`
    - hot leads: `3`
    - weighted pipeline total GCI: `$160,336`
    - pipeline GCI: `$77,794`
- Remaining P3 recommendation:
  - Add a true investor-facing ROI proof panel that compares protected revenue, automation value, and deduped CRM contact coverage over time.
  - Later harden `api/fub_sync.py` so the same FUB contact is not inserted once per connected test owner when the brokerage wants shared broker-level rollups.

## 2026-04-10 P3 Investor ROI Proof and FUB Sync Guard

- Continued remaining P3 work after broker revenue dedupe.
- Backend file changed: `/home/empathetic/.openclaw/workspace/api/fub_sync.py`.
- Frontend file changed: `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/BrokerPortal.jsx`.
- Added an `Investor ROI Proof` strip to the Broker Overview executive snapshot:
  - Protected Pipeline
  - Risk Exposure
  - Automation Leverage
  - Data Integrity
- The visible investor readout now explicitly says broker revenue projections use distinct FUB contacts so duplicated owner imports do not inflate ROI.
- Hardened FUB sync matching:
  - Existing lead lookup now matches by `fub_id + team_id + brokerage_id`, preferring the current owner only for tie-breaking.
  - Sync updates no longer overwrite an existing lead owner unless the owner is blank.
  - This should stop the same CRM contact from being newly inserted once per connected John/Jane owner going forward.
- I did not delete the existing 92 legacy owner rows in this pass because pipeline user/team visibility still needs to be handled carefully. Broker ROI math already reads the truthful deduped contact basis.
- Verification:
  - `python3 -m compileall -q api/fub_sync.py api/routers/broker_portal.py`
  - `npm run lint`
  - `npm run build`
  - `npm run deploy`
  - API restarted and `/health` returned OK.
  - Live bundle: `/api/ui/assets/index-BigjuVPJ.js`.
  - Live bundle contains `Investor ROI Proof`, `rows normalized`, and `distinct FUB contacts`.
  - Active production users are still exactly:
    - `aiden@vesta-tech.net` as system admin
    - `aiden.h.huynh@gmail.com` as head broker test account
    - `empathetic.inc@gmail.com` as team lead test account
  - John Doe broker API verification: `/overview`, `/pipeline_value`, `/revenue`, `/briefing`, `/trends`, `/teams`, `/activity`, `/leaderboard`, and `/health` all returned HTTP 200.
  - Verified current truthful ROI basis:
    - raw lead rows: `92`
    - distinct FUB contacts: `46`
    - duplicate owner rows: `46`
    - overview total leads: `46`
    - hot leads: `3`
    - GCI at risk: `$0`
    - weighted pipeline total GCI: `$160,336`
    - pipeline GCI: `$77,794`
- Remaining P3 recommendation:
  - Decide whether to run a careful one-time historical lead-row dedupe. If we do it, verify agent/team lead pipeline visibility first so we do not accidentally hide shared test CRM contacts from Jane or future agent scopes.
  - Next value slice can be ROI trend history over time, not just a point-in-time proof card.

## 2026-04-10 P3 ROI Trend Baseline

- User clarified that John/Jane currently point to the same underlying FUB account because only one FUB account is available right now:
  - The duplicate-looking contacts are expected in this temporary setup.
  - Do not run historical lead-row dedupe until separate FUB accounts/keys are available.
  - Keep broker ROI math deduped by distinct FUB contacts, but leave the raw rows alone.
- Continued P3 by adding truthful investor ROI trend capture instead of backfilled/demo history.
- Backend file changed: `/home/empathetic/.openclaw/workspace/api/routers/broker_portal.py`.
- Frontend file changed: `/home/empathetic/.openclaw/workspace/vesta-app/src/pages/BrokerPortal.jsx`.
- Added `broker_roi_snapshots` storage:
  - One row per brokerage per UTC date.
  - Captures closed GCI, pipeline GCI, total projected GCI, annual pace, targets, distinct leads, and raw lead rows.
- `/api/broker/revenue` now upserts today's ROI snapshot and returns `roi_history`.
- Added `/api/broker/roi_history?days=30`.
- Added Broker Revenue tab panel: `Investor ROI Trend`.
  - Shows current/baseline projected GCI.
  - Shows pipeline delta once at least two snapshots exist.
  - Shows a no-fake-history baseline message until daily snapshots accumulate.
- Verification:
  - `python3 -m compileall -q api/routers/broker_portal.py`
  - `npm run lint`
  - `npm run build`
  - `npm run deploy`
  - API restarted and `/health` returned OK.
  - Live bundle: `/api/ui/assets/index-ClY8UQSu.js`.
  - Live bundle contains `Investor ROI Trend`, `Baseline captured today`, and `ROI history starts now`.
  - Broker smoke endpoints returned HTTP 200:
    - `/api/broker/overview`
    - `/api/broker/revenue`
    - `/api/broker/roi_history?days=30`
    - `/api/broker/pipeline_value`
    - `/api/broker/health`
  - Captured baseline snapshot for `2026-04-10`:
    - closed GCI: `$82,542`
    - pipeline GCI: `$77,368`
    - total projected GCI: `$159,910`
    - annual pace: `$479,730`
    - distinct FUB contacts: `46`
    - raw lead rows: `101`
- Note:
  - `/api/broker/health` reports `vesta-platform` systemd service as inactive while the direct Uvicorn process and `/health` are OK. This is not blocking, but the service-manager status should be cleaned up later if we want the health panel to match the actual running API process.
