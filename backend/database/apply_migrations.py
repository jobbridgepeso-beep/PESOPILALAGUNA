"""
Apply JobBridge SQL migrations to Supabase PostgreSQL.

Requires DATABASE_URL in backend/.env (Supabase → Settings → Database → Connection string).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

MIGRATIONS_DIR = Path(__file__).parent / "migrations"
MIGRATION_FILES = [
    "001_initial_schema.sql",
    "002_storage_buckets.sql",
    "003_seed_data.sql",
]


def _connect():
    """Connect via DATABASE_URL or discrete DB_* variables (avoids @ in password issues)."""
    import psycopg2

    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        return psycopg2.connect(database_url)

    host = os.getenv("DB_HOST", "").strip()
    user = os.getenv("DB_USER", "").strip()
    password = os.getenv("DB_PASSWORD", "").strip()
    dbname = os.getenv("DB_NAME", "postgres").strip()
    port = os.getenv("DB_PORT", "5432").strip()

    if host and user and password:
        return psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            dbname=dbname,
            sslmode="require",
        )

    raise ValueError(
        "Set DATABASE_URL (URL-encode special chars in password, e.g. @ → %40) "
        "or DB_HOST, DB_USER, DB_PASSWORD in backend/.env"
    )


def main() -> int:
    try:
        import psycopg2  # noqa: F401
    except ImportError:
        print("[ERROR] psycopg2-binary is required. Run: pip install -r requirements.txt")
        return 1

    try:
        print("[INFO] Connecting to Supabase PostgreSQL...")
        conn = _connect()
    except Exception as exc:
        print(f"[ERROR] Database connection failed: {exc}")
        return 1
    conn.autocommit = True

    try:
        with conn.cursor() as cur:
            for name in MIGRATION_FILES:
                path = MIGRATIONS_DIR / name
                if not path.exists():
                    print(f"[WARN] Skipping missing file: {name}")
                    continue
                sql = path.read_text(encoding="utf-8")
                print(f"[INFO] Applying {name}...")
                cur.execute(sql)
                print(f"[OK]   {name}")
    finally:
        conn.close()

    print("[INFO] Migrations complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
