# Vesta Baseline Smoke Checklist

Date: 2026-04-11

Scope: P1Q3 simplification/refactor safety harness.

Run this before and after each later refactor slice when the production API is expected to be up.

## Command

From `/home/empathetic/eliterealty.homes`:

```bash
python3 scripts/vesta_smoke.py
```

Public-only fallback:

```bash
python3 scripts/vesta_smoke.py --public-only
```

Remote or alternate base URL:

```bash
python3 scripts/vesta_smoke.py --base-url http://127.0.0.1:8080
```

## What It Checks

- Public/unauthenticated:
  - `/health` returns DB `ok`.
  - `/auth/providers` reports `dev_login=false`.
  - `/api/demo/snapshot` returns `404`.
  - `/auth/dev-login` returns `404`.
  - `/app/app.html` redirects to `/chat`.
  - `/login` returns an HTML page.
  - `/admin` returns the SPA shell.
  - `/api/ui/sw.js` returns the service worker.
  - protected tenant/admin/investor API routes reject unauthenticated requests.

- System admin:
  - `/auth/me` returns `system_admin`.
  - `/api/admin/system` returns `ops_overview` and `ai_quality`.
  - `/api/admin/users`, `/api/admin/audit`, and `/api/admin/roi-assumptions` return JSON.
  - `/api/investor/snapshot` returns aggregate proof and no forbidden client-style keys.

- Broker:
  - `/auth/me` returns `head_broker`.
  - `/api/broker/overview`, `/api/broker/revenue`, `/api/broker/roi_history`, `/api/broker/pipeline_value`, and `/api/broker/health` return JSON.
  - `/api/approvals` and `/api/pipeline/stats` return JSON.
  - `/api/investor/snapshot` returns aggregate proof and no forbidden client-style keys.

## Notes

- The script mints short-lived local JWT cookies for the configured DB users and does not print tokens.
- Default admin smoke user: `Aiden@vesta-tech.net`.
- Default broker smoke user: `aiden.h.huynh@gmail.com`.
- If a future environment changes user emails, pass `--admin-email` or `--broker-email`.
- This is a baseline smoke harness, not a full end-to-end test suite.
