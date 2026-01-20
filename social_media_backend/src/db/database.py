import os
import sqlite3
from contextlib import contextmanager
from typing import Any, Dict, List, Optional, Tuple

DB_PATH_ENV = "SQLITE_DB"
DEFAULT_DB_PATH = "data/social_media.db"


def _ensure_data_dir(path: str):
    directory = os.path.dirname(path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def get_db_path() -> str:
    """
    Resolve database path from environment or default.
    """
    return os.getenv(DB_PATH_ENV, DEFAULT_DB_PATH)


def init_db():
    """
    Initialize database with required tables if they do not exist.
    """
    db_path = get_db_path()
    _ensure_data_dir(db_path)
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # Users table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        # Profiles table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                bio TEXT DEFAULT '',
                avatar_url TEXT DEFAULT '',
                location TEXT DEFAULT '',
                website TEXT DEFAULT '',
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        # Posts table
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                likes INTEGER DEFAULT 0,
                comments INTEGER DEFAULT 0,
                shares INTEGER DEFAULT 0,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        # Followers table (simple follower -> followee mapping)
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS followers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL, -- who is followed
                follower_id INTEGER NOT NULL, -- who follows
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, follower_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY(follower_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """
        )
        conn.commit()


@contextmanager
def get_db():
    """
    Context manager to get a SQLite connection with row factory.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def fetch_one_dict(cursor) -> Optional[Dict[str, Any]]:
    row = cursor.fetchone()
    if not row:
        return None
    return {k: row[k] for k in row.keys()}


def fetch_all_dicts(cursor) -> List[Dict[str, Any]]:
    rows = cursor.fetchall()
    return [{k: row[k] for k in row.keys()} for row in rows]


def paginate_query(base_sql: str, params: Tuple[Any, ...], page: int, page_size: int) -> Tuple[str, Tuple[Any, ...]]:
    """
    Apply LIMIT/OFFSET pagination to a base SQL.
    """
    offset = max(page - 1, 0) * page_size
    sql = f"{base_sql} LIMIT ? OFFSET ?"
    new_params = params + (page_size, offset)
    return sql, new_params
