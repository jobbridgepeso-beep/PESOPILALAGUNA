-- =============================================================================
-- JobBridge System — Initial Database Schema Migration
-- File: 001_initial_schema.sql
-- Description: Creates all tables, indexes, RLS policies, and triggers for the
--              JobBridge employment management platform (PESO Pila, Laguna).
-- Run this in the Supabase SQL editor.
-- =============================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- =============================================================================
-- HELPER: updated_at trigger function
-- =============================================================================
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- TABLE: users
-- =============================================================================
CREATE TABLE IF NOT EXISTS users (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email         VARCHAR(255) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role          VARCHAR(20)  NOT NULL CHECK (role IN ('jobseeker','employer','staff','admin')),
  is_active     BOOLEAN      NOT NULL DEFAULT false,
  is_verified   BOOLEAN      NOT NULL DEFAULT false,
  first_login   BOOLEAN      NOT NULL DEFAULT true,
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_users_email  ON users (email);
CREATE INDEX IF NOT EXISTS idx_users_role   ON users (role);

CREATE TRIGGER trg_users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- RLS policies: users
-- Admins and staff can read all users; each user can read/update their own row.
CREATE POLICY "users_select_own" ON users
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users_select_staff_admin" ON users
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "users_update_own" ON users
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "users_update_admin" ON users
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'admin'
    )
  );

-- service_role bypass (used by backend with service key)
CREATE POLICY "users_service_role_all" ON users
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: otp_tokens
-- =============================================================================
CREATE TABLE IF NOT EXISTS otp_tokens (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token      VARCHAR(6)  NOT NULL,
  purpose    VARCHAR(30) NOT NULL CHECK (purpose IN ('registration','password_reset')),
  expires_at TIMESTAMPTZ NOT NULL,
  used_at    TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_otp_tokens_user_id ON otp_tokens (user_id);
CREATE INDEX IF NOT EXISTS idx_otp_tokens_token   ON otp_tokens (token);

ALTER TABLE otp_tokens ENABLE ROW LEVEL SECURITY;

CREATE POLICY "otp_tokens_service_role_all" ON otp_tokens
  FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY "otp_tokens_select_own" ON otp_tokens
  FOR SELECT USING (auth.uid() = user_id);

-- =============================================================================
-- TABLE: jobseeker_profiles
-- =============================================================================
CREATE TABLE IF NOT EXISTS jobseeker_profiles (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id       UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  first_name    VARCHAR(100),
  last_name     VARCHAR(100),
  middle_name   VARCHAR(100),
  birthdate     DATE,
  gender        VARCHAR(20),
  civil_status  VARCHAR(30),
  address       TEXT,
  phone         VARCHAR(20),
  education     JSONB,
  experience    JSONB,
  skills        TEXT[],
  resume_url    TEXT,
  profile_photo TEXT,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_jobseeker_profiles_user_id ON jobseeker_profiles (user_id);
CREATE INDEX IF NOT EXISTS idx_jobseeker_profiles_skills  ON jobseeker_profiles USING GIN (skills);

CREATE TRIGGER trg_jobseeker_profiles_updated_at
  BEFORE UPDATE ON jobseeker_profiles
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE jobseeker_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "jobseeker_profiles_select_own" ON jobseeker_profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "jobseeker_profiles_update_own" ON jobseeker_profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "jobseeker_profiles_insert_own" ON jobseeker_profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "jobseeker_profiles_select_staff_admin_employer" ON jobseeker_profiles
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin','employer')
    )
  );

CREATE POLICY "jobseeker_profiles_service_role_all" ON jobseeker_profiles
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: employer_profiles
-- =============================================================================
CREATE TABLE IF NOT EXISTS employer_profiles (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id      UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  company_name VARCHAR(255),
  industry     VARCHAR(100),
  address      TEXT,
  phone        VARCHAR(20),
  website      VARCHAR(255),
  description  TEXT,
  logo_url     TEXT,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_employer_profiles_user_id ON employer_profiles (user_id);

CREATE TRIGGER trg_employer_profiles_updated_at
  BEFORE UPDATE ON employer_profiles
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE employer_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "employer_profiles_select_own" ON employer_profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "employer_profiles_update_own" ON employer_profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "employer_profiles_insert_own" ON employer_profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "employer_profiles_select_public" ON employer_profiles
  FOR SELECT USING (true);

CREATE POLICY "employer_profiles_update_staff_admin" ON employer_profiles
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "employer_profiles_service_role_all" ON employer_profiles
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: job_vacancies
-- =============================================================================
CREATE TABLE IF NOT EXISTS job_vacancies (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  employer_id      UUID        NOT NULL REFERENCES employer_profiles(id) ON DELETE CASCADE,
  title            VARCHAR(255) NOT NULL,
  description      TEXT         NOT NULL,
  requirements     TEXT         NOT NULL,
  skills_required  TEXT[],
  employment_type  VARCHAR(50)  CHECK (employment_type IN ('full-time','part-time','contract','temporary')),
  salary_min       NUMERIC(12,2),
  salary_max       NUMERIC(12,2),
  slots            INTEGER      NOT NULL DEFAULT 1,
  status           VARCHAR(20)  NOT NULL DEFAULT 'pending'
                   CHECK (status IN ('pending','active','rejected','closed')),
  rejection_reason TEXT,
  approved_by      UUID         REFERENCES users(id),
  approved_at      TIMESTAMPTZ,
  created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_vacancies_employer_id ON job_vacancies (employer_id);
CREATE INDEX IF NOT EXISTS idx_job_vacancies_status      ON job_vacancies (status);
CREATE INDEX IF NOT EXISTS idx_job_vacancies_skills      ON job_vacancies USING GIN (skills_required);

CREATE TRIGGER trg_job_vacancies_updated_at
  BEFORE UPDATE ON job_vacancies
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE job_vacancies ENABLE ROW LEVEL SECURITY;

-- Jobseekers can see active vacancies
CREATE POLICY "job_vacancies_select_active_jobseeker" ON job_vacancies
  FOR SELECT USING (
    status = 'active'
    AND EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'jobseeker'
    )
  );

-- Employers can see their own vacancies
CREATE POLICY "job_vacancies_select_own_employer" ON job_vacancies
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM employer_profiles ep WHERE ep.id = employer_id AND ep.user_id = auth.uid()
    )
  );

CREATE POLICY "job_vacancies_insert_employer" ON job_vacancies
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM employer_profiles ep WHERE ep.id = employer_id AND ep.user_id = auth.uid()
    )
  );

CREATE POLICY "job_vacancies_update_employer_own" ON job_vacancies
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM employer_profiles ep WHERE ep.id = employer_id AND ep.user_id = auth.uid()
    )
  );

-- Staff and admin can see and manage all vacancies
CREATE POLICY "job_vacancies_all_staff_admin" ON job_vacancies
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "job_vacancies_service_role_all" ON job_vacancies
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: job_applications
-- =============================================================================
CREATE TABLE IF NOT EXISTS job_applications (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  vacancy_id   UUID        NOT NULL REFERENCES job_vacancies(id) ON DELETE CASCADE,
  jobseeker_id UUID        NOT NULL REFERENCES jobseeker_profiles(id) ON DELETE CASCADE,
  status       VARCHAR(30) NOT NULL DEFAULT 'pending'
               CHECK (status IN ('pending','reviewed','shortlisted','rejected','hired')),
  match_score  NUMERIC(5,4),
  cover_letter TEXT,
  applied_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (vacancy_id, jobseeker_id)
);

CREATE INDEX IF NOT EXISTS idx_job_applications_vacancy_id   ON job_applications (vacancy_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_jobseeker_id ON job_applications (jobseeker_id);
CREATE INDEX IF NOT EXISTS idx_job_applications_status       ON job_applications (status);

CREATE TRIGGER trg_job_applications_updated_at
  BEFORE UPDATE ON job_applications
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE job_applications ENABLE ROW LEVEL SECURITY;

-- Jobseeker can see their own applications
CREATE POLICY "job_applications_select_own_jobseeker" ON job_applications
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM jobseeker_profiles jp WHERE jp.id = jobseeker_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "job_applications_insert_jobseeker" ON job_applications
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM jobseeker_profiles jp WHERE jp.id = jobseeker_id AND jp.user_id = auth.uid()
    )
  );

-- Employer can see applications for their vacancies
CREATE POLICY "job_applications_select_employer" ON job_applications
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM job_vacancies jv
      JOIN employer_profiles ep ON ep.id = jv.employer_id
      WHERE jv.id = vacancy_id AND ep.user_id = auth.uid()
    )
  );

CREATE POLICY "job_applications_update_employer" ON job_applications
  FOR UPDATE USING (
    EXISTS (
      SELECT 1 FROM job_vacancies jv
      JOIN employer_profiles ep ON ep.id = jv.employer_id
      WHERE jv.id = vacancy_id AND ep.user_id = auth.uid()
    )
  );

CREATE POLICY "job_applications_all_staff_admin" ON job_applications
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "job_applications_service_role_all" ON job_applications
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: interviews
-- =============================================================================
CREATE TABLE IF NOT EXISTS interviews (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID        NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
  scheduled_at   TIMESTAMPTZ NOT NULL,
  location       TEXT,
  meeting_link   TEXT,
  notes          TEXT,
  status         VARCHAR(20) NOT NULL DEFAULT 'scheduled'
                 CHECK (status IN ('scheduled','completed','cancelled')),
  created_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_interviews_application_id ON interviews (application_id);
CREATE INDEX IF NOT EXISTS idx_interviews_scheduled_at   ON interviews (scheduled_at);

CREATE TRIGGER trg_interviews_updated_at
  BEFORE UPDATE ON interviews
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE interviews ENABLE ROW LEVEL SECURITY;

-- Jobseeker can see interviews for their applications
CREATE POLICY "interviews_select_jobseeker" ON interviews
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM job_applications ja
      JOIN jobseeker_profiles jp ON jp.id = ja.jobseeker_id
      WHERE ja.id = application_id AND jp.user_id = auth.uid()
    )
  );

-- Employer can manage interviews for their vacancies
CREATE POLICY "interviews_all_employer" ON interviews
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM job_applications ja
      JOIN job_vacancies jv ON jv.id = ja.vacancy_id
      JOIN employer_profiles ep ON ep.id = jv.employer_id
      WHERE ja.id = application_id AND ep.user_id = auth.uid()
    )
  );

CREATE POLICY "interviews_all_staff_admin" ON interviews
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "interviews_service_role_all" ON interviews
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: referral_letters
-- =============================================================================
CREATE TABLE IF NOT EXISTS referral_letters (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID        NOT NULL REFERENCES job_applications(id) ON DELETE CASCADE,
  generated_by   UUID        REFERENCES users(id),
  pdf_url        TEXT        NOT NULL,
  generated_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_referral_letters_application_id ON referral_letters (application_id);

ALTER TABLE referral_letters ENABLE ROW LEVEL SECURITY;

-- Jobseeker can view their own referral letters
CREATE POLICY "referral_letters_select_jobseeker" ON referral_letters
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM job_applications ja
      JOIN jobseeker_profiles jp ON jp.id = ja.jobseeker_id
      WHERE ja.id = application_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "referral_letters_all_staff_admin" ON referral_letters
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "referral_letters_service_role_all" ON referral_letters
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: job_fairs
-- =============================================================================
CREATE TABLE IF NOT EXISTS job_fairs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title       VARCHAR(255) NOT NULL,
  description TEXT,
  event_date  DATE         NOT NULL,
  start_time  TIME         NOT NULL,
  end_time    TIME         NOT NULL,
  venue       TEXT         NOT NULL,
  status      VARCHAR(20)  NOT NULL DEFAULT 'upcoming'
              CHECK (status IN ('upcoming','ongoing','completed','cancelled')),
  created_by  UUID         REFERENCES users(id),
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_fairs_event_date ON job_fairs (event_date);
CREATE INDEX IF NOT EXISTS idx_job_fairs_status     ON job_fairs (status);

CREATE TRIGGER trg_job_fairs_updated_at
  BEFORE UPDATE ON job_fairs
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE job_fairs ENABLE ROW LEVEL SECURITY;

-- All authenticated users can view job fairs
CREATE POLICY "job_fairs_select_authenticated" ON job_fairs
  FOR SELECT USING (auth.uid() IS NOT NULL);

-- Only staff/admin can insert/update/delete
CREATE POLICY "job_fairs_write_staff_admin" ON job_fairs
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "job_fairs_service_role_all" ON job_fairs
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: job_fair_registrations
-- =============================================================================
CREATE TABLE IF NOT EXISTS job_fair_registrations (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  job_fair_id  UUID        NOT NULL REFERENCES job_fairs(id) ON DELETE CASCADE,
  jobseeker_id UUID        NOT NULL REFERENCES jobseeker_profiles(id) ON DELETE CASCADE,
  qr_token     TEXT        UNIQUE NOT NULL,
  qr_url       TEXT,
  registered_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (job_fair_id, jobseeker_id)
);

CREATE INDEX IF NOT EXISTS idx_job_fair_registrations_job_fair_id  ON job_fair_registrations (job_fair_id);
CREATE INDEX IF NOT EXISTS idx_job_fair_registrations_jobseeker_id ON job_fair_registrations (jobseeker_id);
CREATE INDEX IF NOT EXISTS idx_job_fair_registrations_qr_token     ON job_fair_registrations (qr_token);

ALTER TABLE job_fair_registrations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "job_fair_registrations_select_own_jobseeker" ON job_fair_registrations
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM jobseeker_profiles jp WHERE jp.id = jobseeker_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "job_fair_registrations_insert_jobseeker" ON job_fair_registrations
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM jobseeker_profiles jp WHERE jp.id = jobseeker_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "job_fair_registrations_all_staff_admin" ON job_fair_registrations
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "job_fair_registrations_service_role_all" ON job_fair_registrations
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: job_fair_attendance
-- =============================================================================
CREATE TABLE IF NOT EXISTS job_fair_attendance (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  registration_id UUID        NOT NULL REFERENCES job_fair_registrations(id) ON DELETE CASCADE,
  scanned_by      UUID        REFERENCES users(id),
  scanned_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_job_fair_attendance_registration_id ON job_fair_attendance (registration_id);
CREATE INDEX IF NOT EXISTS idx_job_fair_attendance_scanned_at      ON job_fair_attendance (scanned_at);

ALTER TABLE job_fair_attendance ENABLE ROW LEVEL SECURITY;

-- Jobseeker can view their own attendance records
CREATE POLICY "job_fair_attendance_select_jobseeker" ON job_fair_attendance
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM job_fair_registrations jfr
      JOIN jobseeker_profiles jp ON jp.id = jfr.jobseeker_id
      WHERE jfr.id = registration_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "job_fair_attendance_all_staff_admin" ON job_fair_attendance
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "job_fair_attendance_service_role_all" ON job_fair_attendance
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: program_applications
-- =============================================================================
CREATE TABLE IF NOT EXISTS program_applications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  jobseeker_id    UUID        NOT NULL REFERENCES jobseeker_profiles(id) ON DELETE CASCADE,
  program_type    VARCHAR(20) NOT NULL CHECK (program_type IN ('spes','dilp','owwa','mst')),
  status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','approved','rejected')),
  decision_reason TEXT,
  reviewed_by     UUID        REFERENCES users(id),
  reviewed_at     TIMESTAMPTZ,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_program_applications_jobseeker_id ON program_applications (jobseeker_id);
CREATE INDEX IF NOT EXISTS idx_program_applications_program_type ON program_applications (program_type);
CREATE INDEX IF NOT EXISTS idx_program_applications_status       ON program_applications (status);

CREATE TRIGGER trg_program_applications_updated_at
  BEFORE UPDATE ON program_applications
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE program_applications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "program_applications_select_own_jobseeker" ON program_applications
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM jobseeker_profiles jp WHERE jp.id = jobseeker_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "program_applications_insert_jobseeker" ON program_applications
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM jobseeker_profiles jp WHERE jp.id = jobseeker_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "program_applications_all_staff_admin" ON program_applications
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "program_applications_service_role_all" ON program_applications
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: program_documents
-- =============================================================================
CREATE TABLE IF NOT EXISTS program_documents (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  application_id UUID         NOT NULL REFERENCES program_applications(id) ON DELETE CASCADE,
  document_type  VARCHAR(100) NOT NULL,
  file_url       TEXT         NOT NULL,
  ocr_data       JSONB,
  uploaded_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_program_documents_application_id ON program_documents (application_id);

ALTER TABLE program_documents ENABLE ROW LEVEL SECURITY;

-- Jobseeker can view their own documents
CREATE POLICY "program_documents_select_jobseeker" ON program_documents
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM program_applications pa
      JOIN jobseeker_profiles jp ON jp.id = pa.jobseeker_id
      WHERE pa.id = application_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "program_documents_insert_jobseeker" ON program_documents
  FOR INSERT WITH CHECK (
    EXISTS (
      SELECT 1 FROM program_applications pa
      JOIN jobseeker_profiles jp ON jp.id = pa.jobseeker_id
      WHERE pa.id = application_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "program_documents_all_staff_admin" ON program_documents
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "program_documents_service_role_all" ON program_documents
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: employment_records
-- =============================================================================
CREATE TABLE IF NOT EXISTS employment_records (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  jobseeker_id    UUID        NOT NULL REFERENCES jobseeker_profiles(id) ON DELETE CASCADE,
  employer_id     UUID        REFERENCES employer_profiles(id),
  vacancy_id      UUID        REFERENCES job_vacancies(id),
  application_id  UUID        REFERENCES job_applications(id),
  employment_type VARCHAR(50),
  start_date      DATE,
  end_date        DATE,
  status          VARCHAR(20) NOT NULL DEFAULT 'active'
                  CHECK (status IN ('active','ended')),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_employment_records_jobseeker_id ON employment_records (jobseeker_id);
CREATE INDEX IF NOT EXISTS idx_employment_records_employer_id  ON employment_records (employer_id);
CREATE INDEX IF NOT EXISTS idx_employment_records_status       ON employment_records (status);

CREATE TRIGGER trg_employment_records_updated_at
  BEFORE UPDATE ON employment_records
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE employment_records ENABLE ROW LEVEL SECURITY;

CREATE POLICY "employment_records_select_own_jobseeker" ON employment_records
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM jobseeker_profiles jp WHERE jp.id = jobseeker_id AND jp.user_id = auth.uid()
    )
  );

CREATE POLICY "employment_records_select_employer" ON employment_records
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM employer_profiles ep WHERE ep.id = employer_id AND ep.user_id = auth.uid()
    )
  );

CREATE POLICY "employment_records_all_staff_admin" ON employment_records
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "employment_records_service_role_all" ON employment_records
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: notifications
-- =============================================================================
CREATE TABLE IF NOT EXISTS notifications (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id    UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  event_type VARCHAR(100) NOT NULL,
  title      VARCHAR(255) NOT NULL,
  body       TEXT,
  payload    JSONB,
  is_read    BOOLEAN      NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_notifications_user_id   ON notifications (user_id);
CREATE INDEX IF NOT EXISTS idx_notifications_is_read   ON notifications (is_read);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON notifications (created_at DESC);

ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;

-- Users can only see their own notifications
CREATE POLICY "notifications_select_own" ON notifications
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "notifications_update_own" ON notifications
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "notifications_service_role_all" ON notifications
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: audit_trail
-- Append-only: INSERT only. No UPDATE or DELETE for any role.
-- =============================================================================
CREATE TABLE IF NOT EXISTS audit_trail (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id      UUID         REFERENCES users(id),
  actor_role    VARCHAR(20)  NOT NULL,
  action_type   VARCHAR(100) NOT NULL,
  resource_type VARCHAR(100),
  resource_id   UUID,
  ip_address    INET,
  metadata      JSONB,
  created_at    TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_audit_trail_actor_id      ON audit_trail (actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_trail_action_type   ON audit_trail (action_type);
CREATE INDEX IF NOT EXISTS idx_audit_trail_resource_type ON audit_trail (resource_type);
CREATE INDEX IF NOT EXISTS idx_audit_trail_created_at    ON audit_trail (created_at DESC);

ALTER TABLE audit_trail ENABLE ROW LEVEL SECURITY;

-- Admin can SELECT audit trail entries
CREATE POLICY "audit_trail_select_admin" ON audit_trail
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'admin'
    )
  );

-- service_role can INSERT (used by backend audit service)
CREATE POLICY "audit_trail_insert_service_role" ON audit_trail
  FOR INSERT WITH CHECK (auth.role() = 'service_role');

-- Explicitly NO UPDATE or DELETE policies — append-only enforcement
-- (No UPDATE policy means no role can update rows)
-- (No DELETE policy means no role can delete rows)

-- Revoke UPDATE and DELETE from all roles at the table level
REVOKE UPDATE, DELETE ON audit_trail FROM PUBLIC;
REVOKE UPDATE, DELETE ON audit_trail FROM authenticated;
REVOKE UPDATE, DELETE ON audit_trail FROM anon;
-- Note: service_role in Supabase bypasses RLS but we still revoke at SQL level
-- to enforce append-only at the database permission layer.

-- =============================================================================
-- TABLE: lmi_reports
-- =============================================================================
CREATE TABLE IF NOT EXISTS lmi_reports (
  id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_type  VARCHAR(20) NOT NULL CHECK (report_type IN ('monthly','quarterly','annual','custom')),
  period_start DATE        NOT NULL,
  period_end   DATE        NOT NULL,
  pdf_url      TEXT,
  excel_url    TEXT,
  generated_by UUID        REFERENCES users(id),
  generated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_lmi_reports_report_type  ON lmi_reports (report_type);
CREATE INDEX IF NOT EXISTS idx_lmi_reports_generated_at ON lmi_reports (generated_at DESC);

ALTER TABLE lmi_reports ENABLE ROW LEVEL SECURITY;

CREATE POLICY "lmi_reports_select_staff_admin" ON lmi_reports
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role IN ('staff','admin')
    )
  );

CREATE POLICY "lmi_reports_service_role_all" ON lmi_reports
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- TABLE: system_settings
-- =============================================================================
CREATE TABLE IF NOT EXISTS system_settings (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key         VARCHAR(100) UNIQUE NOT NULL,
  value       TEXT         NOT NULL,
  description TEXT,
  updated_by  UUID         REFERENCES users(id),
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_system_settings_key ON system_settings (key);

CREATE TRIGGER trg_system_settings_updated_at
  BEFORE UPDATE ON system_settings
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

ALTER TABLE system_settings ENABLE ROW LEVEL SECURITY;

-- Only admin can read/write system settings
CREATE POLICY "system_settings_all_admin" ON system_settings
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM users u WHERE u.id = auth.uid() AND u.role = 'admin'
    )
  );

CREATE POLICY "system_settings_service_role_all" ON system_settings
  FOR ALL USING (auth.role() = 'service_role');

-- =============================================================================
-- GRANT PERMISSIONS
-- Grant INSERT-only on audit_trail to the authenticated role.
-- No UPDATE or DELETE is granted to any role.
-- =============================================================================
GRANT INSERT ON audit_trail TO authenticated;
GRANT SELECT ON audit_trail TO authenticated;

-- Grant standard CRUD on all other tables to authenticated role
GRANT SELECT, INSERT, UPDATE, DELETE ON users                    TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON otp_tokens               TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON jobseeker_profiles       TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON employer_profiles        TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON job_vacancies            TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON job_applications         TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON interviews               TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON referral_letters         TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON job_fairs                TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON job_fair_registrations   TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON job_fair_attendance      TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON program_applications     TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON program_documents        TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON employment_records       TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON notifications            TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON lmi_reports              TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON system_settings          TO authenticated;

-- =============================================================================
-- SUPABASE REALTIME
-- Enable realtime on tables that need live updates
-- =============================================================================
ALTER PUBLICATION supabase_realtime ADD TABLE notifications;
ALTER PUBLICATION supabase_realtime ADD TABLE job_applications;
ALTER PUBLICATION supabase_realtime ADD TABLE interviews;
ALTER PUBLICATION supabase_realtime ADD TABLE job_fair_attendance;

-- =============================================================================
-- END OF MIGRATION
-- =============================================================================
