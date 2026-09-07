"""Unified database access layer.

Every database consumer in the app (auth/users, billing state, chart cache,
agent memory) goes through get_connection() so production uses a single
PostgreSQL database while local development still works with SQLite files.

Never import sqlite3/psycopg2 directly in feature code — extend this module.
"""
import os
import sqlite3
import threading
from contextlib import contextmanager

import runtime_config

try:
    import psycopg2
    import psycopg2.extras
except ImportError:
    psycopg2 = None

_local = threading.local()

# Dev-only SQLite file locations (production always uses DATABASE_URL/Postgres)
SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_local.db")


def is_postgres() -> bool:
    return bool(runtime_config.DATABASE_URL) and psycopg2 is not None


def get_connection():
    """Return (conn, db_type) where db_type is 'postgres' or 'sqlite'.

    Postgres connections are per-thread (threading.local) and autocommit;
    SQLite connections are opened per call (cheap, avoids cross-thread issues).
    Callers owning a cursor must commit for sqlite (or use execute_then_commit).
    """
    if is_postgres():
        conn = getattr(_local, "pg_conn", None)
        if conn is None or conn.closed:
            conn = psycopg2.connect(runtime_config.DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
            conn.autocommit = True
            _local.pg_conn = conn
        return conn, "postgres"
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn, "sqlite"


@contextmanager
def cursor():
    """Context manager yielding (cursor, db_type); commits on sqlite on exit."""
    conn, db_type = get_connection()
    cur = conn.cursor()
    try:
        yield cur, db_type
    finally:
        cur.close()
        if db_type == "sqlite":
            conn.commit()
            conn.close()
        # postgres connection stays on the thread; autocommit already applied


def ph(db_type: str) -> str:
    """Parameter placeholder for the active backend."""
    return "%s" if db_type == "postgres" else "?"


def init_schema():
    """Create all application tables if missing. Idempotent — safe to run on
    every boot. Never drops or alters existing data."""
    statements = {
        "users": """
            CREATE TABLE IF NOT EXISTS users (
                id {pk_int},
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                plan TEXT DEFAULT 'free',
                created_at {ts_default}
            )
        """,
        "birth_profiles": """
            CREATE TABLE IF NOT EXISTS birth_profiles (
                user_id {pk_int},
                full_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                birth_time TEXT NOT NULL,
                city TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timezone TEXT NOT NULL,
                updated_at {ts_default}
            )
        """,
        "chart_cache": """
            CREATE TABLE IF NOT EXISTS chart_cache (
                session_id TEXT PRIMARY KEY,
                chart_json TEXT NOT NULL,
                updated_at {ts_default}
            )
        """,
        "agent_memory": """
            CREATE TABLE IF NOT EXISTS agent_memory (
                thread_id TEXT NOT NULL,
                checkpoint {blob} NOT NULL,
                created_at {ts_default}
            )
        """,
        "user_profiles": """
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id TEXT PRIMARY KEY,
                profile_json TEXT,
                updated_at {ts_default}
            )
        """,
        "conversation_corrections": """
            CREATE TABLE IF NOT EXISTS conversation_corrections (
                id {pk_int},
                user_id TEXT,
                correction_type TEXT,
                raw_statement TEXT,
                extracted_fact TEXT,
                created_at {ts_default}
            )
        """,
        "relationship_profiles": """
            CREATE TABLE IF NOT EXISTS relationship_profiles (
                id {pk_int},
                owner_id BIGINT NOT NULL,
                label TEXT NOT NULL,
                relation TEXT DEFAULT 'partner',
                full_name TEXT NOT NULL,
                birth_date TEXT NOT NULL,
                birth_time TEXT NOT NULL,
                city TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timezone TEXT NOT NULL,
                created_at {ts_default}
            )
        """,
        "notification_prefs": """
            CREATE TABLE IF NOT EXISTS notification_prefs (
                user_id BIGINT PRIMARY KEY,
                daily_insight INTEGER DEFAULT 1,
                transit_alert INTEGER DEFAULT 1,
                timing_period INTEGER DEFAULT 1,
                relationship_event INTEGER DEFAULT 0,
                product_updates INTEGER DEFAULT 0,
                appearance TEXT DEFAULT 'system',
                updated_at {ts_default}
            )
        """,
    }
    for sql in statements.values():
        conn, db_type = get_connection()
        cur = conn.cursor()
        cur.execute(sql.format(
            pk_int="BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY" if db_type == "postgres" else "INTEGER PRIMARY KEY AUTOINCREMENT",
            ts_default="TIMESTAMPTZ DEFAULT NOW()" if db_type == "postgres" else "TEXT DEFAULT CURRENT_TIMESTAMP",
            blob="BYTEA" if db_type == "postgres" else "BLOB",
        ))
        if db_type == "sqlite":
            conn.commit()
            conn.close()
        else:
            cur.close()
