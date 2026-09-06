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
