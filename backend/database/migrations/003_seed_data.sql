-- =============================================================================
-- JobBridge System — Seed Data Migration
-- File: 003_seed_data.sql
-- Description: Inserts the pre-seeded Admin user and default system_settings
--              rows. All statements use ON CONFLICT DO NOTHING so this script
--              is safe to run multiple times (idempotent).
--
-- Requirements: 3.8 (Admin pre-seeded, no self-registration), 18.1 (system
--               settings configurable by Admin).
--
-- NOTE: The password_hash below is a bcrypt hash of 'Admin@JobBridge2026'
--       generated with cost factor 12. To regenerate:
--           python -c "import bcrypt; print(bcrypt.hashpw(b'Admin@JobBridge2026', bcrypt.gensalt(12)).decode())"
--       Replace the hash value below with the freshly generated one if needed.
--
-- Run this in the Supabase SQL editor AFTER 001_initial_schema.sql and
-- 002_storage_buckets.sql have been applied.
-- =============================================================================

-- Admin user: run `python seed.py` after migrations (writes a real bcrypt hash).

-- =============================================================================
-- SEED: Default system_settings
-- =============================================================================

-- Session timeout for Jobseeker role (seconds) — default 1 hour
INSERT INTO system_settings (key, value, description)
VALUES (
    'session_timeout_jobseeker',
    '3600',
    'Session timeout in seconds for Jobseeker role (default: 1 hour).'
)
ON CONFLICT (key) DO NOTHING;

-- Session timeout for Employer role (seconds) — default 1 hour
INSERT INTO system_settings (key, value, description)
VALUES (
    'session_timeout_employer',
    '3600',
    'Session timeout in seconds for Employer role (default: 1 hour).'
)
ON CONFLICT (key) DO NOTHING;

-- Session timeout for PESO Staff role (seconds) — default 2 hours
INSERT INTO system_settings (key, value, description)
VALUES (
    'session_timeout_staff',
    '7200',
    'Session timeout in seconds for PESO Staff role (default: 2 hours).'
)
ON CONFLICT (key) DO NOTHING;

-- OTP validity window (seconds) — default 10 minutes
INSERT INTO system_settings (key, value, description)
VALUES (
    'otp_expiry',
    '600',
    'OTP validity window in seconds (default: 10 minutes).'
)
ON CONFLICT (key) DO NOTHING;

-- Maximum file upload size (bytes) — default 5 MB
INSERT INTO system_settings (key, value, description)
VALUES (
    'max_file_size',
    '5242880',
    'Maximum allowed file upload size in bytes (default: 5 MB = 5 * 1024 * 1024).'
)
ON CONFLICT (key) DO NOTHING;

-- Rate limit: registration attempts per IP per 15-minute window
INSERT INTO system_settings (key, value, description)
VALUES (
    'rate_limit_register',
    '10',
    'Maximum registration attempts per IP per 15-minute window.'
)
ON CONFLICT (key) DO NOTHING;

-- Rate limit: failed login attempts per IP before lockout (15-minute window)
INSERT INTO system_settings (key, value, description)
VALUES (
    'rate_limit_login',
    '5',
    'Maximum failed login attempts per IP before lockout (15-minute window).'
)
ON CONFLICT (key) DO NOTHING;

-- =============================================================================
-- END OF SEED MIGRATION
-- =============================================================================
