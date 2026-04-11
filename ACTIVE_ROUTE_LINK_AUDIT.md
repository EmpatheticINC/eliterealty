# Vesta Active Route And Link Audit

Date: 2026-04-11

Scope: P4Q4 of the simplification/refactor track.

This audit checked active production SPA routes, compatibility redirects, PWA assets, public marketing pages, and hardcoded demo links. No frontend or API route behavior was changed during this pass.

## Production SPA Routes

The local production API shell at `http://127.0.0.1:8080` returns HTTP `200` for:

- `/`
- `/chat`
- `/pipeline`
- `/approvals`
- `/settings`
- `/team`
- `/broker`
- `/admin`
- `/investor`
- `/onboard`
- `/investor/share`
- `/join/test-token`

`/join/test-token` returns the SPA shell because invite validation happens client-side through the React invite handler.

## Legacy Compatibility Redirects

The local production API returns expected HTTP `307` redirects:

- `/app` -> `/chat`
- `/app/app.html` -> `/chat`
- `/app/pipeline` -> `/pipeline`
- `/app/demo` -> `/chat`

## PWA And Static Asset Routes

The active PWA/static routes return HTTP `200`:

- `/api/ui/sw.js`
- `/api/ui/manifest.json`
- `/api/ui/icon-192.png`
- `/api/ui/assets/index-CxukvNTr.js`
- `/api/ui/assets/index-CqHmp-f7.css`

Note: `https://vesta-tech.net/manifest.json` returned HTTP `404` in the public curl check, but the app’s active manifest route is `/api/ui/manifest.json`, and that route is now covered by smoke.

## Public Marketing Routes

The public marketing surface returned HTTP `200` for:

- `https://vesta-tech.net/`
- `https://vesta-tech.net/demo.html`
- `https://vesta-tech.net/login`
- `https://vesta-tech.net/logo-mark.svg`
- `https://vesta-tech.net/og-image.svg`

## Demo Links

The marketing page still intentionally points demo CTAs to:

- `https://vesta-tech.net/demo.html`

The production demo API remains disabled/not executable under P4Q1 smoke coverage:

- `/api/demo/snapshot`
- `/api/demo/chat`
- `/api/demo/simulate-lead`
- `/api/demo/cleanup`
- `/auth/dev-login`
- `/auth/demo-switch?role=agent`

## Smoke Harness Updates

Updated `/home/empathetic/eliterealty.homes/scripts/vesta_smoke.py` to include:

- generalized redirect validator
- legacy `/app/pipeline` redirect check
- legacy unknown `/app/demo` redirect check
- SPA shell checks for `chat`, `pipeline`, `approvals`, `settings`, `team`, `broker`, `admin`, `investor`, `onboard`, and `investor/share`
- PWA manifest check
- PWA icon check

## Verification

- `python3 -m py_compile scripts/vesta_smoke.py` passed.
- `python3 scripts/vesta_smoke.py --public-only` passed with `28 passed, 0 failed`.
- `python3 scripts/vesta_smoke.py` passed with `43 passed, 0 failed`.

## P4Q4 Result

P4Q4 is complete for the active route/link audit. The route/link smoke guard now covers production SPA shells, compatibility redirects, PWA assets, disabled demo/dev routes, and authenticated API surfaces.
