"""SQLite-backed stores with atomic read/modify/write operations."""
from __future__ import annotations

from contextvars import ContextVar
from functools import wraps
import json
from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "app.sqlite3"
_connection = ContextVar("database_connection", default=None)


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH, timeout=30) as db:
        db.execute("CREATE TABLE IF NOT EXISTS store (name TEXT PRIMARY KEY, value TEXT NOT NULL)")


def load(namespace, default):
    init_db()
    with sqlite3.connect(DB_PATH, timeout=30) as db:
        row = db.execute("SELECT value FROM store WHERE name=?", (namespace,)).fetchone()
    return json.loads(row[0]) if row else default


def save(namespace, value):
    init_db()
    with sqlite3.connect(DB_PATH, timeout=30) as db:
        db.execute("INSERT INTO store(name,value) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value", (namespace, json.dumps(value, ensure_ascii=False)))
        db.commit()


def persistent(namespace, fields):
    """Reload stores under a SQLite write lock; nested calls share the transaction."""
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            if _connection.get() is not None:
                return function(*args, **kwargs)
            init_db()
            db = sqlite3.connect(DB_PATH, timeout=30)
            token = _connection.set(db)
            try:
                db.execute("BEGIN IMMEDIATE")
                for field in fields:
                    name = f"{namespace}.{field}"
                    row = db.execute("SELECT value FROM store WHERE name=?", (name,)).fetchone()
                    if row:
                        value = json.loads(row[0])
                        if field == "LIKES":
                            value = {key: set(users) for key, users in value.items()}
                        function.__globals__[field] = value
                result = function(*args, **kwargs)
                for field in fields:
                    value = function.__globals__[field]
                    if field == "LIKES":
                        value = {key: sorted(users) for key, users in value.items()}
                    db.execute(
                        "INSERT INTO store(name,value) VALUES(?,?) ON CONFLICT(name) DO UPDATE SET value=excluded.value",
                        (f"{namespace}.{field}", json.dumps(value, ensure_ascii=False)),
                    )
                db.commit()
                return result
            except BaseException:
                db.rollback()
                raise
            finally:
                _connection.reset(token)
                db.close()
        return wrapped
    return decorate
