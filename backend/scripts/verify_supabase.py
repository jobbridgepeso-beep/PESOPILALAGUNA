"""
Verify Supabase connection and that core tables are reachable.

Usage:
    cd backend
    python scripts/verify_supabase.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

TABLES = [
    "users",
    "otp_tokens",
    "jobseeker_profiles",
    "employer_profiles",
    "job_vacancies",
    "job_applications",
    "notifications",
    "audit_trail",
    "system_settings",
]


def main() -> int:
    url = os.getenv("SUPABASE_URL", "").strip()
    key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

    if not url or not key:
        print("[FAIL] SUPABASE_URL or SUPABASE_SERVICE_KEY missing in backend/.env")
        return 1

    try:
        from supabase import create_client
    except ImportError:
        print("[FAIL] pip install -r requirements.txt")
        return 1

    print(f"[INFO] Project: {url}")
    client = create_client(url, key)
    ok = True

    for table in TABLES:
        try:
            r = client.table(table).select("id", count="exact").limit(1).execute()
            count = r.count if r.count is not None else len(r.data or [])
            print(f"  [OK]   {table}: {count} row(s)")
        except Exception as exc:
            print(f"  [FAIL] {table}: {exc}")
            ok = False

    print()
    if ok:
        print("[SUCCESS] Supabase is connected. Auth & data save to these tables.")
        print("          Register/login writes to: users, otp_tokens, profiles, audit_trail")
    else:
        print("[ERROR] Some tables failed. Run: python database/apply_migrations.py")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
