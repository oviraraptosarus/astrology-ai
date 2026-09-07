"""Central runtime configuration — environment-aware, fail-fast in production.

Reads DATABASE_URL, JWT_SECRET, APP_ENV, BASE_URL, Stripe + LLM + RAG keys.
Rules:
  * APP_ENV=production  -> critical secrets MUST be set; no insecure fallbacks.
  * APP_ENV=development -> permissive defaults so local dev keeps working.
  * APP_ENV=test        -> like development, plus explicit test overrides.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.getenv("APP_ENV", "development").strip().lower()
if APP_ENV not in ("development", "test", "production"):
    raise RuntimeError(f"Invalid APP_ENV '{APP_ENV}' (use development|test|production)")

IS_PRODUCTION = APP_ENV == "production"
IS_TEST = APP_ENV == "test"

ROOT_DIR = Path(__file__).resolve().parent

# ── Database ────────────────────────────────────────────────────────────────
DATABASE_URL = os.getenv("DATABASE_URL", "").strip()

# ── Secrets ─────────────────────────────────────────────────────────────────
JWT_SECRET = os.getenv("JWT_SECRET", "").strip()

# ── URLs ────────────────────────────────────────────────────────────────────
BASE_URL = os.getenv("BASE_URL", "").strip()          # public origin, no trailing slash

# ── Stripe ──────────────────────────────────────────────────────────────────
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()

# ── LLM providers (all optional; app degrades gracefully) ───────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
AGENTROUTER_API_KEY = os.getenv("AGENTROUTER_API_KEY", "").strip()

# ── CORS ────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]

# ── Logging ─────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()


def _fail_fast(name: str, why: str):
    raise RuntimeError(
        f"Missing required environment variable {name} — required in production. {why}"
    )


# ── Auth & OAuth ────────────────────────────────────────────────────────────
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "1074117408479-85ralktijlkae9v0assa5kqa9s3kpop2.apps.googleusercontent.com").strip()
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "").strip()

def validate_production() -> list:
    """Raise if any production-critical setting is missing. Returns list of
    soft warnings for optional integrations."""
    if not IS_PRODUCTION:
        return []

    if not DATABASE_URL:
        _fail_fast("DATABASE_URL", "Managed PostgreSQL connection string (postgres://...).")
    if not JWT_SECRET or len(JWT_SECRET) < 32:
        _fail_fast("JWT_SECRET", "Random secret >= 32 chars (e.g. `openssl rand -hex 32`).")
    if not BASE_URL or not BASE_URL.startswith("https://"):
        _fail_fast("BASE_URL", "Public HTTPS origin of the deployment, e.g. https://astro.example.com")

    # If either Stripe key is provided, both must be provided
    if bool(STRIPE_SECRET_KEY) != bool(STRIPE_WEBHOOK_SECRET):
        _fail_fast("STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET",
                   "Both STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET must be configured together.")

    warnings = []
    if not STRIPE_SECRET_KEY:
        warnings.append("Stripe payments not configured (STRIPE_SECRET_KEY / STRIPE_WEBHOOK_SECRET unset) — payment endpoints will return 503.")
    if not (GOOGLE_API_KEY or GROQ_API_KEY or OPENROUTER_API_KEY or AGENTROUTER_API_KEY):
        warnings.append("No LLM provider key set (GOOGLE_API_KEY/GROQ_API_KEY/OPENROUTER_API_KEY/AGENTROUTER_API_KEY) — AI chat will be degraded.")
    if warnings:
        for w in warnings:
            print(f"[config] WARNING: {w}")
    return warnings


def jwt_secret() -> str:
    """JWT signing secret. Production fails fast; dev/test get a stable local
    secret so tokens survive restarts during development."""
    if IS_PRODUCTION:
        if not JWT_SECRET:
            _fail_fast("JWT_SECRET", "Random secret >= 32 chars.")
        return JWT_SECRET
    return JWT_SECRET or "dev-only-insecure-secret-do-not-use-in-production"


def stripe_success_url() -> str:
    base = BASE_URL or "http://localhost:8000"
    return f"{base}/?payment=success"


def stripe_cancel_url() -> str:
    base = BASE_URL or "http://localhost:8000"
    return f"{base}/?payment=cancelled"
