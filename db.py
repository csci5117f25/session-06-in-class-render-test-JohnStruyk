from contextlib import contextmanager
import logging
import os

from flask import current_app
import psycopg2
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    """
    Initialize the global connection pool exactly once.
    Safe to call multiple times (e.g., from a Flask hook).
    Requires env var: DATABASE_URL
    """
    global pool
    if pool is not None:
        return
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")
    # psycopg2 recommends using sslmode=require for hosted PG (Neon/Render/Heroku)
    current_app.logger.info("Creating db connection pool")
    pool = ThreadedConnectionPool(1, 100, dsn=database_url, sslmode="require")

def close_pool():
    """Close all connections in the pool (call on app shutdown)."""
    global pool
    if pool is not None:
        pool.closeall()
        pool = None

@contextmanager
def get_db_connection():
    if pool is None:
        raise RuntimeError("DB pool is not initialized. Call db.setup() first.")
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

@contextmanager
def get_db_cursor(commit: bool = False):
    with get_db_connection() as connection:
        cursor = connection.cursor(cursor_factory=DictCursor)
        try:
            yield cursor
            if commit:
                connection.commit()
        finally:
            cursor.close()

def add_person(name: str):
    with get_db_cursor(True) as cur:
        current_app.logger.info("Adding person %s", name)
        cur.execute("INSERT INTO person (name) VALUES (%s)", (name,))

def get_people(page: int = 0, people_per_page: int = 10):
    """Return a list of dict-like rows from 'person'."""
    limit = people_per_page
    offset = page * people_per_page
    with get_db_cursor() as cur:
        cur.execute(
            "SELECT * FROM person ORDER BY person_id LIMIT %s OFFSET %s",
            (limit, offset),
        )
        return cur.fetchall()
