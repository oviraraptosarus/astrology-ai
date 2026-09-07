import os
import urllib.parse
from datetime import datetime, timedelta, timezone
from typing import Optional
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import JWTError, jwt

import runtime_config
import db

load_dotenv()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def init_db():
    """Initialize the unified schema (users, profiles, chart cache, memory)."""
    db.init_schema()
    # Dev-only convenience seed so local login works out of the box.
    # NEVER runs in production: no default accounts exist there.
    if not runtime_config.IS_PRODUCTION and not get_user_by_email("seeker@cosmos.com"):
        create_user("seeker@cosmos.com", "Cosmic Seeker", "password123")


def get_user_by_email(email: str) -> Optional[dict]:
    with db.cursor() as (cur, db_type):
        cur.execute(f"SELECT * FROM users WHERE email = {db.ph(db_type)}", (email,))
        row = cur.fetchone()
        return dict(row) if row else None


def create_user(email: str, full_name: str, password: str) -> dict:
    hashed = pwd_context.hash(password)
    with db.cursor() as (cur, db_type):
        cur.execute(
            f"INSERT INTO users (email, full_name, hashed_password) VALUES ({db.ph(db_type)}, {db.ph(db_type)}, {db.ph(db_type)})",
            (email, full_name, hashed),
        )
    return get_user_by_email(email)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def set_user_plan(email: str, plan: str) -> bool:
    """Used by the Stripe webhook to record billing state in the SAME database
    as auth/user state."""
    with db.cursor() as (cur, db_type):
        cur.execute(
            f"UPDATE users SET plan = {db.ph(db_type)} WHERE email = {db.ph(db_type)}",
            (plan, email),
        )
        return cur.rowcount > 0


def get_user_profile(user_id: int) -> Optional[dict]:
    with db.cursor() as (cur, db_type):
        cur.execute(f"SELECT * FROM birth_profiles WHERE user_id = {db.ph(db_type)}", (user_id,))
        row = cur.fetchone()
        return dict(row) if row else None


def save_user_profile(user_id: int, data: dict) -> dict:
    if db.is_postgres():
        query = """
            INSERT INTO birth_profiles
            (user_id, full_name, birth_date, birth_time, city, latitude, longitude, timezone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name=excluded.full_name,
                birth_date=excluded.birth_date,
                birth_time=excluded.birth_time,
                city=excluded.city,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                timezone=excluded.timezone,
                updated_at=NOW()
        """
    else:
        query = """
            INSERT INTO birth_profiles
            (user_id, full_name, birth_date, birth_time, city, latitude, longitude, timezone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                full_name=excluded.full_name,
                birth_date=excluded.birth_date,
                birth_time=excluded.birth_time,
                city=excluded.city,
                latitude=excluded.latitude,
                longitude=excluded.longitude,
                timezone=excluded.timezone,
                updated_at=CURRENT_TIMESTAMP
        """
    with db.cursor() as (cur, db_type):
        cur.execute(query, (
            user_id, data['full_name'], data['date'], data['time'],
            data['city'], data['lat'], data['lon'], data['timezone']
        ))
    return get_user_profile(user_id)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, runtime_config.jwt_secret(), algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, runtime_config.jwt_secret(), algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


# ─── Relationship profiles (saved people to compare with) ───────────────────
def list_relationships(owner_id: int) -> list:
    with db.cursor() as (cur, db_type):
        cur.execute(
            f"SELECT * FROM relationship_profiles WHERE owner_id = {db.ph(db_type)} ORDER BY id DESC",
            (owner_id,),
        )
        return [dict(r) for r in cur.fetchall()]


def get_relationship(owner_id: int, rel_id: int) -> Optional[dict]:
    with db.cursor() as (cur, db_type):
        cur.execute(
            f"SELECT * FROM relationship_profiles WHERE owner_id = {db.ph(db_type)} AND id = {db.ph(db_type)}",
            (owner_id, rel_id),
        )
        row = cur.fetchone()
        return dict(row) if row else None


def create_relationship(owner_id: int, data: dict) -> dict:
    with db.cursor() as (cur, db_type):
        p = db.ph(db_type)
        cur.execute(
            f"""INSERT INTO relationship_profiles
                (owner_id, label, relation, full_name, birth_date, birth_time, city, latitude, longitude, timezone)
                VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})""",
            (owner_id, data["label"], data.get("relation", "partner"), data["full_name"],
             data["birth_date"], data["birth_time"], data["city"],
             data["latitude"], data["longitude"], data["timezone"]),
        )
    # Return the newest row for this owner (works on both backends).
    rels = list_relationships(owner_id)
    return rels[0] if rels else {}


def delete_relationship(owner_id: int, rel_id: int) -> bool:
    with db.cursor() as (cur, db_type):
        p = db.ph(db_type)
        cur.execute(
            f"DELETE FROM relationship_profiles WHERE owner_id = {p} AND id = {p}",
            (owner_id, rel_id),
        )
        return cur.rowcount > 0


# ─── Notification / appearance preferences ──────────────────────────────────
_PREF_DEFAULTS = {
    "daily_insight": 1, "transit_alert": 1, "timing_period": 1,
    "relationship_event": 0, "product_updates": 0, "appearance": "system",
}


def get_notification_prefs(user_id: int) -> dict:
    with db.cursor() as (cur, db_type):
        cur.execute(f"SELECT * FROM notification_prefs WHERE user_id = {db.ph(db_type)}", (user_id,))
        row = cur.fetchone()
        if row:
            return dict(row)
    return {"user_id": user_id, **_PREF_DEFAULTS}


def save_notification_prefs(user_id: int, data: dict) -> dict:
    merged = {**_PREF_DEFAULTS, **{k: v for k, v in data.items() if k in _PREF_DEFAULTS}}
    with db.cursor() as (cur, db_type):
        p = db.ph(db_type)
        exists = get_notification_prefs_row_exists(cur, db_type, user_id)
        if exists:
            cur.execute(
                f"""UPDATE notification_prefs SET
                    daily_insight={p}, transit_alert={p}, timing_period={p},
                    relationship_event={p}, product_updates={p}, appearance={p}
                    WHERE user_id={p}""",
                (int(merged["daily_insight"]), int(merged["transit_alert"]), int(merged["timing_period"]),
                 int(merged["relationship_event"]), int(merged["product_updates"]), merged["appearance"], user_id),
            )
        else:
            cur.execute(
                f"""INSERT INTO notification_prefs
                    (user_id, daily_insight, transit_alert, timing_period, relationship_event, product_updates, appearance)
                    VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p})""",
                (user_id, int(merged["daily_insight"]), int(merged["transit_alert"]), int(merged["timing_period"]),
                 int(merged["relationship_event"]), int(merged["product_updates"]), merged["appearance"]),
            )
    return get_notification_prefs(user_id)


def get_notification_prefs_row_exists(cur, db_type, user_id) -> bool:
    cur.execute(f"SELECT 1 FROM notification_prefs WHERE user_id = {db.ph(db_type)}", (user_id,))
    return cur.fetchone() is not None
