#!/usr/bin/env python3
"""Baseline smoke checks for the production Vesta app.

This script is intentionally small and dependency-free. It checks public route
behavior by default, then mints short-lived local JWT cookies for existing DB
users to verify admin, broker, investor, pipeline, and approval surfaces.

It does not print secrets or tokens.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WORKSPACE = Path.home() / ".openclaw" / "workspace"
DB_PATH = WORKSPACE / "vesta.db"
DEFAULT_BASE_URL = "http://127.0.0.1:8080"
DEFAULT_ADMIN_EMAIL = "Aiden@vesta-tech.net"
DEFAULT_BROKER_EMAIL = "aiden.h.huynh@gmail.com"
COOKIE_NAME = "vesta_session"
FORBIDDEN_PRIVACY_KEYS = {
    "client_name",
    "to_email",
    "file_url",
    "lead_name",
    "phone",
    "body",
    "subject",
    "content",
    "address",
}


@dataclass
class SmokeResult:
    name: str
    ok: bool
    detail: str


class SmokeRunner:
    def __init__(self, base_url: str, timeout: float = 8.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.results: list[SmokeResult] = []

    def record(self, name: str, ok: bool, detail: str) -> None:
        self.results.append(SmokeResult(name, ok, detail))
        status = "PASS" if ok else "FAIL"
        print(f"[{status}] {name}: {detail}")

    def request(
        self,
        method: str,
        path: str,
        *,
        token: str | None = None,
        body: dict[str, Any] | None = None,
    ) -> tuple[int, dict[str, str], str, Any | None]:
        data = None
        headers = {"Accept": "application/json"}
        if body is not None:
            data = json.dumps(body).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if token:
            headers["Cookie"] = f"{COOKIE_NAME}={token}"

        req = urllib.request.Request(
            f"{self.base_url}{path}",
            data=data,
            headers=headers,
            method=method.upper(),
        )
        opener = urllib.request.build_opener(NoRedirectHandler)
        try:
            with opener.open(req, timeout=self.timeout) as resp:
                text = resp.read().decode("utf-8", errors="replace")
                parsed = parse_json(text)
                return resp.status, dict(resp.headers), text, parsed
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            parsed = parse_json(text)
            return exc.code, dict(exc.headers), text, parsed

    def expect_status(
        self,
        name: str,
        method: str,
        path: str,
        expected: int | set[int],
        *,
        token: str | None = None,
        body: dict[str, Any] | None = None,
        validator=None,
    ) -> Any | None:
        expected_set = expected if isinstance(expected, set) else {expected}
        try:
            status, headers, text, parsed = self.request(method, path, token=token, body=body)
        except Exception as exc:
            self.record(name, False, f"request error: {type(exc).__name__}: {exc}")
            return None

        if status not in expected_set:
            preview = text[:160].replace("\n", " ")
            self.record(name, False, f"HTTP {status}, expected {sorted(expected_set)}; {preview}")
            return parsed

        if validator:
            try:
                validator(status, headers, text, parsed)
            except AssertionError as exc:
                self.record(name, False, f"HTTP {status}; {exc}")
                return parsed

        self.record(name, True, f"HTTP {status}")
        return parsed

    def exit_code(self) -> int:
        failed = [r for r in self.results if not r.ok]
        print(f"\nSmoke summary: {len(self.results) - len(failed)} passed, {len(failed)} failed")
        if failed:
            print("Failed checks:")
            for result in failed:
                print(f"- {result.name}: {result.detail}")
            return 1
        return 0


class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def parse_json(text: str) -> Any | None:
    try:
        return json.loads(text)
    except Exception:
        return None


def load_user(email: str) -> dict[str, str]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT id, email, display_name, role, team_id, brokerage_id, is_active, onboarded_at
            FROM users
            WHERE lower(email)=lower(?)
            """,
            (email,),
        ).fetchone()
        if not row:
            raise RuntimeError(f"no user found for {email}")
        if not row["is_active"]:
            raise RuntimeError(f"user is inactive: {email}")
        return dict(row)
    finally:
        conn.close()


def mint_token(email: str) -> str:
    sys.path.insert(0, str(WORKSPACE))
    from auth.session import create_token

    user = load_user(email)
    return create_token(
        user_id=user["id"],
        role=user["role"],
        team_id=user.get("team_id") or "",
        brokerage_id=user.get("brokerage_id") or "",
        expires_hours=1,
    )


def forbidden_key_paths(obj: Any, forbidden: set[str], prefix: str = "$") -> list[str]:
    paths: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}"
            if key in forbidden:
                paths.append(path)
            paths.extend(forbidden_key_paths(value, forbidden, path))
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            paths.extend(forbidden_key_paths(value, forbidden, f"{prefix}[{idx}]"))
    return paths


def require_json(parsed: Any) -> None:
    assert isinstance(parsed, (dict, list)), "response was not JSON"


def validate_health(_status, _headers, _text, parsed):
    assert isinstance(parsed, dict), "health response was not JSON"
    assert parsed.get("status") == "ok", f"status={parsed.get('status')!r}"
    assert parsed.get("db") == "ok", f"db={parsed.get('db')!r}"


def validate_auth_providers(_status, _headers, _text, parsed):
    assert isinstance(parsed, dict), "providers response was not JSON"
    assert parsed.get("dev_login") is False, "dev_login should be false in production"


def validate_redirect_to_chat(_status, headers, _text, _parsed):
    location = headers.get("location") or headers.get("Location") or ""
    assert location.endswith("/chat") or location == "/chat", f"location={location!r}"


def validate_redirect_to(expected_path: str):
    def _validator(_status, headers, _text, _parsed):
        location = headers.get("location") or headers.get("Location") or ""
        assert location.endswith(expected_path) or location == expected_path, f"location={location!r}"

    return _validator


def validate_html(_status, headers, text, _parsed):
    content_type = headers.get("content-type") or headers.get("Content-Type") or ""
    assert "text/html" in content_type, f"content-type={content_type!r}"
    assert "<!DOCTYPE html>" in text or "<html" in text.lower(), "HTML shell not found"


def validate_text_contains(expected: str):
    def _validator(_status, _headers, text, _parsed):
        assert expected in text, f"missing {expected!r}"

    return _validator


def validate_role(expected_role: str):
    def _validator(_status, _headers, _text, parsed):
        assert isinstance(parsed, dict), "auth response was not JSON"
        assert parsed.get("role") == expected_role, f"role={parsed.get('role')!r}"

    return _validator


def validate_no_privacy_keys(scope: str):
    def _validator(_status, _headers, _text, parsed):
        require_json(parsed)
        paths = forbidden_key_paths(parsed, FORBIDDEN_PRIVACY_KEYS)
        assert not paths, f"{scope} exposed forbidden key(s): {', '.join(paths[:8])}"

    return _validator


def validate_admin_system(_status, _headers, _text, parsed):
    assert isinstance(parsed, dict), "admin system response was not JSON"
    assert "ops_overview" in parsed, "missing ops_overview"
    assert "background_jobs" in parsed, "missing background_jobs"
    assert "ai_quality" in parsed, "missing ai_quality"
    assert "fub_reliability" in parsed, "missing fub_reliability"
    assert "sender_delivery" in parsed, "missing sender_delivery"
    assert "data_integrity_closeout" in parsed, "missing data_integrity_closeout"
    background_jobs = parsed.get("background_jobs") or {}
    assert isinstance(background_jobs.get("summary"), dict), "missing background_jobs.summary"
    jobs = background_jobs.get("jobs")
    assert isinstance(jobs, list), "missing background_jobs.jobs"
    fub_reliability = parsed.get("fub_reliability") or {}
    assert isinstance(fub_reliability.get("members"), dict), "missing fub_reliability.members"
    assert isinstance(fub_reliability.get("contacts"), dict), "missing fub_reliability.contacts"
    assert fub_reliability.get("contacts", {}).get("basis") == "distinct_fub_contacts", "unexpected FUB contact basis"
    sender_delivery = parsed.get("sender_delivery") or {}
    assert isinstance(sender_delivery.get("members"), dict), "missing sender_delivery.members"
    assert isinstance(sender_delivery.get("drafts"), dict), "missing sender_delivery.drafts"
    assert isinstance(sender_delivery.get("activity_30d"), dict), "missing sender_delivery.activity_30d"
    assert sender_delivery.get("privacy", {}).get("basis") == "aggregate_delivery_signals", "unexpected sender delivery basis"
    data_integrity = parsed.get("data_integrity_closeout") or {}
    assert isinstance(data_integrity.get("checks"), dict), "missing data_integrity_closeout.checks"
    assert isinstance(data_integrity.get("counts"), dict), "missing data_integrity_closeout.counts"
    assert data_integrity.get("checks", {}).get("admin_scope") == "aggregate_only", "unexpected admin scope"
    assert data_integrity.get("checks", {}).get("demo_api_enabled") is False, "demo API should be disabled in production"
    assert any(
        job.get("unit") == "vesta-platform.service" and job.get("classification") == "disabled"
        for job in jobs
    ), "legacy vesta-platform unit should be classified as disabled"
    for key in ("ops_overview", "ai_quality", "fub_reliability", "sender_delivery", "data_integrity_closeout"):
        paths = forbidden_key_paths(parsed.get(key), FORBIDDEN_PRIVACY_KEYS)
        assert not paths, f"{key} exposed forbidden key(s): {', '.join(paths[:8])}"


def validate_broker_health(_status, _headers, _text, parsed):
    assert isinstance(parsed, dict), "broker health response was not JSON"
    assert parsed.get("db") == "ok", f"db={parsed.get('db')!r}"
    assert "cma_jobs" in parsed, "missing cma_jobs"


def validate_investor_snapshot(_status, _headers, _text, parsed):
    assert isinstance(parsed, dict), "investor snapshot response was not JSON"
    assert parsed.get("proof"), "missing proof"
    readiness = (parsed.get("proof") or {}).get("readiness") or {}
    assert readiness.get("status") in {"ready", "needs_context", "not_ready"}, "missing investor readiness status"
    assert isinstance(readiness.get("score"), int), "missing investor readiness score"
    assert isinstance(readiness.get("checks"), list), "missing investor readiness checks"
    assert any(check.get("label") == "Privacy boundary" for check in readiness.get("checks", [])), "missing investor privacy readiness check"
    launch_closeout = parsed.get("launch_closeout") or {}
    assert launch_closeout.get("status") in {"launch_ready", "needs_context", "not_ready"}, "missing investor launch closeout status"
    assert isinstance(launch_closeout.get("checks"), list), "missing investor launch closeout checks"
    assert any(check.get("label") == "Controlled share route" for check in launch_closeout.get("checks", [])), "missing controlled share closeout check"
    assert (launch_closeout.get("privacy") or {}).get("basis") == "aggregate_launch_packaging", "unexpected launch closeout privacy basis"
    assert (launch_closeout.get("privacy") or {}).get("client_records_exposed") is False, "launch closeout client_records_exposed not false"
    privacy = parsed.get("privacy") or {}
    assert privacy.get("client_records_exposed") is False, "client_records_exposed not false"
    paths = forbidden_key_paths(parsed, FORBIDDEN_PRIVACY_KEYS)
    assert not paths, f"investor snapshot exposed forbidden key(s): {', '.join(paths[:8])}"


def validate_investor_shares(_status, _headers, _text, parsed):
    assert isinstance(parsed, dict), "investor shares response was not JSON"
    shares = parsed.get("shares")
    assert isinstance(shares, list), "missing shares list"
    for share in shares:
        follow_up = share.get("follow_up") or {}
        assert follow_up.get("status") in {"viewed", "sent_not_viewed", "expired", "closed"}, "missing share follow-up status"
        assert follow_up.get("priority") in {"high", "medium", "low"}, "missing share follow-up priority"
        assert follow_up.get("basis") == "share_status_view_count_expiry", "unexpected share follow-up basis"
    paths = forbidden_key_paths(parsed, FORBIDDEN_PRIVACY_KEYS)
    assert not paths, f"investor shares exposed forbidden key(s): {', '.join(paths[:8])}"


def run_public_checks(runner: SmokeRunner) -> None:
    runner.expect_status("health", "GET", "/health", 200, validator=validate_health)
    runner.expect_status("auth providers", "GET", "/auth/providers", 200, validator=validate_auth_providers)
    runner.expect_status("demo snapshot disabled", "GET", "/api/demo/snapshot", 404)
    runner.expect_status("demo chat not executable", "POST", "/api/demo/chat", {404, 405}, body={"message": "hello"})
    runner.expect_status("demo simulate not executable", "POST", "/api/demo/simulate-lead", {404, 405})
    runner.expect_status("demo cleanup not executable", "DELETE", "/api/demo/cleanup", {404, 405})
    runner.expect_status("dev login disabled", "GET", "/auth/dev-login", 404)
    runner.expect_status("demo switch disabled", "GET", "/auth/demo-switch?role=agent", 404)
    runner.expect_status("legacy app redirect", "GET", "/app/app.html", 307, validator=validate_redirect_to_chat)
    runner.expect_status("legacy pipeline redirect", "GET", "/app/pipeline", 307, validator=validate_redirect_to("/pipeline"))
    runner.expect_status("legacy unknown app redirect", "GET", "/app/demo", 307, validator=validate_redirect_to_chat)
    runner.expect_status("login page", "GET", "/login", 200, validator=validate_html)
    runner.expect_status("chat SPA shell", "GET", "/chat", 200, validator=validate_html)
    runner.expect_status("pipeline SPA shell", "GET", "/pipeline", 200, validator=validate_html)
    runner.expect_status("approvals SPA shell", "GET", "/approvals", 200, validator=validate_html)
    runner.expect_status("settings SPA shell", "GET", "/settings", 200, validator=validate_html)
    runner.expect_status("team SPA shell", "GET", "/team", 200, validator=validate_html)
    runner.expect_status("broker SPA shell", "GET", "/broker", 200, validator=validate_html)
    runner.expect_status("admin SPA shell", "GET", "/admin", 200, validator=validate_html)
    runner.expect_status("investor SPA shell", "GET", "/investor", 200, validator=validate_html)
    runner.expect_status("onboard SPA shell", "GET", "/onboard", 200, validator=validate_html)
    runner.expect_status("investor share SPA shell", "GET", "/investor/share", 200, validator=validate_html)
    runner.expect_status("service worker", "GET", "/api/ui/sw.js", 200, validator=validate_text_contains("Service Worker"))
    runner.expect_status("PWA manifest", "GET", "/api/ui/manifest.json", 200, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("PWA icon", "GET", "/api/ui/icon-192.png", 200)
    runner.expect_status("pipeline requires auth", "GET", "/api/pipeline/stats", 401)
    runner.expect_status("admin requires auth", "GET", "/api/admin/system", 401)
    runner.expect_status("investor requires auth", "GET", "/api/investor/snapshot", 401)


def run_admin_checks(runner: SmokeRunner, token: str) -> None:
    runner.expect_status("admin auth/me", "GET", "/auth/me", 200, token=token, validator=validate_role("system_admin"))
    runner.expect_status("admin system", "GET", "/api/admin/system", 200, token=token, validator=validate_admin_system)
    runner.expect_status("admin users", "GET", "/api/admin/users", 200, token=token, validator=validate_no_privacy_keys("admin users"))
    runner.expect_status("admin audit", "GET", "/api/admin/audit", 200, token=token, validator=validate_no_privacy_keys("admin audit"))
    runner.expect_status("admin ROI assumptions", "GET", "/api/admin/roi-assumptions", 200, token=token, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("admin investor snapshot", "GET", "/api/investor/snapshot", 200, token=token, validator=validate_investor_snapshot)
    runner.expect_status("admin investor shares", "GET", "/api/investor/shares", 200, token=token, validator=validate_investor_shares)


def run_broker_checks(runner: SmokeRunner, token: str) -> None:
    runner.expect_status("broker auth/me", "GET", "/auth/me", 200, token=token, validator=validate_role("head_broker"))
    runner.expect_status("broker overview", "GET", "/api/broker/overview", 200, token=token, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("broker revenue", "GET", "/api/broker/revenue", 200, token=token, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("broker ROI history", "GET", "/api/broker/roi_history?days=30", 200, token=token, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("broker pipeline value", "GET", "/api/broker/pipeline_value", 200, token=token, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("broker health", "GET", "/api/broker/health", 200, token=token, validator=validate_broker_health)
    runner.expect_status("broker approvals", "GET", "/api/approvals", 200, token=token, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("broker pipeline stats", "GET", "/api/pipeline/stats", 200, token=token, validator=lambda *_args: require_json(_args[3]))
    runner.expect_status("broker investor snapshot", "GET", "/api/investor/snapshot", 200, token=token, validator=validate_investor_snapshot)
    runner.expect_status("broker investor shares", "GET", "/api/investor/shares", 200, token=token, validator=validate_investor_shares)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Vesta baseline smoke checks.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--timeout", type=float, default=8.0)
    parser.add_argument("--public-only", action="store_true", help="Skip local JWT-authenticated checks.")
    parser.add_argument("--admin-email", default=DEFAULT_ADMIN_EMAIL)
    parser.add_argument("--broker-email", default=DEFAULT_BROKER_EMAIL)
    args = parser.parse_args()

    runner = SmokeRunner(args.base_url, timeout=args.timeout)
    run_public_checks(runner)

    if not args.public_only:
        try:
            admin_token = mint_token(args.admin_email)
            run_admin_checks(runner, admin_token)
        except Exception as exc:
            runner.record("admin token setup", False, f"{type(exc).__name__}: {exc}")

        try:
            broker_token = mint_token(args.broker_email)
            run_broker_checks(runner, broker_token)
        except Exception as exc:
            runner.record("broker token setup", False, f"{type(exc).__name__}: {exc}")

    return runner.exit_code()


if __name__ == "__main__":
    raise SystemExit(main())
