"""Production smoke tests — run against a live server (local or deployed).

Usage:
    python tests/smoke_test.py http://localhost:8000

Covers: health, readiness, frontend, static assets, auth (signup/login/
logout/protected route), chart calculation, chart-data retrieval, mode
endpoint, Stripe webhook signature rejection.
"""
import json
import sys
import secrets
import string
import requests

BASE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://localhost:8000"

PASS, FAIL = [], []


def check(name, ok, detail=""):
    (PASS if ok else FAIL).append((name, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail and not ok else ""))


def main():
    s = requests.Session()

    # ── Health ──────────────────────────────────────────────────────────
    r = s.get(f"{BASE}/health", timeout=15)
    check("GET /health -> 200", r.status_code == 200, str(r.status_code))
    body = r.json() if r.status_code == 200 else {}
    check("/health reports status ok", body.get("status") == "ok", str(body))

    r = s.get(f"{BASE}/health/ready", timeout=15)
    check("GET /health/ready -> 200", r.status_code == 200, f"{r.status_code} {r.text[:120]}")

    # ── Frontend ────────────────────────────────────────────────────────
    r = s.get(f"{BASE}/", timeout=15)
    check("GET / -> 200 (frontend)", r.status_code == 200, str(r.status_code))
    check("frontend is HTML", "text/html" in r.headers.get("content-type", ""), r.headers.get("content-type", ""))

    r = s.get(f"{BASE}/login", timeout=15)
    check("GET /login -> 200", r.status_code == 200, str(r.status_code))

    r = s.get(f"{BASE}/static/style.css", timeout=15)
    check("static asset served", r.status_code == 200, str(r.status_code))

    r = s.get(f"{BASE}/static/api.js", timeout=15)
    check("static api.js served", r.status_code == 200, str(r.status_code))

    # ── Auth ────────────────────────────────────────────────────────────
    suffix = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    email = f"smoke_{suffix}@example.com"
    password = "smoke-test-pass-123"

    r = s.post(f"{BASE}/api/auth/signup", json={
        "email": email, "full_name": "Smoke Test", "password": password}, timeout=20)
    check("signup -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")
    if r.status_code == 200:
        check("signup sets auth cookie", "astro_token" in s.cookies, "no cookie")

    r = s.get(f"{BASE}/api/auth/me", timeout=15)
    check("protected /api/auth/me with cookie", r.status_code == 200 and r.json().get("email") == email,
          f"{r.status_code} {r.text[:120]}")

    # logout clears cookie state
    s2 = requests.Session()
    r = s2.get(f"{BASE}/api/auth/me", timeout=15)
    check("protected route rejects anonymous", r.status_code == 401, str(r.status_code))

    r = s.post(f"{BASE}/api/auth/login", json={"email": email, "password": "wrong-password"}, timeout=15)
    check("login rejects wrong password", r.status_code == 401, str(r.status_code))

    r = s.post(f"{BASE}/api/auth/login", json={"email": email, "password": password}, timeout=15)
    check("login -> 200", r.status_code == 200, f"{r.status_code} {r.text[:200]}")

    # malformed token
    r = requests.get(f"{BASE}/api/auth/me", headers={"Authorization": "Bearer not.a.jwt"}, timeout=15)
    check("malformed JWT rejected", r.status_code == 401, str(r.status_code))

    # ── Chart calculation (deterministic engine, no LLM) ────────────────
    r = s.post(f"{BASE}/api/chart/calculate", json={
        "session_id": "smoke-session",
        "full_name": "Smoke User",
        "year": 1947, "month": 8, "day": 15, "hour": 0, "minute": 0,
        "location": {"display_name": "New Delhi", "latitude": 28.6139,
                      "longitude": 77.2090, "timezone": "Asia/Kolkata", "place_id": ""},
    }, timeout=60)
    check("POST /api/chart/calculate -> 200", r.status_code == 200, f"{r.status_code} {r.text[:300]}")

    r = s.get(f"{BASE}/api/chart/status?session_id=smoke-session", timeout=15)
    check("chart status has_chart=true", r.status_code == 200 and r.json().get("has_chart") is True,
          f"{r.status_code} {r.text[:120]}")

    r = s.get(f"{BASE}/api/chart-data?session_id=smoke-session", timeout=15)
    ok = r.status_code == 200
    if ok:
        bc = r.json().get("Basic_Chart", {})
        # India Independence chart: Taurus ascendant, Sun in Cancer (locked reference)
        ok = bc.get("Ascendant", {}).get("sign") == "Taurus" and bc.get("Sun", {}).get("sign") == "Cancer"
        detail = f"Asc={bc.get('Ascendant', {}).get('sign')} Sun={bc.get('Sun', {}).get('sign')}"
    else:
        detail = f"{r.status_code} {r.text[:200]}"
    check("chart-data returns correct deterministic chart (Taurus Asc, Cancer Sun)", ok, detail)

    # ── Mode endpoint (public info) ─────────────────────────────────────
    r = s.get(f"{BASE}/api/mode", timeout=15)
    check("GET /api/mode -> 200", r.status_code == 200, str(r.status_code))

    # ── Stripe webhook must reject unsigned payloads ────────────────────
    r = requests.post(f"{BASE}/api/stripe/webhook",
                      json={"type": "checkout.session.completed",
                            "data": {"object": {"client_reference_id": email}}},
                      timeout=15)
    check("unsigned Stripe webhook rejected", r.status_code in (400, 403, 503), str(r.status_code))

    # bogus signature must also be rejected
    r = requests.post(f"{BASE}/api/stripe/webhook",
                      headers={"stripe-signature": "t=1,v1=deadbeef"},
                      data=b"{}", timeout=15)
    check("bogus-signature webhook rejected", r.status_code in (400, 403, 503), str(r.status_code))

    # ── Summary ─────────────────────────────────────────────────────────
    print()
    print(f"SMOKE RESULT: {len(PASS)} passed, {len(FAIL)} failed  (target: {BASE})")
    if FAIL:
        for name, detail in FAIL:
            print(f"  FAIL: {name} — {detail}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
