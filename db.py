""" database access helpers """

from contextlib import contextmanager
import os
from flask import current_app
from psycopg2.pool import ThreadedConnectionPool
from psycopg2.extras import DictCursor

pool = None

def setup():
    global pool
    DATABASE_URL = os.environ["DATABASE_URL"]
    current_app.logger.info("Creating DB connection pool")
    pool = ThreadedConnectionPool(1, 10, dsn=DATABASE_URL, sslmode="require")

@contextmanager
def get_db_connection():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

@contextmanager
def get_db_cursor(commit=False):
    with get_db_connection() as conn:
        cur = conn.cursor(cursor_factory=DictCursor)
        try:
            yield cur
            if commit:
                conn.commit()
        finally:
            cur.close()
