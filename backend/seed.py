"""
seed.py — JobBridge Database Seeder
====================================
Inserts the pre-seeded Admin user and default system_settings rows into the
Supabase PostgreSQL database using the SERVICE KEY (bypasses RLS).

Usage:
    cd backend
    python seed.py

Requirements: 3.8, 18.1
"""

import os
import sys

import bcrypt
from dotenv import load_dotenv
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# 1. Load environment variables from backend/.env
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("[ERROR] SUPABASE_URL or SUPABASE_SERVICE_KEY is not set in .env")
    sys.exit(1)

# ---------------------------------------------------------------------------
# 2. Connect to Supabase using the SERVICE KEY (bypasses RLS)
# ---------------------------------------------------------------------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
print(f"[INFO] Connected to Supabase: {SUPABASE_URL}")

# ---------------------------------------------------------------------------
# 3. Seed Admin user
# ---------------------------------------------------------------------------
ADMIN_EMAIL = "admin@jobbridge.ph"
ADMIN_PASSWORD = "Admin@JobBridge2026"
ADMIN_ROLE = "admin"

def seed_admin() -> None:
    """Insert the pre-seeded Admin account if it does not already exist."""
    print("\n--- Seeding Admin user ---")

    # Check if admin already exists
    existing = (
        supabase.table("users")
        .select("id, email")
        .eq("email", ADMIN_EMAIL)
        .execute()
    )

    password_bytes = ADMIN_PASSWORD.encode("utf-8")
    password_hash = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12)).decode("utf-8")

    if existing.data:
        row = existing.data[0]
        current = (
            supabase.table("users")
            .select("password_hash")
            .eq("id", row["id"])
            .single()
            .execute()
        )
        stored = (current.data or {}).get("password_hash", "")
        if stored and stored.startswith("$2b$") and "PLACEHOLDER" not in stored:
            print(f"[SKIP] Admin user '{ADMIN_EMAIL}' already exists — skipping insert.")
            return
        supabase.table("users").update({"password_hash": password_hash}).eq(
            "id", row["id"]
        ).execute()
        print(f"[OK]   Admin password hash updated for '{ADMIN_EMAIL}'.")
        return

    admin_record = {
        "email": ADMIN_EMAIL,
        "password_hash": password_hash,
        "role": ADMIN_ROLE,
        "is_active": True,
        "is_verified": True,
        "first_login": False,
    }

    result = supabase.table("users").insert(admin_record).execute()

    if result.data:
        inserted = result.data[0]
        print(f"[OK]   Admin user created — id={inserted['id']}, email={inserted['email']}")
    else:
        print(f"[ERROR] Failed to insert Admin user: {result}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# 4. Seed default system_settings
# ---------------------------------------------------------------------------
DEFAULT_SETTINGS = [
    {
        "key": "session_timeout_jobseeker",
        "value": "3600",
        "description": "Session timeout in seconds for Jobseeker role (default: 1 hour).",
    },
    {
        "key": "session_timeout_employer",
        "value": "3600",
        "description": "Session timeout in seconds for Employer role (default: 1 hour).",
    },
    {
        "key": "session_timeout_staff",
        "value": "7200",
        "description": "Session timeout in seconds for PESO Staff role (default: 2 hours).",
    },
    {
        "key": "otp_expiry",
        "value": "600",
        "description": "OTP validity window in seconds (default: 10 minutes).",
    },
    {
        "key": "max_file_size",
        "value": "5242880",
        "description": "Maximum allowed file upload size in bytes (default: 5 MB = 5 * 1024 * 1024).",
    },
    {
        "key": "rate_limit_register",
        "value": "10",
        "description": "Maximum registration attempts per IP per 15-minute window.",
    },
    {
        "key": "rate_limit_login",
        "value": "5",
        "description": "Maximum failed login attempts per IP before lockout (15-minute window).",
    },
]


def seed_system_settings() -> None:
    """Insert default system_settings rows, skipping any that already exist."""
    print("\n--- Seeding system_settings ---")

    for setting in DEFAULT_SETTINGS:
        # Check if key already exists
        existing = (
            supabase.table("system_settings")
            .select("id, key")
            .eq("key", setting["key"])
            .execute()
        )

        if existing.data:
            print(f"[SKIP] system_settings key='{setting['key']}' already exists — skipping.")
            continue

        result = supabase.table("system_settings").insert(setting).execute()

        if result.data:
            inserted = result.data[0]
            print(
                f"[OK]   Inserted system_settings key='{inserted['key']}' "
                f"value='{setting['value']}'"
            )
        else:
            print(f"[ERROR] Failed to insert system_settings key='{setting['key']}': {result}")
            sys.exit(1)


# ---------------------------------------------------------------------------
# 5. Main entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("=" * 60)
    print("  JobBridge Database Seeder")
    print("=" * 60)

    seed_admin()
    seed_system_settings()

    print("\n" + "=" * 60)
    print("  Seeding complete.")
    print("=" * 60)
