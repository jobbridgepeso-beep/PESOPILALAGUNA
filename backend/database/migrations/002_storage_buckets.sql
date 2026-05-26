-- =============================================================================
-- JobBridge System — Supabase Storage Buckets Migration
-- File: 002_storage_buckets.sql
-- Description: Creates all Storage buckets and configures RLS policies for
--              the JobBridge employment management platform (PESO Pila, Laguna).
-- Requirement: 19.3 — Store all uploaded files in Supabase Storage with access
--              controlled by the uploader's role and ownership.
-- Run this in the Supabase SQL editor AFTER 001_initial_schema.sql.
-- =============================================================================

-- =============================================================================
-- SECTION 1: Create Storage Buckets
-- =============================================================================

-- resumes: Jobseeker resume files (private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'resumes',
  'resumes',
  false,
  5242880,  -- 5MB in bytes
  ARRAY['image/jpeg', 'image/png', 'application/pdf']
)
ON CONFLICT (id) DO UPDATE SET
  public             = EXCLUDED.public,
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- program-docs: Program application documents (private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'program-docs',
  'program-docs',
  false,
  5242880,
  ARRAY['image/jpeg', 'image/png', 'application/pdf']
)
ON CONFLICT (id) DO UPDATE SET
  public             = EXCLUDED.public,
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- referral-letters: Generated referral PDFs (private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'referral-letters',
  'referral-letters',
  false,
  5242880,
  ARRAY['application/pdf']
)
ON CONFLICT (id) DO UPDATE SET
  public             = EXCLUDED.public,
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- lmi-reports: LMI PDF + Excel files (private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'lmi-reports',
  'lmi-reports',
  false,
  52428800,  -- 50MB — reports can be large
  ARRAY['application/pdf', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']
)
ON CONFLICT (id) DO UPDATE SET
  public             = EXCLUDED.public,
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- qr-codes: Job fair QR code images (private)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'qr-codes',
  'qr-codes',
  false,
  1048576,  -- 1MB — QR images are small
  ARRAY['image/jpeg', 'image/png']
)
ON CONFLICT (id) DO UPDATE SET
  public             = EXCLUDED.public,
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- company-logos: Employer company logos (public read)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'company-logos',
  'company-logos',
  true,
  2097152,  -- 2MB
  ARRAY['image/jpeg', 'image/png']
)
ON CONFLICT (id) DO UPDATE SET
  public             = EXCLUDED.public,
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;

-- profile-photos: Jobseeker profile photos (public read)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'profile-photos',
  'profile-photos',
  true,
  2097152,  -- 2MB
  ARRAY['image/jpeg', 'image/png']
)
ON CONFLICT (id) DO UPDATE SET
  public             = EXCLUDED.public,
  file_size_limit    = EXCLUDED.file_size_limit,
  allowed_mime_types = EXCLUDED.allowed_mime_types;


-- =============================================================================
-- SECTION 2: Storage RLS Policies
-- =============================================================================
-- Supabase Storage RLS policies operate on the storage.objects table.
-- The bucket_id column identifies which bucket an object belongs to.
-- The owner column (UUID) is set to auth.uid() on upload.
-- We use auth.uid() and a sub-select on the users table to check roles.
-- =============================================================================

-- Helper note: storage.objects columns used in policies:
--   bucket_id  TEXT    — matches the bucket name/id
--   owner      UUID    — set to auth.uid() at upload time (Supabase sets this)
--   name       TEXT    — the file path within the bucket


-- =============================================================================
-- BUCKET: resumes
-- Access: Owner (jobseeker) + Staff + Admin — read and write
-- =============================================================================

-- Drop existing policies to allow idempotent re-runs
DROP POLICY IF EXISTS "resumes_select_owner_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "resumes_insert_owner"              ON storage.objects;
DROP POLICY IF EXISTS "resumes_update_owner_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "resumes_delete_owner_staff_admin"  ON storage.objects;

CREATE POLICY "resumes_select_owner_staff_admin" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'resumes'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
      )
    )
  );

CREATE POLICY "resumes_insert_owner" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'resumes'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'jobseeker'
    )
  );

CREATE POLICY "resumes_update_owner_staff_admin" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'resumes'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
      )
    )
  );

CREATE POLICY "resumes_delete_owner_staff_admin" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'resumes'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
      )
    )
  );


-- =============================================================================
-- BUCKET: program-docs
-- Access: Owner (jobseeker) + Staff + Admin — read and write
-- =============================================================================

DROP POLICY IF EXISTS "program_docs_select_owner_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "program_docs_insert_owner"              ON storage.objects;
DROP POLICY IF EXISTS "program_docs_update_owner_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "program_docs_delete_owner_staff_admin"  ON storage.objects;

CREATE POLICY "program_docs_select_owner_staff_admin" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'program-docs'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
      )
    )
  );

CREATE POLICY "program_docs_insert_owner" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'program-docs'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'jobseeker'
    )
  );

CREATE POLICY "program_docs_update_owner_staff_admin" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'program-docs'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
      )
    )
  );

CREATE POLICY "program_docs_delete_owner_staff_admin" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'program-docs'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
      )
    )
  );


-- =============================================================================
-- BUCKET: referral-letters
-- Access: Owner (jobseeker who the letter belongs to) + Staff + Admin — read and write
-- Staff generates the letter (insert); jobseeker and staff/admin can read.
-- =============================================================================

DROP POLICY IF EXISTS "referral_letters_select_owner_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "referral_letters_insert_staff_admin"        ON storage.objects;
DROP POLICY IF EXISTS "referral_letters_update_staff_admin"        ON storage.objects;
DROP POLICY IF EXISTS "referral_letters_delete_staff_admin"        ON storage.objects;

CREATE POLICY "referral_letters_select_owner_staff_admin" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'referral-letters'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
      )
    )
  );

-- Only staff/admin generate referral letters (backend service_role also bypasses RLS)
CREATE POLICY "referral_letters_insert_staff_admin" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'referral-letters'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
    )
  );

CREATE POLICY "referral_letters_update_staff_admin" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'referral-letters'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
    )
  );

CREATE POLICY "referral_letters_delete_staff_admin" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'referral-letters'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
    )
  );


-- =============================================================================
-- BUCKET: lmi-reports
-- Access: Staff + Admin only — read and write
-- =============================================================================

DROP POLICY IF EXISTS "lmi_reports_select_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "lmi_reports_insert_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "lmi_reports_update_staff_admin"  ON storage.objects;
DROP POLICY IF EXISTS "lmi_reports_delete_staff_admin"  ON storage.objects;

CREATE POLICY "lmi_reports_select_staff_admin" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'lmi-reports'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
    )
  );

CREATE POLICY "lmi_reports_insert_staff_admin" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'lmi-reports'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
    )
  );

CREATE POLICY "lmi_reports_update_staff_admin" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'lmi-reports'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
    )
  );

CREATE POLICY "lmi_reports_delete_staff_admin" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'lmi-reports'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff', 'admin')
    )
  );


-- =============================================================================
-- BUCKET: qr-codes
-- Access: Owner (jobseeker) + Staff — read and write
-- Staff generates QR codes (insert); jobseeker can read their own.
-- =============================================================================

DROP POLICY IF EXISTS "qr_codes_select_owner_staff"  ON storage.objects;
DROP POLICY IF EXISTS "qr_codes_insert_staff"        ON storage.objects;
DROP POLICY IF EXISTS "qr_codes_update_staff"        ON storage.objects;
DROP POLICY IF EXISTS "qr_codes_delete_staff"        ON storage.objects;

CREATE POLICY "qr_codes_select_owner_staff" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'qr-codes'
    AND (
      auth.uid() = owner
      OR EXISTS (
        SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'staff'
      )
    )
  );

-- Staff generates QR codes on behalf of jobseekers
CREATE POLICY "qr_codes_insert_staff" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'qr-codes'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'staff'
    )
  );

CREATE POLICY "qr_codes_update_staff" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'qr-codes'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'staff'
    )
  );

CREATE POLICY "qr_codes_delete_staff" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'qr-codes'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'staff'
    )
  );


-- =============================================================================
-- BUCKET: company-logos
-- Access: Public read (bucket is public=true), Employer owner write
-- =============================================================================

DROP POLICY IF EXISTS "company_logos_insert_employer_owner"  ON storage.objects;
DROP POLICY IF EXISTS "company_logos_update_employer_owner"  ON storage.objects;
DROP POLICY IF EXISTS "company_logos_delete_employer_owner"  ON storage.objects;

-- Public SELECT is handled automatically by the bucket's public=true setting.
-- We still add an explicit policy for completeness and to allow anon reads.
DROP POLICY IF EXISTS "company_logos_select_public" ON storage.objects;

CREATE POLICY "company_logos_select_public" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'company-logos'
  );

CREATE POLICY "company_logos_insert_employer_owner" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'company-logos'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'employer'
    )
  );

CREATE POLICY "company_logos_update_employer_owner" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'company-logos'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'employer'
    )
  );

CREATE POLICY "company_logos_delete_employer_owner" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'company-logos'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'employer'
    )
  );


-- =============================================================================
-- BUCKET: profile-photos
-- Access: Public read (bucket is public=true), Jobseeker owner write
-- =============================================================================

DROP POLICY IF EXISTS "profile_photos_select_public"          ON storage.objects;
DROP POLICY IF EXISTS "profile_photos_insert_jobseeker_owner" ON storage.objects;
DROP POLICY IF EXISTS "profile_photos_update_jobseeker_owner" ON storage.objects;
DROP POLICY IF EXISTS "profile_photos_delete_jobseeker_owner" ON storage.objects;

CREATE POLICY "profile_photos_select_public" ON storage.objects
  FOR SELECT USING (
    bucket_id = 'profile-photos'
  );

CREATE POLICY "profile_photos_insert_jobseeker_owner" ON storage.objects
  FOR INSERT WITH CHECK (
    bucket_id = 'profile-photos'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'jobseeker'
    )
  );

CREATE POLICY "profile_photos_update_jobseeker_owner" ON storage.objects
  FOR UPDATE USING (
    bucket_id = 'profile-photos'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'jobseeker'
    )
  );

CREATE POLICY "profile_photos_delete_jobseeker_owner" ON storage.objects
  FOR DELETE USING (
    bucket_id = 'profile-photos'
    AND auth.uid() = owner
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'jobseeker'
    )
  );


-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
