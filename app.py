from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from dotenv import load_dotenv

# Make settings available before importing modules that read them at import time.
load_dotenv()

from ai_agent import (
    chart_exists_in_db,
    load_chart,
    run_astrologer,
    run_astrologer_stream,
    save_chart,
)
from auth import init_db, get_user_by_email, create_user, verify_password, create_access_token, decode_access_token, get_user_profile, save_user_profile, set_user_plan
import logging
import os
import hashlib
import stripe
import json
from starlette.responses import StreamingResponse

import runtime_config

# ── Logging (before anything else logs) ─────────────────────────────────────
logging.basicConfig(
    level=getattr(logging, runtime_config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger("app")

# Fail fast on missing production-critical configuration.
runtime_config.validate_production()

# Stripe: no hardcoded fallback key. Missing key in production already failed
# above; in dev an unset key just means checkout returns a clear 503.
stripe.api_key = runtime_config.STRIPE_SECRET_KEY or None

app = FastAPI()

# CORS: the frontend may be served from a different origin than the API
# (e.g. static hosting + API on another domain/port). Default allows only
# same-origin, which browsers enforce anyway — set ALLOWED_ORIGINS in .env
# (comma-separated) to your frontend origin(s) in production.
from fastapi.middleware.cors import CORSMiddleware
_allowed = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed,          # empty list = no cross-origin access (secure default)
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# Init DB on startup
init_db()

# Serve static files for CSS/JS
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

os.makedirs("templates", exist_ok=True)
templates = Jinja2Templates(directory="templates")

security = HTTPBearer(auto_error=False)

# ─── Request Models ───────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default_session"
    debug_mode: bool = False
    provider: str = "auto"

class SignupRequest(BaseModel):
    email: str
    full_name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class GoogleLoginRequest(BaseModel):
    credential: str

class LocationResolution(BaseModel):
    display_name: str
    latitude: float
    longitude: float
    timezone: str
    place_id: str = ""

class ChartCalculationRequest(BaseModel):
    session_id: str
    full_name: str
    year: int
    month: int
    day: int
    hour: int
    minute: int
    location: LocationResolution

class ProfileRequest(BaseModel):
    full_name: str
    date: str
    time: str
    city: str
    lat: float
    lon: float
    timezone: str

# ─── Auth Helper ─────────────────────────────────────────────────
def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Accept auth from EITHER HttpOnly cookie OR Authorization: Bearer header."""
    token = None
    # Prefer cookie (more secure), fall back to Bearer token
    token = request.cookies.get("astro_token")
    if not token and credentials:
        token = credentials.credentials
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user_by_email(payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def chart_session_key(user: dict, session_id: str) -> str:
    """Keep chart cache and agent memory private to the signed-in user."""
    normalized = session_id.strip()
    if not normalized or len(normalized) > 128:
        raise HTTPException(status_code=422, detail="Invalid chart session")
    digest = hashlib.sha256(f"{user['id']}:{normalized}".encode("utf-8")).hexdigest()
    return f"chart-{digest}"

# ─── Stripe Payments ───────────────────────────────────────────────

@app.post("/api/create-checkout-session")
def create_checkout_session(user: dict = Depends(get_current_user)):
    if not stripe.api_key:
        raise HTTPException(status_code=503, detail="Payments are not configured on this deployment")
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Astrology AI Premium',
                        'description': 'Unlimited cosmic readings and overpowered transits.',
                    },
                    'unit_amount': 2900, # $29.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=runtime_config.stripe_success_url(),
            cancel_url=runtime_config.stripe_cancel_url(),
            client_reference_id=user["email"] # Pass email to identify user on webhook
        )
        return {"checkout_url": session.url}
    except stripe.StripeError as e:
        logger.error(f"Stripe checkout session failed: {e}")
        raise HTTPException(status_code=502, detail="Payment provider error. Please try again shortly.")
    except Exception:
        logger.exception("Unexpected error creating checkout session")
        raise HTTPException(status_code=500, detail="Could not create checkout session")

@app.post("/api/stripe/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    endpoint_secret = runtime_config.STRIPE_WEBHOOK_SECRET

    # Signature verification is MANDATORY. No unsigned fallback.
    if not endpoint_secret:
        logger.error("Stripe webhook rejected: STRIPE_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=503, detail="Webhook not configured")
    if not sig_header:
        logger.warning("Stripe webhook rejected: missing stripe-signature header")
        raise HTTPException(status_code=400, detail="Missing signature")

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except (ValueError, stripe.SignatureVerificationError) as e:
        logger.warning(f"Stripe webhook signature verification failed: {type(e).__name__}")
        raise HTTPException(status_code=400, detail="Invalid signature")
    except stripe.StripeError as e:
        logger.error(f"Stripe webhook error: {e}")
        raise HTTPException(status_code=400, detail="Webhook error")

    try:
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_email = session.get('client_reference_id')

            if user_email:
                # Billing state goes to the SAME unified database as auth
                # (PostgreSQL in production) — never a separate SQLite file.
                updated = set_user_plan(user_email, 'premium')
                if updated:
                    logger.info(f"Stripe: upgraded user {user_email} to premium")
                else:
                    logger.warning(f"Stripe: checkout completed for unknown email {user_email}")
        return {"status": "success"}
    except Exception:
        logger.exception("Stripe webhook handler error")
        raise HTTPException(status_code=500, detail="Webhook processing error")

@app.get("/api/user/status")
def get_user_status(user: dict = Depends(get_current_user)):
    return {"plan": user["plan"], "email": user["email"]}

# ─── Pages ───────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def get_ui(request: Request):
    response = templates.TemplateResponse(request=request, name="index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    response = templates.TemplateResponse(request=request, name="login.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

# ─── Auth API ────────────────────────────────────────────────────
@app.post("/api/auth/signup")
async def signup(req: SignupRequest):
    if get_user_by_email(req.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    if len(req.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    user = create_user(req.email, req.full_name, req.password)
    token = create_access_token({"sub": user["email"]})
    from fastapi.responses import JSONResponse
    response = JSONResponse({"token": token, "user": {"email": user["email"], "full_name": user["full_name"], "plan": user["plan"]}})
    response.set_cookie(
        key="astro_token", value=token,
        httponly=True, samesite="lax", max_age=60*60*24*7,
        secure=runtime_config.IS_PRODUCTION,
    )
    return response

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    user = get_user_by_email(req.email)
    if not user or not verify_password(req.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token({"sub": user["email"]})
    from fastapi.responses import JSONResponse
    response = JSONResponse({"token": token, "user": {"email": user["email"], "full_name": user["full_name"], "plan": user["plan"]}})
    response.set_cookie(
        key="astro_token", value=token,
        httponly=True, samesite="lax", max_age=60*60*24*7,
        secure=runtime_config.IS_PRODUCTION,
    )
    return response

@app.post("/api/auth/google")
async def google_login(req: GoogleLoginRequest):
    if not runtime_config.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google Login is not configured")
    
    from google.oauth2 import id_token
    from google.auth.transport import requests
    import secrets

    try:
        # Verify the Google JWT token
        idinfo = id_token.verify_oauth2_token(
            req.credential, 
            requests.Request(), 
            runtime_config.GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        if not email:
            raise ValueError("No email in Google token")
        
        full_name = idinfo.get("name", email.split('@')[0])
        
        # Check if user exists. If not, auto-create a strong random password since they use Google.
        user = get_user_by_email(email)
        if not user:
            random_pw = secrets.token_urlsafe(32)
            user = create_user(email, full_name, random_pw)

        token = create_access_token({"sub": user["email"]})
        from fastapi.responses import JSONResponse
        response = JSONResponse({
            "token": token, 
            "user": {"email": user["email"], "full_name": user["full_name"], "plan": user["plan"]}
        })
        response.set_cookie(
            key="astro_token", value=token,
            httponly=True, samesite="lax", max_age=60*60*24*7,
            secure=runtime_config.IS_PRODUCTION,
        )
        return response

    except ValueError as e:
        logger.warning(f"Google login token verification failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid Google token")

@app.post("/api/auth/logout")
async def logout():
    from fastapi.responses import JSONResponse
    response = JSONResponse({"status": "logged out"})
    response.delete_cookie("astro_token")
    return response

@app.get("/api/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["email"], "full_name": current_user["full_name"], "plan": current_user["plan"]}

@app.get("/api/profile")
async def get_profile_endpoint(current_user: dict = Depends(get_current_user)):
    profile = get_user_profile(current_user["id"])
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@app.post("/api/profile")
async def save_profile_endpoint(req: ProfileRequest, current_user: dict = Depends(get_current_user)):
    profile = save_user_profile(current_user["id"], req.model_dump())
    return profile


@app.get("/api/location/timezone")
async def get_timezone(lat: float, lon: float, current_user: dict = Depends(get_current_user)):
    if not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise HTTPException(status_code=422, detail="Coordinates are out of range")
    from timezonefinder import TimezoneFinder
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lng=lon, lat=lat) or 'UTC'
    return {"timezone": tz_name}


@app.get("/api/locations/search")
async def search_locations(q: str, current_user: dict = Depends(get_current_user)):
    """Resolve cities server-side so CORS and forbidden browser headers cannot break onboarding."""
    query = q.strip()
    if not 2 <= len(query) <= 100:
        raise HTTPException(status_code=422, detail="Enter between 2 and 100 characters")

    import requests

    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params={
                "q": query,
                "format": "jsonv2",
                "addressdetails": 1,
                "limit": 6,
                "featuretype": "city",
            },
            headers={"User-Agent": "AstrologyAI/1.0 (birth-location-search)"},
            timeout=5,
        )
        response.raise_for_status()
        return {"results": response.json()}
    except requests.RequestException as exc:
        raise HTTPException(status_code=503, detail="Location search is temporarily unavailable") from exc

@app.post("/api/chart/calculate")
async def calculate_chart_endpoint(req: ChartCalculationRequest, current_user: dict = Depends(get_current_user)):
    """Deterministically calculate a chart from explicit geographic coordinates."""
    from astrology_engine import calculate_full_chart
    try:
        chart_data = calculate_full_chart(
            req.year, req.month, req.day, 
            req.hour, req.minute, 
            req.location.latitude, req.location.longitude,
            req.location.timezone,
            req.full_name
        )
        save_chart(chart_session_key(current_user, req.session_id), chart_data)
        
        # We also need to persist the location source explicitly if needed
        # but the chart_data metadata now captures the timezone and lat/lon exactly!
        
        return {"status": "success", "session_id": req.session_id}
    except ValueError as e:
        # Bad date/coordinates from the user — their fault, not a server error
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Chart calculation failed")
        raise HTTPException(status_code=500, detail="Chart calculation failed. Please check the birth details and try again.")

@app.get("/api/chart/status")
async def chart_status(session_id: str, current_user: dict = Depends(get_current_user)):
    """Check whether a cached chart exists for this user and session."""
    has_chart = chart_exists_in_db(chart_session_key(current_user, session_id))
    return {"has_chart": has_chart, "session_id": session_id}

@app.get("/api/chart-data")
async def get_chart_data(session_id: str, current_user: dict = Depends(get_current_user)):
    """Return the cached chart JSON for visual rendering in the frontend."""
    chart_data = load_chart(chart_session_key(current_user, session_id))
    if chart_data is None:
        raise HTTPException(status_code=404, detail="Chart not yet calculated")
    return chart_data

@app.get("/api/models")
async def get_models():
    """Fetch available models dynamically from configured gateways."""
    import requests
    import os

    models = [
        {"id": "auto", "name": "✦ Auto (Smart Fallback)", "provider": "auto", "badge": "Smart", "group": "Auto"}
    ]

    # ── OmniRoute local gateway check ──────────────────────────────
    try:
        resp = requests.get("http://localhost:20128/v1/models", timeout=1.0)
        if resp.status_code == 200:
            for m in resp.json().get("data", []):
                m_id = m.get("id", "")
                models.append({
                    "id": f"omniroute:{m_id}",
                    "name": f"OmniRoute: {m_id}",
                    "provider": "omniroute",
                    "badge": "Local Gateway",
                    "group": "OmniRoute"
                })
    except Exception:
        pass

    # ── AgentRouter check ──────────────────────────────────────────
    if os.getenv("AGENTROUTER_API_KEY"):
        # Always add DeepSeek v4 Flash if configured
        models.append({
            "id": "agentrouter:deepseek",
            "name": "AgentRouter: deepseek-v4-flash",
            "provider": "agentrouter",
            "badge": "Premium",
            "group": "AgentRouter"
        })
        try:
            headers = {
                "Authorization": f"Bearer {os.getenv('AGENTROUTER_API_KEY')}",
                "User-Agent": "Cline/1.0.0",
                "X-Requested-With": "XMLHttpRequest"
            }
            resp = requests.get("https://agentrouter.org/v1/models", headers=headers, timeout=2.0)
            if resp.status_code == 200:
                for m in resp.json().get("data", []):
                    m_id = m.get("id", "")
                    if "deepseek" not in m_id.lower(): # Avoid duplicate if it returns it
                        models.append({
                            "id": f"agentrouter:{m_id}",
                            "name": f"AgentRouter: {m_id}",
                            "provider": "agentrouter",
                            "badge": "Premium",
                            "group": "AgentRouter"
                        })
        except Exception:
            pass

    # ── Local Models (Ollama) ───────────────────────────────────────
    try:
        resp = requests.get("http://localhost:11434/api/tags", timeout=1.5)
        if resp.status_code == 200:
            for m in resp.json().get("models", []):
                m_name = m.get("name", "")
                models.append({
                    "id": m_name,
                    "name": f"🖥 {m_name}",
                    "provider": "ollama",
                    "badge": "Local",
                    "group": "Local Ollama"
                })
    except Exception:
        pass
        
    # ── Standard Providers (Google/Groq) ───────────────────────────
    if os.getenv("GOOGLE_API_KEY"):
        models.append({
            "id": "gemini-3.6-flash",
            "name": "Gemini 3.6 Flash",
            "provider": "gemini-3.6-flash",
            "badge": "Standard",
            "group": "Google"
        })
        
    if os.getenv("GROQ_API_KEY"):
        models.append({
            "id": "groq",
            "name": "Groq LLaMA 3.3",
            "provider": "groq",
            "badge": "Fast",
            "group": "Groq"
        })

    if os.getenv("OPENROUTER_API_KEY"):
        models.append({
            "id": "openrouter-nemotron",
            "name": "OpenRouter Nemotron 3.5 (Free)",
            "provider": "openrouter",
            "badge": "Free",
            "group": "OpenRouter"
        })

    return {"models": models}

@app.get("/api/mode")
def get_mode_endpoint():
    """Get active application mode and guardrail configuration."""
    from modes import get_active_mode, get_mode_config
    cfg = get_mode_config()
    return {
        "mode": get_active_mode(),
        "mode_name": getattr(cfg, "MODE_NAME", ""),
        "allow_fatal_timing": getattr(cfg, "ALLOW_FATAL_TIMING", False),
        "attach_disclaimers": getattr(cfg, "ATTACH_DISCLAIMERS", True),
    }

@app.post("/api/mode")
def set_mode_endpoint(mode: str, _admin: dict = Depends(get_current_user)):
    """Switch active application execution mode. Admin-only (authenticated);
    in production the mode is pinned by ASTRO_MODE and cannot be switched."""
    if runtime_config.IS_PRODUCTION:
        raise HTTPException(status_code=403, detail="Mode switching is disabled in production")
    from modes import set_active_mode
    try:
        new_mode = set_active_mode(mode)
        logger.info(f"Mode switched to {new_mode}")
        return {"status": "success", "mode": new_mode}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# ─── Health Checks ────────────────────────────────────────────────
@app.get("/health")
def health():
    """Liveness: process is up. Never depends on optional external services."""
    return {"status": "ok", "env": runtime_config.APP_ENV}

@app.get("/health/ready")
def health_ready():
    """Readiness: process is up AND the primary database answers."""
    import db as _db
    try:
        with _db.cursor() as (cur, _):
            cur.execute("SELECT 1")
            cur.fetchone()
        db_status = "ok"
    except Exception as e:
        logger.error(f"Readiness check failed: DB error: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")
    return {
        "status": "ok",
        "env": runtime_config.APP_ENV,
        "database": db_status,
        "database_backend": "postgres" if _db.is_postgres() else "sqlite(dev)",
    }

@app.get("/api/health/ai")
def health_ai():
    # Sync def on purpose: does blocking chart calcs + HTTP probes. FastAPI runs
    # sync endpoints in a threadpool, so this never blocks the event loop.
    import os
    import requests
    
    # Engine self-test: golden charts + cross-engine consistency (deterministic, no LLM)
    try:
        from engine_self_test import run_golden_checks, probe_providers
        golden = run_golden_checks()
        engine_ok = all(g["ok"] for g in golden.values())
        engine_detail = {
            key: {"ok": g["ok"], "fails": [c["name"] for c in g["checks"] if not c["ok"]]}
            for key, g in golden.items()
        }
    except Exception as e:
        engine_ok = False
        engine_detail = {"self_test_error": str(e)}

    health = {
        "Engine_Self_Test": "PASS" if engine_ok else "FAIL",
        "Golden_Charts": engine_detail,
    }

    # Live provider probes (catches decommissioned models, not just env presence)
    try:
        health.update(probe_providers())
    except Exception as e:
        health["Providers"] = f"PROBE_ERROR: {e}"

    return health


# ─── Core Chat API ───────────────────────────────────────────────
@app.post("/api/chat")
def chat(req: ChatRequest, current_user: dict = Depends(get_current_user)):
    """Non-streaming chat endpoint (backward compatible)."""
    try:
        scoped_session = chart_session_key(current_user, req.session_id)
        had_chart_before = chart_exists_in_db(scoped_session)
        reply = run_astrologer(req.message, scoped_session, req.provider)
        chart_generated = chart_exists_in_db(scoped_session) and not had_chart_before
        return {"reply": reply, "chart_generated": chart_generated}
    except Exception:
        logger.exception("Chat processing failed")
        return {"reply": "The stars are clouded — an unexpected error occurred. Please try again."}


@app.get("/api/chat/stream")
async def chat_stream(message: str, session_id: str = "default", provider: str = "auto",
                      request: Request = None, current_user: dict = Depends(get_current_user)):
    """
    Phase 3: SSE Streaming Chat Endpoint.
    
    Streams agent thought steps as Server-Sent Events so the frontend can show
    live progress (e.g., 'Calculating chart...', 'Consulting ancient texts...')
    instead of a blank 60-90s loading screen.
    
    Frontend usage:
        const source = new EventSource(`/api/chat/stream?message=...&session_id=...`);
        source.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'final') { ... }
            if (data.type === 'thinking') { showThought(data.content); }
        };
    """
    def event_generator():
        try:
            scoped_session = chart_session_key(current_user, session_id)
            for chunk in run_astrologer_stream(message, scoped_session, provider):
                yield f"data: {chunk}\n\n"
        except Exception as e:
            error_data = json.dumps({"type": "error", "content": str(e)})
            yield f"data: {error_data}\n\n"
        finally:
            yield "data: {\"type\": \"done\"}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering for SSE
        }
    )



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
