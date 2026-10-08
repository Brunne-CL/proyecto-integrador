import os
import sqlite3
from contextlib import contextmanager


def default_db_path():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.environ.get("DB_PATH", os.path.join(root, "data", "users.db"))


def init_db(db_path):
    folder = os.path.dirname(db_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE
            )
            """
        )


@contextmanager
def connect(db_path):
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def to_user(row):
    return {"id": row["id"], "name": row["name"], "email": row["email"]}


def list_users(db_path):
    with connect(db_path) as conn:
        rows = conn.execute(
            "SELECT id, name, email FROM users ORDER BY id"
        ).fetchall()
    return [to_user(row) for row in rows]


def get_user(db_path, user_id):
    with connect(db_path) as conn:
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return to_user(row) if row else None


def create_user(db_path, name, email):
    with connect(db_path) as conn:
        try:
            cur = conn.execute(
                "INSERT INTO users (name, email) VALUES (?, ?)",
                (name, email),
            )
        except sqlite3.IntegrityError:
            return None
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
    return to_user(row)


def update_user(db_path, user_id, name, email):
    with connect(db_path) as conn:
        exists = conn.execute(
            "SELECT 1 FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if exists is None:
            return "missing"
        try:
            conn.execute(
                "UPDATE users SET name = ?, email = ? WHERE id = ?",
                (name, email, user_id),
            )
        except sqlite3.IntegrityError:
            return "duplicate"
        row = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    return to_user(row)


def delete_user(db_path, user_id):
    with connect(db_path) as conn:
        cur = conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
        return cur.rowcount > 0
