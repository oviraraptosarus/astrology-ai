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
from auth import (
    init_db, get_user_by_email, create_user, verify_password,
    create_access_token, decode_access_token, get_user_profile, save_user_profile, set_user_plan,
    list_relationships, get_relationship, create_relationship, delete_relationship,
    get_notification_prefs, save_notification_prefs,
)
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

class RelationshipRequest(BaseModel):
    label: str
    relation: str = "partner"
    full_name: str
    birth_date: str          # YYYY-MM-DD
    birth_time: str          # HH:MM
    city: str
    latitude: float
    longitude: float
    timezone: str

class NotificationPrefRequest(BaseModel):
    daily_insight: bool = True
    transit_alert: bool = True
    timing_period: bool = True
    relationship_event: bool = False
    product_updates: bool = False
    appearance: str = "system"   # system | light | dark

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


def _parse_birth(date_str: str, time_str: str):
    """Parse 'YYYY-MM-DD' + 'HH:MM' into (y, mo, d, h, mi). Raises ValueError."""
    from datetime import datetime as _dt
    d = _dt.strptime(date_str.strip(), "%Y-%m-%d")
    t = _dt.strptime(time_str.strip(), "%H:%M")
    return d.year, d.month, d.day, t.hour, t.minute


def build_user_chart(user: dict):
    """Load-or-compute the signed-in user's authoritative chart from their saved
    birth profile. Cached per-user under a key that changes when birth data
    changes, so a corrected profile recomputes automatically. Returns the full
    engine chart dict, or None if the user has no birth profile yet."""
    profile = get_user_profile(user["id"])
    if not profile:
        return None
    # Cache key includes the birth fingerprint so edits invalidate the cache.
    fp = f"{profile['birth_date']}|{profile['birth_time']}|{profile['latitude']}|{profile['longitude']}|{profile['timezone']}|{profile['full_name']}"
    key = chart_session_key(user, "primary:" + hashlib.sha256(fp.encode()).hexdigest()[:16])
    cached = load_chart(key)
    if cached is not None:
        return cached
    from astrology_engine import calculate_full_chart
    y, mo, d, h, mi = _parse_birth(profile["birth_date"], profile["birth_time"])
    chart = calculate_full_chart(
        y, mo, d, h, mi,
        float(profile["latitude"]), float(profile["longitude"]),
        profile["timezone"], profile["full_name"],
    )
    save_chart(key, chart)
    return chart


def _require_chart(user: dict):
    chart = build_user_chart(user)
    if chart is None:
        raise HTTPException(status_code=404, detail="No birth profile yet")
    return chart

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
async def get_landing(request: Request):
    """Public landing / welcome page."""
    response = templates.TemplateResponse(request=request, name="landing.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.get("/app", response_class=HTMLResponse)
async def get_app_shell(request: Request):
    """The installable product shell (SPA). Auth is enforced per-API-call."""
    response = templates.TemplateResponse(request=request, name="app.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.get("/app/{path:path}", response_class=HTMLResponse)
async def get_app_deep_link(path: str, request: Request):
    """Deep links (e.g. /app/chart) resolve to the same SPA shell; the client
    router renders the right screen."""
    response = templates.TemplateResponse(request=request, name="app.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    return response


@app.get("/chat", response_class=HTMLResponse)
async def get_chat_ui(request: Request):
    """Legacy conversational UI, preserved."""
    response = templates.TemplateResponse(request=request, name="index.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/manifest.webmanifest")
@app.get("/manifest.json")
async def web_manifest():
    """PWA manifest served at root scope so the whole app is installable."""
    from fastapi.responses import JSONResponse as _JSON
    manifest = {
        "name": "Astrology AI — Cosmic Guide",
        "short_name": "Astrology AI",
        "description": "Your personal Vedic astrology, read simply.",
        "id": "/app",
        "start_url": "/app",
        "scope": "/",
        "display": "standalone",
        "display_override": ["standalone", "minimal-ui"],
        "orientation": "portrait",
        "background_color": "#0b0b0f",
        "theme_color": "#0b0b0f",
        "categories": ["lifestyle", "health"],
        "icons": [
            {"src": "/static/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
            {"src": "/static/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
            {"src": "/static/icons/icon-maskable-192.png", "sizes": "192x192", "type": "image/png", "purpose": "maskable"},
            {"src": "/static/icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
        ],
        "shortcuts": [
            {"name": "My Chart", "url": "/app/chart"},
            {"name": "Forecast", "url": "/app/forecast"},
        ],
    }
    resp = _JSON(manifest, media_type="application/manifest+json")
    resp.headers["Cache-Control"] = "public, max-age=3600"
    return resp


@app.get("/sw.js")
async def service_worker():
    """Service worker MUST be served at root scope to control /app and /static."""
    from fastapi.responses import FileResponse
    resp = FileResponse(os.path.join("static", "sw.js"), media_type="application/javascript")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["Service-Worker-Allowed"] = "/"
    return resp


@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request):
    response = templates.TemplateResponse(request=request, name="login.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.get("/legal", response_class=HTMLResponse)
async def get_legal(request: Request):
    """Standalone public Terms of Service / Privacy Policy page."""
    response = templates.TemplateResponse(request=request, name="legal.html")
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
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

# ─── Product API (consumer product layer over the engine) ────────────────────
import product_api as product


@app.get("/api/product/summary")
async def product_summary(current_user: dict = Depends(get_current_user)):
    """Lightweight bootstrap: whether the user has a profile + basic identity.
    Used by the app shell to decide onboarding vs. home."""
    profile = get_user_profile(current_user["id"])
    prefs = get_notification_prefs(current_user["id"])
    result = {
        "user": {"email": current_user["email"], "full_name": current_user["full_name"], "plan": current_user["plan"]},
        "has_profile": profile is not None,
        "appearance": prefs.get("appearance", "system"),
    }
    if profile:
        result["profile"] = {
            "full_name": profile["full_name"], "birth_date": profile["birth_date"],
            "birth_time": profile["birth_time"], "city": profile["city"],
            "timezone": profile["timezone"],
        }
    return result


@app.get("/api/product/home")
async def product_home(current_user: dict = Depends(get_current_user)):
    chart = _require_chart(current_user)
    return product.home_overview(chart, current_user["full_name"])


@app.get("/api/product/chart")
async def product_chart(current_user: dict = Depends(get_current_user)):
    chart = _require_chart(current_user)
    return product.chart_summary(chart)


@app.get("/api/product/planet/{name}")
async def product_planet(name: str, current_user: dict = Depends(get_current_user)):
    chart = _require_chart(current_user)
    p = chart.get("Basic_Chart", {}).get(name.capitalize())
    if not p:
        raise HTTPException(status_code=404, detail="Unknown planet")
    return product.planet_card(name.capitalize(), p, deep=True)


@app.get("/api/product/forecast")
async def product_forecast(current_user: dict = Depends(get_current_user)):
    from astrology_engine import get_semantic_view
    chart = _require_chart(current_user)
    return product.forecast_overview(get_semantic_view, chart)


@app.get("/api/product/forecast/{domain}")
async def product_forecast_domain(domain: str, current_user: dict = Depends(get_current_user)):
    from astrology_engine import get_semantic_view
    valid = {"career", "marriage", "wealth", "health"}
    if domain not in valid:
        raise HTTPException(status_code=404, detail="Unknown forecast area")
    chart = _require_chart(current_user)
    return product.domain_forecast(get_semantic_view, chart, domain)


@app.get("/api/product/calendar")
async def product_calendar(current_user: dict = Depends(get_current_user)):
    chart = _require_chart(current_user)
    return product.calendar_view(chart)


# ─── Relationships ────────────────────────────────────────────────────────────
@app.get("/api/product/relationships")
async def product_relationships(current_user: dict = Depends(get_current_user)):
    rels = list_relationships(current_user["id"])
    # Never leak precise coordinates back to the client; the label/relation are enough.
    return {"relationships": [
        {"id": r["id"], "label": r["label"], "relation": r["relation"],
         "full_name": r["full_name"], "birth_date": r["birth_date"], "city": r["city"]}
        for r in rels
    ]}


@app.post("/api/product/relationships")
async def product_add_relationship(req: RelationshipRequest, current_user: dict = Depends(get_current_user)):
    try:
        _parse_birth(req.birth_date, req.birth_time)
    except ValueError:
        raise HTTPException(status_code=422, detail="Birth date/time must be YYYY-MM-DD and HH:MM")
    if not (-90 <= req.latitude <= 90 and -180 <= req.longitude <= 180):
        raise HTTPException(status_code=422, detail="Coordinates out of range")
    rel = create_relationship(current_user["id"], req.model_dump())
    return {"id": rel.get("id"), "label": rel.get("label"), "relation": rel.get("relation"),
            "full_name": rel.get("full_name"), "birth_date": rel.get("birth_date"), "city": rel.get("city")}


@app.delete("/api/product/relationships/{rel_id}")
async def product_delete_relationship(rel_id: int, current_user: dict = Depends(get_current_user)):
    ok = delete_relationship(current_user["id"], rel_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Relationship not found")
    return {"status": "deleted"}


@app.get("/api/product/relationships/{rel_id}/compatibility")
async def product_compatibility(rel_id: int, current_user: dict = Depends(get_current_user)):
    """Compute Ashtakoota compatibility between the user and a saved person.
    Authorization: the relationship MUST belong to the requesting user — a user
    can never read another user's saved person by guessing an id."""
    import swisseph as swe
    from config import Config
    from datetime import datetime as _dt
    from astrology_engine import calculate_compatibility, ZODIAC_SIGNS

    rel = get_relationship(current_user["id"], rel_id)
    if not rel:
        raise HTTPException(status_code=404, detail="Relationship not found")

    chart = _require_chart(current_user)
    p1_sign = chart["Basic_Chart"]["Moon"]["sign"]
    p1_deg = chart["Basic_Chart"]["Moon"]["degree"]
    m1_lon = (ZODIAC_SIGNS.index(p1_sign) * 30) + p1_deg

    try:
        y, mo, d, h, mi = _parse_birth(rel["birth_date"], rel["birth_time"])
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        jd2 = swe.julday(y, mo, d, h + mi / 60.0)
        res_moon2, _ = swe.calc_ut(jd2, swe.MOON, flags)
        m2_lon = res_moon2[0]
        compat = calculate_compatibility(m1_lon, m2_lon)
    except Exception:
        logger.exception("Compatibility calculation failed")
        raise HTTPException(status_code=500, detail="Could not compute compatibility")

    return product.compatibility_summary(compat, rel["label"], rel["relation"])


# ─── Notification / appearance preferences ────────────────────────────────────
@app.get("/api/product/preferences")
async def product_get_prefs(current_user: dict = Depends(get_current_user)):
    prefs = get_notification_prefs(current_user["id"])
    prefs.pop("user_id", None)
    prefs.pop("updated_at", None)
    # Normalise integer flags to booleans for the client.
    for k in ("daily_insight", "transit_alert", "timing_period", "relationship_event", "product_updates"):
        prefs[k] = bool(prefs.get(k))
    return prefs


@app.post("/api/product/preferences")
async def product_save_prefs(req: NotificationPrefRequest, current_user: dict = Depends(get_current_user)):
    if req.appearance not in ("system", "light", "dark"):
        raise HTTPException(status_code=422, detail="Invalid appearance")
    saved = save_notification_prefs(current_user["id"], req.model_dump())
    saved.pop("user_id", None)
    saved.pop("updated_at", None)
    for k in ("daily_insight", "transit_alert", "timing_period", "relationship_event", "product_updates"):
        saved[k] = bool(saved.get(k))
    return saved


@app.get("/api/models")
async def get_models():
    """Return only the smart auto fallback model."""
    return {
        "models": [
            {"id": "auto", "name": "✦ Auto (Smart Fallback)", "provider": "auto", "badge": "Smart", "group": "Auto"}
        ]
    }

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
        if not chart_exists_in_db(scoped_session):
            chart = build_user_chart(current_user)
            if chart:
                save_chart(scoped_session, chart)
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
    """
    scoped_session = chart_session_key(current_user, session_id)
    if not chart_exists_in_db(scoped_session):
        chart = build_user_chart(current_user)
        if chart:
            save_chart(scoped_session, chart)

    def event_generator():
        try:
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
