"""
create_buckets.py
=================
Programmatic alternative to 002_storage_buckets.sql.

Uses supabase-py (service_role key) to create all 7 Supabase Storage buckets
for the JobBridge system.  Run this script once during initial environment
setup or when bootstrapping a new Supabase project.

Usage
-----
    # From the backend/ directory:
    python database/create_buckets.py

Environment variables (loaded from backend/.env or set in the shell):
    SUPABASE_URL        — e.g. https://<project-ref>.supabase.co
    SUPABASE_SERVICE_KEY — service_role secret key (NOT the anon key)

Note: The service_role key bypasses RLS and is required to create buckets.
      Never expose this key in client-side code or commit it to version control.
"""

import os
import sys

from dotenv import load_dotenv
from supabase import create_client, Client

# ---------------------------------------------------------------------------
# Load environment
# ---------------------------------------------------------------------------
# Walk up from this file's directory to find the .env file in backend/
_HERE = os.path.dirname(os.path.abspath(__file__))
_BACKEND_DIR = os.path.dirname(_HERE)  # backend/
load_dotenv(os.path.join(_BACKEND_DIR, ".env"))

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print(
        "ERROR: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set in the environment "
        "or in backend/.env before running this script.",
        file=sys.stderr,
    )
    sys.exit(1)

# ---------------------------------------------------------------------------
# Bucket definitions
# ---------------------------------------------------------------------------
# Each entry:
#   id              — bucket name / identifier (must be unique in the project)
#   public          — True  → public read (no auth required for GET)
#                     False → private (RLS policies control access)
#   file_size_limit — maximum upload size in bytes (enforced by Supabase)
#   allowed_mime_types — list of accepted MIME types (None = allow all)
# ---------------------------------------------------------------------------
BUCKETS = [
    {
        "id": "resumes",
        "public": False,
        "file_size_limit": 5 * 1024 * 1024,  # 5 MB
        "allowed_mime_types": ["image/jpeg", "image/png", "application/pdf"],
    },
    {
        "id": "program-docs",
        "public": False,
        "file_size_limit": 5 * 1024 * 1024,
        "allowed_mime_types": ["image/jpeg", "image/png", "application/pdf"],
    },
    {
        "id": "referral-letters",
        "public": False,
        "file_size_limit": 5 * 1024 * 1024,
        "allowed_mime_types": ["application/pdf"],
    },
    {
        "id": "lmi-reports",
        "public": False,
        "file_size_limit": 50 * 1024 * 1024,  # 50 MB — reports can be large
        "allowed_mime_types": [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        ],
    },
    {
        "id": "qr-codes",
        "public": False,
        "file_size_limit": 1 * 1024 * 1024,  # 1 MB — QR images are small
        "allowed_mime_types": ["image/jpeg", "image/png"],
    },
    {
        "id": "company-logos",
        "public": True,   # Public read — displayed on job listings
        "file_size_limit": 2 * 1024 * 1024,  # 2 MB
        "allowed_mime_types": ["image/jpeg", "image/png"],
    },
    {
        "id": "profile-photos",
        "public": True,   # Public read — displayed on jobseeker profiles
        "file_size_limit": 2 * 1024 * 1024,
        "allowed_mime_types": ["image/jpeg", "image/png"],
    },
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _bucket_exists(client: Client, bucket_id: str) -> bool:
    """Return True if a bucket with the given id already exists."""
    try:
        buckets = client.storage.list_buckets()
        return any(b.id == bucket_id for b in buckets)
    except Exception:
        return False


def create_bucket(client: Client, bucket: dict) -> None:
    """Create a single bucket, skipping if it already exists."""
    bucket_id = bucket["id"]

    if _bucket_exists(client, bucket_id):
        print(f"  [SKIP]    '{bucket_id}' already exists — skipping.")
        return

    options = {
        "public": bucket["public"],
        "file_size_limit": bucket["file_size_limit"],
        "allowed_mime_types": bucket["allowed_mime_types"],
    }

    client.storage.create_bucket(bucket_id, options=options)
    visibility = "public" if bucket["public"] else "private"
    size_mb = bucket["file_size_limit"] // (1024 * 1024)
    print(f"  [CREATED] '{bucket_id}' ({visibility}, {size_mb} MB limit)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    print("JobBridge — Supabase Storage bucket setup")
    print(f"Project URL : {SUPABASE_URL}")
    print("-" * 50)

    client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

    errors: list[tuple[str, str]] = []

    for bucket in BUCKETS:
        try:
            create_bucket(client, bucket)
        except Exception as exc:
            bucket_id = bucket["id"]
            print(f"  [ERROR]   '{bucket_id}' — {exc}")
            errors.append((bucket_id, str(exc)))

    print("-" * 50)

    if errors:
        print(f"Completed with {len(errors)} error(s):")
        for bucket_id, msg in errors:
            print(f"  • {bucket_id}: {msg}")
        sys.exit(1)
    else:
        print(f"All {len(BUCKETS)} buckets created (or already existed) successfully.")
        print()
        print("Next step: Run 002_storage_buckets.sql in the Supabase SQL editor")
        print("to apply the RLS policies for each bucket.")


if __name__ == "__main__":
    main()
