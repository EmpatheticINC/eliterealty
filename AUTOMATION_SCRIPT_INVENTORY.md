# Vesta Automation Script Inventory

Date: 2026-04-11

Scope: P4Q2 of the simplification/refactor track.

This inventory is intentionally non-destructive. No scripts, services, timers, or units were removed or moved during this pass.

Production workspace reviewed:

- `/home/empathetic/.openclaw/workspace`
- `/home/empathetic/.openclaw/workspace/scripts`
- `/home/empathetic/.config/systemd/user`

## Executive Summary

- Root-level automation/script files found: `133` Python, shell, and JavaScript files.
- Active/enabled user systemd services and timers are the current source of truth for production automation ownership.
- Disabled units exist that reference missing scripts. Treat them as stale candidates, but do not delete until a later archive pass.
- `vesta-platform.service` is disabled and labeled as the legacy demo API unit. Do not restart or re-enable it for production.
- `vesta-api.service` is the production FastAPI/PWA service.

## Active Or Enabled Production Spine

These services/timers are enabled and should be treated as production-owned unless separately retired.

| Unit | Status | Backing command or file | Classification | Notes |
|---|---:|---|---|---|
| `cloudflared.service` | enabled, running | `cloudflared tunnel ...` | Active infrastructure | Tunnel for production ingress. Do not expose or rewrite token inline. |
| `vesta-api.service` | enabled, running | `uvicorn api.app:app --host 127.0.0.1 --port 8080` | Active production app | Primary production API and PWA. |
| `vesta-bot.service` | enabled, running | `vesta-bot.py` | Active automation | Discord bot, slash commands, approval buttons. |
| `email-monitor.service` | enabled, running | `email-monitor.py` | Active automation | Email auto-responder monitor. |
| `fub-inbound-monitor.service` | enabled, running | `fub-inbound-monitor.py` | Active automation | FUB inbound reply monitor. |
| `speed-to-lead.service` | enabled, running | `speed-to-lead.py` | Active automation | Speed-to-lead auto response. |
| `lead-activity-server.service` | enabled, running | `lead-activity-server.py` | Active automation | Email open pixel/activity tracking server. |
| `vesta-continuous.service` | enabled, running | `vesta_continuous_agent.py` | Active automation | Continuous background agent. |
| `vesta-dashboard.service` | enabled, running | `vesta-dashboard.py` | Active dashboard | Real-time agent activity monitor. |
| `vesta-crm.service` | enabled, running | `/home/empathetic/.openclaw/vesta-crm/app.py` | Active dashboard | Separate Flask CRM dashboard, outside main workspace root. |
| `vesta-fub-sync.timer` | enabled, waiting | triggers `vesta-fub-sync.service` | Active timer | Runs FUB sync every 2 minutes. |
| `vesta-fub-sync.service` | enabled, oneshot | `scripts/fub_periodic_sync.py` | Active automation | Periodic FUB sync. |
| `vesta-db-backup.timer` | enabled, waiting | triggers `vesta-db-backup.service` | Active timer | Nightly DB backup at 2:00 AM. |
| `vesta-db-backup.service` | enabled, oneshot | `vesta-db-backup.sh` | Active maintenance | SQLite backup/integrity check. |
| `vesta-allday-learning.timer` | enabled, waiting | triggers `vesta-allday-learning.service` | Active timer | Runs every 5 minutes. |
| `vesta-allday-learning.service` | enabled, oneshot | `all-day-learning.py` | Active automation | Knowledge expansion job. |
| `vesta-loop-alert@.service` | template | `systemd-loop-alert.sh` | Active support utility | OnFailure alert template used by multiple services. |

## Disabled Or Stale Unit Definitions

These units are not enabled. They should not be treated as production automation until explicitly repaired and re-enabled.

| Unit | Enabled? | Referenced file | File exists? | Classification | Notes |
|---|---:|---|---:|---|---|
| `vesta-platform.service` | disabled | `uvicorn api.app:app` with demo DB env | yes | Legacy/demo unit | Keep disabled. Do not use for production. |
| `vesta-composio.service` | disabled | `composio_continuous_agent.py` | no | Stale disabled unit | Unit references a missing file. |
| `sms-inbound-monitor.service` | disabled | `sms-inbound-monitor.py` | no | Stale disabled unit | Unit references a missing file. |
| `telegram-listener.service` | disabled | `telegram-listener.sh` | no | Stale disabled unit | Unit references a missing file. |

## Active Script Files

Treat these as active or production-adjacent because systemd currently references them:

- `all-day-learning.py`
- `email-monitor.py`
- `fub-inbound-monitor.py`
- `lead-activity-server.py`
- `scripts/fub_periodic_sync.py`
- `speed-to-lead.py`
- `systemd-loop-alert.sh`
- `vesta-bot.py`
- `vesta-dashboard.py`
- `vesta-db-backup.sh`
- `vesta_continuous_agent.py`

Also active but outside the workspace root:

- `/home/empathetic/.openclaw/vesta-crm/app.py`

## Manual Utility Candidates

These look like manual utilities, reporting helpers, validators, or operator-run scripts. Do not delete; keep until a later archive pass confirms ownership.

- `approval_triage.py`
- `build-knowledge-base.sh`
- `chunk_knowledge.py`
- `crypto_utils.py`
- `daily-report.sh`
- `db_migrate.py`
- `discord_channels.py`
- `extract-address.py`
- `generate_training_docs.py`
- `ingest_knowledge.py`
- `loop_guard.py`
- `market-research.sh`
- `morning-report.py`
- `morning-report.sh`
- `morning_briefing.py`
- `neighborhood-research.sh`
- `night-learning.py`
- `night-learning.sh`
- `nightly-report.sh`
- `outlook_mail.py`
- `preflight_check.py`
- `routing-health-report.py`
- `run-cma.sh`
- `team_config.py`
- `trainual-scraper.py`
- `translate-document.py`
- `vesta-api-validator.py`
- `vesta-backup.sh`
- `vesta-cleanup.py`
- `vesta-db-backup.sh`
- `vesta-diagnose.py`
- `vesta-full-sync.py`
- `vesta-healthcheck.py`
- `vesta-memory-prune.py`
- `vesta-morning-briefing.py`
- `vesta-query.py`
- `vesta-system-health.py`
- `watch-mls-csv.sh`

## Feature Automation Candidates

These look like product/agent automation modules. They may be useful, but are not directly referenced by enabled systemd units in this pass unless listed in the active section.

- `appointment-reminders.py`
- `auto-lead-response.sh`
- `budget-tracker.py`
- `budget_tracker.py`
- `buyer-journey-analytics.py`
- `buyer-prequalification-bot.py`
- `check-property-status.js`
- `check-property-status.sh`
- `client-anniversary.py`
- `cma_deliver.py`
- `commission-tracker.py`
- `contract_watchdog.py`
- `document-chaser.py`
- `duplicate-detector.py`
- `expired-fsbo-prospector.py`
- `fair_housing_checker.py`
- `flexmls-email-monitor.py`
- `follow-up-drips.py`
- `fub-leads.sh`
- `fub-telegram-handler.sh`
- `home-valuation-report.py`
- `lead-scoring.py`
- `lead-source-roi.py`
- `lead_decay_watchdog.py`
- `listing-alert-push.py`
- `listing-description-writer.py`
- `listing-monitor.sh`
- `listing-presentation-generator.py`
- `market-snapshot.py`
- `market_pulse.py`
- `mls-intelligence.py`
- `mortgage-rate-alert.py`
- `negotiation-coach.py`
- `neighborhood-report.py`
- `new_listing_alert.py`
- `noshow-recovery.py`
- `notification_router.py`
- `objection-handler.py`
- `open-house-capture.py`
- `pipeline-pulse.py`
- `post-showing-feedback.py`
- `preference-learner.py`
- `preference-matcher.py`
- `prequal_expiry_watchdog.py`
- `prequalification-detector.py`
- `price-drop-alerts.py`
- `price-tracker.sh`
- `process-leads.py`
- `property-match-digest.py`
- `rate_watcher.py`
- `referral-tracker.py`
- `review-request.py`
- `revival-campaign.py`
- `send-calendar-invite.py`
- `showing-confirmation-parser.py`
- `smart-match.py`
- `social-media-post.py`
- `stagnant_listing_alert.py`
- `stagnation-report.py`
- `transaction-timeline.py`
- `transaction-tracker.py`
- `weekly-summary.py`
- `zillow-import.py`
- `zillow-workspace-scraper.py`
- `zillow_api.py`

## Demo, Test, Or Scenario Files

These should not be promoted into production automation without an explicit review.

- `demo_new_lead.py`
- `demo_refresh.py`
- `demo_seed.py`
- `test_e2e_smoke.py`
- `test_soul_knowledge.py`
- `test_system_integration.py`
- `vesta-test-scenarios.py`

## Core Vesta Library/Agent Modules

These look like shared code or agent internals rather than standalone operator scripts.

- `stage_policy.py`
- `vesta_agents.py`
- `vesta_approvals.py`
- `vesta_constants.py`
- `vesta_errors.py`
- `vesta_exa.py`
- `vesta_intent.py`
- `vesta_llm.py`
- `vesta_memory.py`
- `vesta_proactive.py`
- `vesta_self_upgrade.py`
- `vesta_utils.py`

## Archive Candidates For Later Review

These are candidates only. Do not delete or move them until a later phase confirms they are not imported, not referenced by docs, not used manually, and not needed for rollback.

- Disabled units referencing missing files:
  - `vesta-composio.service`
  - `sms-inbound-monitor.service`
  - `telegram-listener.service`
- Legacy/demo unit:
  - `vesta-platform.service`
- Demo scripts:
  - `demo_new_lead.py`
  - `demo_refresh.py`
  - `demo_seed.py`

## P4Q2 Recommendation

- Keep active/enabled systemd-backed files in place.
- Do not remove the disabled units yet; mark them for a later archive/removal pass.
- For P4Q3, focus on database startup/migration cleanup from the plan.
- For a later P4 archive pass, build an import/reference check before moving any root scripts.
