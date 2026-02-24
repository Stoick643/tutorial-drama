"""
ABOUTME: Admin settings module — stores tutorial visibility in SQLite.
ABOUTME: Used for progressive disclosure: enable/disable tutorials for all visitors.
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = os.environ.get("SETTINGS_DB", str(Path(__file__).resolve().parent.parent / "data" / "settings.db"))


def _get_admin_password():
    """Read admin password at call time (after load_dotenv)."""
    return os.environ.get("ADMIN_PASSWORD", "")

# All known tutorials
ALL_TUTORIALS = ["redis", "sql", "git", "docker", "llm", "bash"]


def _get_db():
    """Get a database connection, creating tables if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tutorial_visibility (
            topic TEXT PRIMARY KEY,
            enabled INTEGER NOT NULL DEFAULT 1
        )
    """)
    conn.commit()
    return conn


def _ensure_all_topics(conn):
    """Ensure all known tutorials have a row (default: enabled)."""
    existing = {row[0] for row in conn.execute("SELECT topic FROM tutorial_visibility").fetchall()}
    for topic in ALL_TUTORIALS:
        if topic not in existing:
            conn.execute("INSERT INTO tutorial_visibility (topic, enabled) VALUES (?, 1)", (topic,))
    conn.commit()


def get_enabled_tutorials() -> list[str]:
    """Return list of enabled tutorial topic names."""
    conn = _get_db()
    _ensure_all_topics(conn)
    rows = conn.execute("SELECT topic FROM tutorial_visibility WHERE enabled = 1 ORDER BY topic").fetchall()
    conn.close()
    return [row[0] for row in rows]


def get_all_tutorial_states() -> dict[str, bool]:
    """Return dict of {topic: enabled} for all tutorials."""
    conn = _get_db()
    _ensure_all_topics(conn)
    rows = conn.execute("SELECT topic, enabled FROM tutorial_visibility ORDER BY topic").fetchall()
    conn.close()
    return {row[0]: bool(row[1]) for row in rows}


def set_tutorial_enabled(topic: str, enabled: bool):
    """Enable or disable a tutorial."""
    conn = _get_db()
    _ensure_all_topics(conn)
    conn.execute("UPDATE tutorial_visibility SET enabled = ? WHERE topic = ?", (1 if enabled else 0, topic))
    conn.commit()
    conn.close()


def update_tutorial_states(states: dict[str, bool]):
    """Bulk update tutorial visibility."""
    conn = _get_db()
    _ensure_all_topics(conn)
    for topic, enabled in states.items():
        conn.execute("UPDATE tutorial_visibility SET enabled = ? WHERE topic = ?", (1 if enabled else 0, topic))
    conn.commit()
    conn.close()


def check_password(password: str) -> bool:
    """Check admin password. Returns False if no password is configured."""
    admin_pw = _get_admin_password()
    if not admin_pw:
        return False
    return password == admin_pw
