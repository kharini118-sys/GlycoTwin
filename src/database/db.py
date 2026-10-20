"""
GlycoTwin — Database Layer
SQLite-backed persistence for users, preferences, and workspaces.

Security notes:
  - Passwords are NEVER stored or retrieved in plaintext.
  - All queries use parameterized statements (no string interpolation).
  - Database is in instance/ (excluded from Git).
  - This is a local prototype auth system; it is NOT suitable for
    production multi-user deployment without a hardened backend.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime, timezone

# ── Path configuration ────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[3]
INSTANCE_DIR = PROJECT_ROOT / "instance"
DB_PATH = INSTANCE_DIR / "glycotwin.db"


def get_connection() -> sqlite3.Connection:
    """Return a thread-local SQLite connection with foreign keys enabled."""
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    return conn


def init_db() -> None:
    """Create all required tables if they do not already exist."""
    conn = get_connection()
    try:
        with conn:
            # ── Users ─────────────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    display_name    TEXT    NOT NULL,
                    email           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
                    password_hash   TEXT    NOT NULL,
                    role            TEXT    NOT NULL DEFAULT 'researcher',
                    institution     TEXT,
                    status          TEXT    NOT NULL DEFAULT 'active',
                    terms_accepted  TEXT,
                    created_at      TEXT    NOT NULL,
                    last_login      TEXT
                );
            """)

            # ── User preferences ───────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id             INTEGER PRIMARY KEY,
                    theme               TEXT    DEFAULT 'dark',
                    default_tab         TEXT    DEFAULT 'overview',
                    preferred_chart     TEXT    DEFAULT 'line',
                    preferred_cohort    TEXT    DEFAULT 'all',
                    last_participant    TEXT,
                    preferred_units     TEXT    DEFAULT 'mg/dL',
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)

            # ── Saved workspaces ────────────────────────────────────────────────
            conn.execute("""
                CREATE TABLE IF NOT EXISTS workspaces (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id         INTEGER NOT NULL,
                    name            TEXT    NOT NULL,
                    cohort          TEXT,
                    participant_id  TEXT,
                    replay_index    INTEGER DEFAULT 0,
                    visualization   TEXT    DEFAULT 'glucose',
                    scenario_json   TEXT,
                    notes           TEXT,
                    model_version   TEXT,
                    created_at      TEXT    NOT NULL,
                    updated_at      TEXT    NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                );
            """)
    finally:
        conn.close()


# ── User CRUD ─────────────────────────────────────────────────────────────────

def create_user(
    display_name: str,
    email: str,
    password_hash: str,
    role: str = "researcher",
    institution: str = "",
) -> int:
    """Insert a new user. Returns the new user ID."""
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            cursor = conn.execute(
                """
                INSERT INTO users
                    (display_name, email, password_hash, role, institution,
                     status, terms_accepted, created_at)
                VALUES (?, ?, ?, ?, ?, 'active', ?, ?)
                """,
                (display_name, email.strip().lower(), password_hash, role,
                 institution or "", now, now),
            )
            user_id = cursor.lastrowid
            # Create default preferences row
            conn.execute(
                "INSERT INTO user_preferences (user_id) VALUES (?)",
                (user_id,),
            )
            return user_id
    finally:
        conn.close()


def get_user_by_email(email: str) -> sqlite3.Row | None:
    """Fetch a user row by email (case-insensitive). Returns None if not found."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM users WHERE email = ? COLLATE NOCASE",
            (email.strip().lower(),),
        ).fetchone()
        return row
    finally:
        conn.close()


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    """Fetch a user row by ID."""
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


def update_last_login(user_id: int) -> None:
    now = datetime.now(timezone.utc).isoformat()
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                "UPDATE users SET last_login = ? WHERE id = ?",
                (now, user_id),
            )
    finally:
        conn.close()


def email_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


# ── Preferences CRUD ─────────────────────────────────────────────────────────

def get_preferences(user_id: int) -> sqlite3.Row | None:
    conn = get_connection()
    try:
        return conn.execute(
            "SELECT * FROM user_preferences WHERE user_id = ?", (user_id,)
        ).fetchone()
    finally:
        conn.close()


def save_preferences(user_id: int, **kwargs) -> None:
    """Update any subset of preference columns."""
    allowed = {
        "theme", "default_tab", "preferred_chart",
        "preferred_cohort", "last_participant", "preferred_units",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return
    cols = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [user_id]
    conn = get_connection()
    try:
        with conn:
            conn.execute(
                f"UPDATE user_preferences SET {cols} WHERE user_id = ?", vals
            )
    finally:
        conn.close()


# ── Workspace CRUD ───────────────────────────────────────────────────────────

def create_workspace(user_id: int, name: str, **kwargs) -> int:
    now = datetime.now(timezone.utc).isoformat()
    scenario_json = json.dumps(kwargs.get("scenario", {}))
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute(
                """
                INSERT INTO workspaces
                    (user_id, name, cohort, participant_id, replay_index,
                     visualization, scenario_json, notes, model_version,
                     created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    name,
                    kwargs.get("cohort", "all"),
                    str(kwargs.get("participant_id", "")),
                    int(kwargs.get("replay_index", 0)),
                    kwargs.get("visualization", "glucose"),
                    scenario_json,
                    kwargs.get("notes", ""),
                    kwargs.get("model_version", "glycotwin_logistic_calibrated"),
                    now,
                    now,
                ),
            )
            return cur.lastrowid
    finally:
        conn.close()


def get_workspaces(user_id: int) -> list:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM workspaces WHERE user_id = ? ORDER BY updated_at DESC",
            (user_id,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_workspace(workspace_id: int, user_id: int) -> dict | None:
    """Fetch a workspace only if it belongs to user_id (authorization check)."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM workspaces WHERE id = ? AND user_id = ?",
            (workspace_id, user_id),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_workspace(workspace_id: int, user_id: int, **kwargs) -> bool:
    allowed = {
        "name", "cohort", "participant_id", "replay_index",
        "visualization", "notes", "model_version",
    }
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if "scenario" in kwargs:
        updates["scenario_json"] = json.dumps(kwargs["scenario"])
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    cols = ", ".join(f"{k} = ?" for k in updates)
    vals = list(updates.values()) + [workspace_id, user_id]
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute(
                f"UPDATE workspaces SET {cols} WHERE id = ? AND user_id = ?",
                vals,
            )
            return cur.rowcount > 0
    finally:
        conn.close()


def delete_workspace(workspace_id: int, user_id: int) -> bool:
    conn = get_connection()
    try:
        with conn:
            cur = conn.execute(
                "DELETE FROM workspaces WHERE id = ? AND user_id = ?",
                (workspace_id, user_id),
            )
            return cur.rowcount > 0
    finally:
        conn.close()
