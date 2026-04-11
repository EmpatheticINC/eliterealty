# Vesta Product Surface Inventory

Date: 2026-04-11

Scope: P1Q1 simplification/refactor inventory for the production app in `/home/empathetic/.openclaw/workspace`.

This file maps the active product surfaces before any simplification refactor begins. It is intended to prevent route confusion, demo/live confusion, and handoff drift.

## Production Locations

- Production API/app source: `/home/empathetic/.openclaw/workspace/api`.
- Production React source: `/home/empathetic/.openclaw/workspace/vesta-app/src`.
- Production React deploy command: `npm run deploy` from `/home/empathetic/.openclaw/workspace/vesta-app`.
- Production API service: `vesta-api.service`.
- API static bundle served from: `/home/empathetic/.openclaw/workspace/api/static`.
- Public marketing/static asset copy target: `/home/empathetic/html/vesta-tech`.
- Durable project memory repo: `/home/empathetic/eliterealty.homes` branch `track-3`.

## API Entrypoint

- Entrypoint: `/home/empathetic/.openclaw/workspace/api/app.py`.
- Health route: `GET /health`.
- SPA shell route: `GET /{full_path:path}` for non-API/non-auth paths.
- Login page route: `GET /login`.
- Compatibility redirect: `GET /app`.
- Compatibility redirect: `GET /app/{full_path:path}`.
- UI asset mount: `/assets`.
- UI asset mount: `/api/ui/assets`.
- UI static allowlist: `GET /api/ui/{filename:path}` for `manifest.json`, `favicon.svg`, `icon-192.png`, `icon-512.png`, `icons.svg`, and `sw.js`.

## API Routers

- `auth.py`, prefix `/auth`.
  - `GET /auth/complete`
  - `GET /auth/login/microsoft`
  - `GET /auth/microsoft/callback`
  - `GET /auth/login/google`
  - `GET /auth/google/callback`
  - `POST /auth/logout`
  - `GET /auth/me`
  - `GET /auth/providers`
  - `GET /auth/dev-login`, registered but self-gated to `404` unless `VESTA_DEV_LOGIN` is enabled.
  - `GET /auth/demo-switch`, registered but self-gated to `404` unless `VESTA_DEV_LOGIN` is enabled.

- `onboard.py`, prefix `/api/onboard`.
  - `GET /api/onboard/brokerages`
  - `GET /api/onboard/teams`
  - `POST /api/onboard/verify-fub`
  - `POST /api/onboard/test-comms`
  - `POST /api/onboard/team-lead`
  - `POST /api/onboard/agent`
  - `POST /api/onboard/update-fub`
  - `POST /api/onboard/sync-fub`
  - `POST /api/onboard/update-signature`
  - `GET /api/onboard/settings`
  - `POST /api/onboard/validate-sender`
  - `POST /api/onboard/send-test-email`
  - `POST /api/onboard/save-comms`

- `chat.py`, prefix `/api/chat`.
  - `POST /api/chat/message`
  - `GET /api/chat/cma-jobs/{job_id}`
  - `GET /api/chat/file/{filename}`
  - `GET /api/chat/welcome`
  - `GET /api/chat/history`
  - `DELETE /api/chat/history`

- `pipeline.py`, prefix `/api/pipeline`.
  - `POST /api/pipeline/refresh`
  - `GET /api/pipeline/leads`
  - `GET /api/pipeline/lead/{fub_id}`
  - `GET /api/pipeline/lead/{fub_id}/draft-email`
  - `GET /api/pipeline/lead/{fub_id}/score-history`
  - `POST /api/pipeline/lead/{fub_id}/update-stage`
  - `POST /api/pipeline/lead/{fub_id}/mark-contacted`
  - `GET /api/pipeline/hot`
  - `GET /api/pipeline/stale`
  - `GET /api/pipeline/new`
  - `GET /api/pipeline/stats`

- `approvals.py`, prefix `/api/approvals`.
  - `GET /api/approvals`
  - `POST /api/approvals/{draft_id}/approve`
  - `POST /api/approvals/{draft_id}/reject`
  - `POST /api/approvals/draft`
  - `GET /api/approvals/{draft_id}/preview`
  - `POST /api/approvals/{draft_id}/edit`

- `team_portal.py`, prefix `/api/team`.
  - `GET /api/team/overview`
  - `GET /api/team/agents`
  - `GET /api/team/activity`
  - `GET /api/team/approvals`
  - `GET /api/team/leaderboard`
  - `GET /api/team/trends`
  - `GET /api/team/briefing`
  - `POST /api/team/invite/create`
  - `GET /api/team/invite/{token}`

- `broker_portal.py`, prefix `/api/broker`.
  - `GET /api/broker/overview`
  - `GET /api/broker/teams`
  - `GET /api/broker/teams/{team_id}/agents`
  - `GET /api/broker/activity`
  - `GET /api/broker/trends`
  - `GET /api/broker/briefing`
  - `GET /api/broker/leaderboard`
  - `GET /api/broker/health`
  - `POST /api/broker/cma_jobs/{job_id}/queue-email`
  - `GET /api/broker/revenue`
  - `GET /api/broker/roi_history`
  - `GET /api/broker/pipeline_value`

- `admin.py`, prefix `/api/admin`.
  - `GET /api/admin/users`
  - `GET /api/admin/stats`
  - `POST /api/admin/users/role`
  - `POST /api/admin/users/active`
  - `POST /api/admin/users/delete-pending`
  - `GET /api/admin/roi-assumptions`
  - `POST /api/admin/roi-assumptions`
  - `GET /api/admin/system`
  - `GET /api/admin/audit`

- `investor.py`, prefix `/api/investor`.
  - `GET /api/investor/snapshot`
  - `GET /api/investor/snapshot.csv`
  - `GET /api/investor/shares`
  - `POST /api/investor/shares`
  - `DELETE /api/investor/shares/{share_id}`
  - `GET /api/investor/public/{token}`
  - `POST /api/investor/public`

- `notifications.py`, prefix `/api/notifications`.
  - `GET /api/notifications/stream`
  - `GET /api/notifications/recent`

- `push.py`, prefix `/api/push`.
  - `GET /api/push/public-key`
  - `GET /api/push/status`
  - `GET /api/push/preferences`
  - `POST /api/push/preferences`
  - `POST /api/push/subscribe`
  - `DELETE /api/push/subscribe`
  - `POST /api/push/test`

- `skills.py`, mounted under `/api/settings`.
  - `GET /api/settings/skills`
  - `POST /api/settings/skills/{skill_name}`

## Demo/Dev Router

- `demo.py`, prefix `/api/demo`.
- Source routes:
  - `GET /api/demo/snapshot`
  - `POST /api/demo/chat`
  - `POST /api/demo/simulate-lead`
  - `DELETE /api/demo/cleanup`
- Production status:
  - The router is only included when `VESTA_DEV_LOGIN` is enabled.
  - Current `vesta-api.service` environment has no `VESTA_DEV_LOGIN` value.
  - Live smoke confirmed `GET /api/demo/snapshot` returns `404`.

## React Routes

- Public/standalone:
  - `/login`
  - `/onboard`
  - `/join/:token`
  - `/investor/share`
  - `/investor/share/:token`

- Protected by `ProtectedRoute`:
  - `/chat`
  - `/pipeline`
  - `/approvals`
  - `/settings`
  - `/team`
  - `/broker`
  - `/admin`
  - `/investor`

- Default behavior:
  - `/` redirects to `/chat` for normal authenticated users.
  - `system_admin` users are redirected to `/admin` unless they are already on `/admin` or `/investor`.
  - Unknown React paths redirect to `/chat`.

## Layout Navigation

- System admin navigation:
  - `/admin?tab=overview`
  - `/admin?tab=members`
  - `/admin?tab=system`
  - `/admin?tab=roi`
  - `/investor`
  - `/admin?tab=audit`

- Tenant navigation:
  - `/chat`
  - `/pipeline`
  - `/approvals`
  - `/team`, for `team_lead` and `head_broker`
  - `/broker`, for `head_broker`
  - `/investor`, for `head_broker`
  - `/settings`

## Compatibility And Static Behavior

- `GET /app` redirects to `/chat`.
- `GET /app/app.html` redirects to `/chat`.
- `GET /app/index.html` redirects to `/chat`.
- `GET /app/{known_production_route}` redirects to that production route if allowed by the compatibility list.
- Unknown non-API/non-auth paths serve the SPA shell.
- API and auth paths not registered return `404`.

## P1Q1 Live Verification

- `GET /health` returned HTTP `200` with `{"status":"ok","db":"ok","version":"1.0.0"}`.
- `GET /api/demo/snapshot` returned HTTP `404`.
- `GET /auth/dev-login` returned HTTP `404` because `VESTA_DEV_LOGIN` is off.
- `GET /app/app.html` returned HTTP `307` redirecting to `/chat`.
- `GET /login` returned HTTP `200` with `text/html`.
- `GET /admin` returned HTTP `200` with the SPA shell.
- `GET /api/ui/sw.js` returned HTTP `200` with `text/javascript`.

## P1Q1 Notes

- No production behavior changes were made in P1Q1.
- Auth dev/demo helpers are still registered in the auth router, but they self-gate to `404` unless `VESTA_DEV_LOGIN` is enabled.
- The `/api/demo/*` router is not registered in the current production service.
- The product surface is now mapped well enough to proceed to P1Q2 copy cleanup.
