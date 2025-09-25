import os
import psycopg
from psycopg_pool import ConnectionPool

def _dsn() -> str:
    dsn = os.environ["DATABASE_URL"]
    if "sslmode=" not in dsn:
        dsn += ("&sslmode=require" if "?" in dsn else "?sslmode=require")
    return dsn

pool: ConnectionPool | None = None

def setup_pool():
    global pool
    if pool is None:
        pool = ConnectionPool(conninfo=_dsn())

def init_schema():
    sql = """
    CREATE TABLE IF NOT EXISTS guests (
        id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with pool.connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
