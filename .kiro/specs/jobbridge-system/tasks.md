# Implementation Plan: JobBridge System

## Overview

Full-stack implementation of the JobBridge employment management platform for PESO Pila, Laguna. The stack is React 18 + Vite (frontend) and Python 3.11 + Flask (backend) with Supabase PostgreSQL, Redis, and Celery. Tasks are ordered to build incrementally: scaffolding → database → auth → core APIs → AI/ML → real-time → frontend → integrations → deployment.

## Tasks

- [x] 1. Project Scaffolding and Configuration
  - [x] 1.1 Initialize backend Flask project structure
    - Create `backend/` directory with `app/__init__.py` (app factory), `app/extensions.py`, `app/config.py`, `wsgi.py`, `celery_worker.py`, `requirements.txt`
    - Configure Flask app factory to register blueprints, JWT, CORS, SocketIO, Mail, Supabase client
    - Add `.env.example` with all required environment variables (SUPABASE_URL, SUPABASE_KEY, SUPABASE_SERVICE_KEY, JWT_SECRET_KEY, MAIL_USERNAME, MAIL_PASSWORD, REDIS_URL, DIALOGFLOW_PROJECT_ID, GOOGLE_APPLICATION_CREDENTIALS)
    - _Requirements: 20.4_
  - [x] 1.2 Initialize frontend React + Vite project structure
    - Create `frontend/` with Vite + React 18 template, install all dependencies from the tech stack
    - Configure Tailwind CSS, Shadcn/UI, React Router v6, Axios instance with base URL and JWT interceptors
    - Create `src/store/`, `src/api/`, `src/hooks/`, `src/components/`, `src/pages/`, `src/utils/` directories
    - _Requirements: 3.1, 3.2_
  - [x] 1.3 Configure Redis and Celery
    - Set up Celery app in `celery_worker.py` with Redis broker and result backend
    - Configure `CELERY_TASK_ALWAYS_EAGER=True` for test environment
    - _Requirements: 13.1_


- [x] 2. Database Schema and Supabase Setup
  - [x] 2.1 Create all database tables via Supabase SQL editor
    - Write migration SQL for: `users`, `otp_tokens`, `jobseeker_profiles`, `employer_profiles`, `job_vacancies`, `job_applications`, `interviews`, `referral_letters`, `job_fairs`, `job_fair_registrations`, `job_fair_attendance`, `program_applications`, `program_documents`, `employment_records`, `notifications`, `audit_trail`, `lmi_reports`, `system_settings`
    - Apply Row Level Security (RLS) policies per table per role
    - Grant append-only access on `audit_trail` (no UPDATE/DELETE for any role)
    - _Requirements: 17.3_
  - [x] 2.2 Create Supabase Storage buckets
    - Create buckets: `resumes`, `program-docs`, `referral-letters`, `lmi-reports`, `qr-codes`, `company-logos`, `profile-photos`
    - Configure bucket-level access policies per design document
    - _Requirements: 19.3_
  - [x] 2.3 Create SQLAlchemy ORM models
    - Write `app/models/` Python files for all 17 tables using SQLAlchemy declarative base
    - Add `__repr__` methods and relationship definitions
    - _Requirements: 4.4, 6.1_
  - [x] 2.4 Create Marshmallow serialization schemas
    - Write `app/schemas/` files for all models with field-level validation
    - Add nested schemas for JSONB fields (education, experience, skills)
    - _Requirements: 20.1_
  - [x] 2.5 Seed Admin account and default system settings
    - Write `seed.py` script to insert pre-seeded Admin user with bcrypt-hashed password
    - Insert default `system_settings` rows (session_timeout_jobseeker=3600, otp_expiry=600, max_file_size=5242880, rate_limit_register=10, rate_limit_login=5)
    - _Requirements: 3.8, 18.1_


- [ ] 3. Authentication and Session Management
  - [x] 3.1 Implement OTP generation and email delivery utilities
    - Write `app/utils/helpers.py`: `generate_otp()` (6-digit), `create_otp_record()`, `validate_otp()` (checks expiry + used_at)
    - Write `app/services/notification_service.py`: `send_email()` using Flask-Mail with Gmail SMTP
    - _Requirements: 1.1, 1.3, 1.4_
  - [-] 3.2 Write property tests for OTP utilities
    - **Property 1: OTP Registration Round-Trip** — generate OTP, verify within window → account active
    - **Property 2: OTP Expiry Rejection** — OTP with past expires_at is rejected
    - **Property 3: OTP Single-Use Idempotence** — used OTP rejected on second submission
    - **Property 4: OTP Resend Invalidation** — after resend, old OTP invalid, new OTP valid
    - **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5**
  - [~] 3.3 Implement password hashing utility
    - Write `hash_password(plain: str) -> str` and `verify_password(plain: str, hashed: str) -> bool` using bcrypt with cost factor 12
    - _Requirements: 2.6_
  - [~] 3.4 Write property test for password hashing
    - **Property 7: Password Hash Correctness** — for any password, hash verifies with bcrypt cost factor 12
    - **Validates: Requirements 2.6**
  - [~] 3.5 Implement auth blueprint (`app/blueprints/auth/`)
    - POST `/api/auth/register` — validate fields, create pending user, create OTP, send email; enforce rate limit via Redis
    - POST `/api/auth/verify-otp` — validate OTP, activate account, redirect hint
    - POST `/api/auth/resend-otp` — invalidate old OTP, issue new OTP, send email
    - POST `/api/auth/login` — verify credentials, issue JWT (15min) + refresh token (httpOnly cookie); enforce 5-attempt lockout per IP via Redis
    - POST `/api/auth/refresh` — validate refresh cookie, issue new access token
    - POST `/api/auth/logout` — invalidate refresh token, clear cookie
    - POST `/api/auth/forgot-password` — send reset OTP
    - POST `/api/auth/reset-password` — validate OTP, update bcrypt hash, invalidate all sessions
    - _Requirements: 1.1–1.6, 2.1–2.6, 21.1–21.4_
  - [~] 3.6 Write property tests for auth blueprint
    - **Property 5: JWT Token Issuance Correctness** — valid credentials → JWT with correct claims
    - **Property 6: Logout Invalidates Refresh Token** — after logout, refresh token rejected
    - **Property 10: Login Brute-Force Blocking** — after 5 failures, 6th attempt blocked
    - **Validates: Requirements 2.1, 2.3, 2.5**
  - [~] 3.7 Implement role-based decorators
    - Write `app/utils/decorators.py`: `@role_required(roles: list)` decorator using Flask-JWT-Extended `get_jwt_identity()` and `get_jwt()`
    - Write `@audit_action(action_type, resource_type)` decorator that calls `audit_service.log()` after successful route execution
    - _Requirements: 3.1, 3.2_


- [~] 4. Checkpoint — Auth layer complete
  - Ensure all auth tests pass. Verify OTP flow end-to-end with a real Gmail SMTP test. Ask the user if questions arise.

- [ ] 5. File Upload, OCR, and Validation Services
  - [~] 5.1 Implement file validation utility
    - Write `app/utils/validators.py`: `validate_file(file_bytes, filename) -> (bool, str)` checking MIME type (python-magic) and size ≤ 5MB
    - Accepted MIME types: `image/jpeg`, `image/png`, `application/pdf`
    - _Requirements: 19.1, 19.2, 19.4_
  - [~] 5.2 Write property test for file validation
    - **Property 8: File Validation Rejects Invalid Inputs** — any file >5MB or wrong MIME type is rejected
    - **Validates: Requirements 4.3, 19.1, 19.2**
  - [~] 5.3 Implement Supabase Storage upload helper
    - Write `app/utils/storage.py`: `upload_file(bucket, path, file_bytes, content_type) -> str` returning public URL
    - Write `delete_file(bucket, path)` for cleanup
    - _Requirements: 19.3_
  - [~] 5.4 Implement OCR Processor service
    - Write `app/services/ocr_processor.py`: `extract_from_file(file_bytes, mime_type) -> dict`
    - Call Google Vision API `document_text_detection` for image files; `text_detection` for PDFs via Vision API PDF input
    - Pass extracted text through spaCy NLP pipeline to identify name, email, phone, education, experience, skills entities
    - Return structured dict: `{ name, email, phone, education: [], experience: [], skills: [] }`
    - Handle Vision API failures gracefully (return partial data, log error)
    - _Requirements: 4.1, 4.2, 11.1_
  - [~] 5.5 Write integration tests for OCR Processor
    - Test with sample JPG, PNG, PDF resume files (mocked Vision API responses)
    - Verify structured data extraction returns all expected keys
    - _Requirements: 4.1_


- [ ] 6. AI Matching Service
  - [~] 6.1 Implement AI_Matcher service
    - Write `app/services/ai_matcher.py`
    - `compute_match_score(jobseeker_profile: dict, vacancy: dict) -> float`: concatenate jobseeker skills + experience text and vacancy requirements + skills_required text; fit TF-IDF vectorizer; compute cosine similarity; return float in [0.0, 1.0]
    - `rank_vacancies(jobseeker_profile: dict, vacancies: list) -> list`: apply compute_match_score to each vacancy, attach `match_score` field, sort descending
    - `rank_applicants(vacancy: dict, applicants: list) -> list`: same pattern for applicant ranking
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [~] 6.2 Write property tests for AI_Matcher
    - **Property 9: AI Match Score Range and Ordering** — for any profile + vacancies list, all scores in [0.0, 1.0] and list sorted descending
    - **Validates: Requirements 7.1, 7.4**

- [ ] 7. Audit Trail Service
  - [~] 7.1 Implement Audit_Trail service
    - Write `app/services/audit_service.py`: `log(actor_id, actor_role, action_type, resource_type, resource_id, ip_address, metadata) -> None`
    - Insert into `audit_trail` table via supabase-py; never update or delete
    - _Requirements: 17.1, 17.2, 17.3_
  - [~] 7.2 Write property test for Audit Trail
    - **Property 14: Audit Trail Append on Significant Actions** — after any significant action, new audit entry exists with all required fields
    - **Validates: Requirements 17.1, 17.2**

- [ ] 8. Notification Service and Socket.io
  - [~] 8.1 Implement Notification_Service
    - Write `app/services/notification_service.py`: `send_inapp(user_id, event_type, payload)` — insert notification record + emit Socket.io event to user's room `f"user_{user_id}"`
    - `send_email(to_email, subject, template, context)` — render Jinja2 HTML template + send via Flask-Mail
    - `notify(user_id, event_type, payload, email_context)` — call both
    - _Requirements: 14.1, 14.2_
  - [~] 8.2 Configure Flask-SocketIO rooms and events
    - On client connect with valid JWT, join room `f"user_{user_id}"`
    - Define events: `notification`, `application_update`, `interview_update`, `announcement`
    - _Requirements: 14.1, 8.5_
  - [~] 8.3 Implement frontend Socket.io client singleton
    - Write `frontend/src/utils/socket.js`: create Socket.io-client instance with auth token, auto-reconnect
    - Write `useNotifications` React hook: listen for `notification` events, update Zustand notification store, show React Hot Toast
    - _Requirements: 14.1, 14.3, 14.4_


- [ ] 9. QR Code Service
  - [~] 9.1 Implement QR_Service
    - Write `app/services/qr_service.py`
    - `generate_qr(participant_id, event_id) -> bytes`: create HMAC-signed token `{participant_id}:{event_id}:{timestamp}`, generate QR PNG using `qrcode` library, return PNG bytes
    - `validate_scan(token, event_id) -> (bool, dict)`: verify HMAC signature, check token matches event_id, return participant data or error
    - _Requirements: 10.1, 10.3, 10.4_
  - [~] 9.2 Write property tests for QR_Service
    - **Property 11: QR Token Uniqueness** — N registrations produce N distinct tokens
    - **Property 12: QR Attendance Round-Trip** — valid token → validate_scan returns (True, data)
    - **Property 13: Invalid QR Rejection** — random/invalid token → validate_scan returns (False, error)
    - **Validates: Requirements 10.1, 10.3, 10.4**

- [ ] 10. PDF and Excel Export Services
  - [~] 10.1 Implement PDF generation service
    - Write `app/services/pdf_service.py`: `generate_referral_letter(application_data) -> bytes` using WeasyPrint with Jinja2 HTML template
    - `generate_lmi_report_pdf(report_data) -> bytes` using WeasyPrint with LMI report template
    - Store generated PDFs in Supabase Storage `referral-letters` / `lmi-reports` buckets
    - _Requirements: 8.4, 13.2_
  - [~] 10.2 Implement Excel export service
    - Write `app/services/excel_service.py`: `generate_attendance_excel(attendance_data) -> bytes` using OpenPyXL
    - `generate_lmi_report_excel(report_data) -> bytes` using OpenPyXL with formatted worksheets
    - `generate_program_enrollment_excel(enrollment_data) -> bytes`
    - _Requirements: 10.6, 11.6, 13.2_

- [ ] 11. LMI Report Generator and APScheduler
  - [~] 11.1 Implement LMI report computation logic
    - Write `app/services/lmi_generator.py`: `compute_lmi_stats(period_start, period_end) -> dict`
    - Query: total registered jobseekers, new registrations, total vacancies posted, total applications, hired count, program enrollment counts per type, top industries, employment type breakdown
    - _Requirements: 13.1, 13.4_
  - [~] 11.2 Implement Celery task for LMI report generation
    - Write `app/tasks/lmi_tasks.py`: `generate_lmi_report_task(report_type, period_start, period_end, triggered_by)`
    - Call `lmi_generator.compute_lmi_stats()`, generate PDF + Excel, upload to Supabase Storage, insert `lmi_reports` record, notify Staff/Admin
    - _Requirements: 13.1, 13.2, 13.3_
  - [~] 11.3 Configure APScheduler jobs
    - Write `app/scheduler.py`: schedule monthly (1st of each month), quarterly (Jan/Apr/Jul/Oct 1st), annual (Jan 1st) Celery task dispatches
    - _Requirements: 13.1_


- [~] 12. Checkpoint — Backend services complete
  - Ensure all service-layer tests pass. Verify Celery task execution with Redis. Ask the user if questions arise.

- [ ] 13. Jobseeker Blueprint API
  - [~] 13.1 Implement jobseeker profile endpoints
    - GET/PUT `/api/jobseeker/profile` — fetch and update jobseeker profile fields
    - POST `/api/jobseeker/profile/upload-resume` — validate file, call OCR_Processor, return extracted data for frontend pre-population; store file in `resumes` bucket
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [~] 13.2 Implement job search and matching endpoints
    - GET `/api/jobseeker/jobs` — fetch active vacancies, call `ai_matcher.rank_vacancies()`, return with match scores
    - _Requirements: 7.1, 7.2, 7.4_
  - [~] 13.3 Implement job application endpoints
    - POST `/api/jobseeker/jobs/:id/apply` — create application record, compute match score, notify employer
    - GET `/api/jobseeker/applications` — list applications with status history
    - _Requirements: 8.1, 8.5_
  - [~] 13.4 Implement interview and employment endpoints
    - GET `/api/jobseeker/interviews` — list scheduled interviews
    - GET `/api/jobseeker/employment` — employment history
    - _Requirements: 9.3, 12.3_
  - [~] 13.5 Implement program application endpoints
    - POST `/api/jobseeker/programs/:type/apply` — validate documents, call OCR_Processor, create program_application + program_documents records
    - GET `/api/jobseeker/programs` — list program applications with status
    - _Requirements: 11.1, 11.2_
  - [~] 13.6 Implement job fair registration endpoint
    - GET `/api/jobseeker/job-fairs` — list upcoming job fairs
    - POST `/api/jobseeker/job-fairs/:id/register` — create registration, generate QR, upload QR PNG to `qr-codes` bucket, send QR via email
    - _Requirements: 10.2_
  - [~] 13.7 Implement chatbot proxy endpoint
    - POST `/api/jobseeker/chatbot` — forward message to Dialogflow ES API, return response; enforce 3-second timeout with fallback message
    - _Requirements: 15.2, 15.4_
  - [~] 13.8 Implement notification endpoints
    - GET `/api/jobseeker/notifications` — list notifications with unread count
    - PATCH `/api/jobseeker/notifications/:id/read` — mark as read
    - _Requirements: 14.3, 14.4_


- [ ] 14. Employer Blueprint API
  - [~] 14.1 Implement employer profile endpoints
    - GET/PUT `/api/employer/profile` — fetch and update company profile; reflect changes on associated vacancies
    - _Requirements: 5.1, 5.2, 5.3_
  - [~] 14.2 Implement vacancy management endpoints
    - GET/POST `/api/employer/vacancies` — list employer's vacancies / create new vacancy (status: pending)
    - GET/PUT/DELETE `/api/employer/vacancies/:id` — manage single vacancy; DELETE sets status to closed
    - _Requirements: 6.1, 6.4_
  - [~] 14.3 Implement applicant management endpoints
    - GET `/api/employer/vacancies/:id/applicants` — list applicants with AI match scores (call `ai_matcher.rank_applicants()`)
    - PATCH `/api/employer/applications/:id/status` — update status (reviewed/shortlisted/rejected/hired); trigger notification; if hired, create employment_record
    - _Requirements: 7.3, 8.2, 8.3_
  - [~] 14.4 Implement interview management endpoints
    - GET/POST `/api/employer/interviews` — list/schedule interviews; on create, notify jobseeker
    - PUT/DELETE `/api/employer/interviews/:id` — update/cancel; notify jobseeker on change
    - _Requirements: 9.1, 9.2_
  - [~] 14.5 Implement employer dashboard and notification endpoints
    - GET `/api/employer/dashboard` — active vacancies count, total applicants, pending reviews, hired count
    - GET `/api/employer/notifications` — list notifications
    - _Requirements: 22.2, 14.3_

- [ ] 15. PESO Staff Blueprint API
  - [~] 15.1 Implement vacancy approval endpoints
    - GET `/api/staff/vacancies/pending` — list pending vacancies
    - PATCH `/api/staff/vacancies/:id/approve` — set status active, notify employer
    - PATCH `/api/staff/vacancies/:id/reject` — set status rejected with reason, notify employer
    - _Requirements: 6.2, 6.3, 6.5_
  - [~] 15.2 Implement referral letter generation endpoint
    - POST `/api/staff/applications/:id/referral` — generate PDF via `pdf_service.generate_referral_letter()`, upload to `referral-letters` bucket, insert referral_letters record, return download URL
    - _Requirements: 8.4_
  - [~] 15.3 Implement job fair management endpoints
    - GET/POST `/api/staff/job-fairs` — list/create job fair events
    - POST `/api/staff/job-fairs/:id/scan` — validate QR token, record attendance, emit real-time update
    - GET `/api/staff/job-fairs/:id/attendance` — attendance list; GET with `?format=excel` triggers Excel export
    - _Requirements: 10.1, 10.3, 10.4, 10.6_
  - [~] 15.4 Implement program management endpoints
    - GET/PATCH `/api/staff/programs/spes`, `/dilp`, `/owwa`, `/mst` — list applications, approve/reject with reason, notify jobseeker
    - GET `/api/staff/programs/:type/export` — Excel export of enrollment data
    - _Requirements: 11.2, 11.3, 11.4, 11.6_
  - [~] 15.5 Implement employment monitoring endpoints
    - GET `/api/staff/employment` — list all employment records
    - PATCH `/api/staff/employment/:id` — update start_date, end_date, employment_type, status
    - _Requirements: 12.1, 12.2_
  - [~] 15.6 Implement LMI report endpoints
    - GET `/api/staff/lmi-reports` — list generated reports with download URLs
    - POST `/api/staff/lmi-reports/generate` — dispatch Celery task for manual generation with date range
    - _Requirements: 13.3, 13.4_
  - [~] 15.7 Implement announcements and staff dashboard endpoints
    - POST `/api/staff/announcements` — create announcement, broadcast to all jobseekers or employers via Notification_Service
    - GET `/api/staff/dashboard` — total jobseekers, active vacancies, pending approvals, upcoming job fairs, program enrollment counts
    - GET `/api/staff/interviews` — all interview schedules across employers
    - _Requirements: 14.5, 22.3, 9.4_


- [ ] 16. Admin Blueprint API
  - [~] 16.1 Implement staff account management endpoints
    - GET `/api/admin/staff` — list all staff accounts with active/inactive status
    - POST `/api/admin/staff` — create staff account, generate temp password (bcrypt), send credentials via email, set first_login=true
    - PATCH `/api/admin/staff/:id/activate` — toggle is_active; on deactivate, invalidate all active sessions (blacklist JWTs in Redis)
    - _Requirements: 16.1, 16.3, 16.4_
  - [~] 16.2 Implement audit trail search endpoint
    - GET `/api/admin/audit-trail` — paginated list with filters: user_id, role, action_type, date_from, date_to, resource_type
    - _Requirements: 17.4_
  - [~] 16.3 Implement system settings endpoints
    - GET/PUT `/api/admin/settings` — fetch all settings / update key-value pairs; apply immediately (update Redis cache); log to audit trail
    - _Requirements: 18.1, 18.2, 18.3_
  - [~] 16.4 Implement admin dashboard endpoint
    - GET `/api/admin/dashboard` — all staff stats + active session count (from Redis) + recent audit trail entries (last 10)
    - _Requirements: 22.4_
  - [~] 16.5 Write property test for API response shape
    - **Property 15: API Response Shape Invariant** — for any endpoint, response has keys success (bool), data (obj/null), message (str)
    - **Validates: Requirements 20.1, 20.2, 20.3**

- [~] 17. Checkpoint — All backend APIs complete
  - Ensure all blueprint tests pass. Test role guard decorator on cross-role access attempts. Verify audit trail entries for all significant actions. Ask the user if questions arise.


- [ ] 18. Frontend — Auth and Routing Foundation
  - [~] 18.1 Implement Zustand auth store and Axios interceptors
    - Write `src/store/authStore.js`: state (user, accessToken, role), actions (setAuth, clearAuth)
    - Configure Axios instance: attach `Authorization: Bearer <token>` header; on 401 response, call refresh endpoint and retry; on 403, redirect to role dashboard
    - _Requirements: 2.1, 2.2, 3.1_
  - [~] 18.2 Implement ProtectedRoute and RoleGuard components
    - Write `src/components/auth/ProtectedRoute.jsx`: redirect to `/login` if no valid token
    - Write `src/components/auth/RoleGuard.jsx`: redirect to role dashboard if role mismatch; return 403 UI for unauthorized access
    - _Requirements: 3.1, 3.2_
  - [~] 18.3 Implement React Router v6 route configuration
    - Configure routes: `/` (public), `/login`, `/register`, `/verify-otp`, `/forgot-password`, `/reset-password`
    - Nested routes under `/jobseeker/*`, `/employer/*`, `/staff/*`, `/admin/*` wrapped in ProtectedRoute + RoleGuard
    - _Requirements: 3.3, 3.4, 3.5, 3.6_
  - [~] 18.4 Implement auth pages
    - `LoginPage.jsx` — React Hook Form + Zod, submit to `/api/auth/login`, store token in Zustand, redirect to role dashboard
    - `RegisterPage.jsx` — role selection (Jobseeker/Employer), form with validation, submit to `/api/auth/register`
    - `OTPVerificationPage.jsx` — 6-digit OTP input, resend button with countdown timer
    - `ForgotPasswordPage.jsx` and `ResetPasswordPage.jsx`
    - _Requirements: 1.1, 1.2, 1.5, 21.1, 21.2_
  - [~] 18.5 Implement first-login forced password change for Staff
    - After staff login, check `first_login` flag in JWT claims; if true, redirect to `/staff/change-password` before any other route
    - _Requirements: 16.2_


- [ ] 19. Frontend — Shared Components
  - [~] 19.1 Implement shared layout components
    - `Sidebar.jsx` — role-specific navigation links with Lucide React icons; active route highlighting
    - `Navbar.jsx` — user avatar, role badge, NotificationBell, logout button
    - `NotificationBell.jsx` — unread count badge, dropdown notification list, mark-as-read on click
    - `DashboardLayout.jsx` — wraps Sidebar + Navbar + main content area
    - _Requirements: 14.3, 14.4_
  - [~] 19.2 Implement Zustand notification store and Socket.io integration
    - Write `src/store/notificationStore.js`: state (notifications[], unreadCount), actions (addNotification, markRead, setAll)
    - Wire `useNotifications` hook to Socket.io `notification` event; update store + show React Hot Toast
    - _Requirements: 14.1, 14.3, 14.4_
  - [~] 19.3 Implement file upload component
    - `FileUpload.jsx` using React Dropzone: accept JPG/PNG/PDF, max 5MB, show preview, display validation errors
    - _Requirements: 19.1, 19.2_
  - [~] 19.4 Implement PDF viewer component
    - `PDFViewer.jsx` using React PDF Viewer: display referral letters and LMI reports in-browser
    - _Requirements: 8.4, 13.3_

- [ ] 20. Frontend — Jobseeker Pages (13 modules)
  - [~] 20.1 Implement Jobseeker Dashboard
    - `pages/jobseeker/Dashboard.jsx` — React Query fetch `/api/jobseeker/dashboard`; Recharts bar/pie charts for applications, interviews, matches
    - _Requirements: 22.1_
  - [~] 20.2 Implement Jobseeker Profile and OCR Resume Upload
    - `pages/jobseeker/Profile.jsx` — display/edit profile fields; FileUpload component for resume; on upload, call `/api/jobseeker/profile/upload-resume`, pre-populate form fields with OCR data; confirm + save
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  - [~] 20.3 Implement Job Search and Matching page
    - `pages/jobseeker/JobSearch.jsx` — TanStack Table with search/filter; match score badge per vacancy; sort by match score default; apply button
    - _Requirements: 7.1, 7.2, 7.4_
  - [~] 20.4 Implement My Applications page
    - `pages/jobseeker/MyApplications.jsx` — TanStack Table with status badges; real-time status updates via Socket.io; referral letter download button
    - _Requirements: 8.5, 8.4_
  - [~] 20.5 Implement Interview Schedule page
    - `pages/jobseeker/InterviewSchedule.jsx` — list of scheduled interviews with Day.js formatted dates; status badges
    - _Requirements: 9.3_
  - [~] 20.6 Implement Program Applications pages (SPES, DILP, OWWA, MST)
    - `pages/jobseeker/Programs.jsx` — tabs per program type; application form with FileUpload for required documents; status tracking
    - _Requirements: 11.1_
  - [~] 20.7 Implement Employment Monitoring page
    - `pages/jobseeker/Employment.jsx` — employment history list with dates and employer info
    - _Requirements: 12.3_
  - [~] 20.8 Implement Job Fair Registration page
    - `pages/jobseeker/JobFairs.jsx` — list upcoming job fairs; register button; show QR code after registration
    - _Requirements: 10.2_
  - [~] 20.9 Implement Notifications page and Chatbot widget
    - `pages/jobseeker/Notifications.jsx` — full notification list with read/unread state
    - `components/chatbot/ChatbotWidget.jsx` — floating button (Framer Motion), chat window, message input, Dialogflow response display; available on all jobseeker pages
    - _Requirements: 14.3, 15.1, 15.2, 15.3, 15.4_


- [ ] 21. Frontend — Employer Pages (10 modules)
  - [~] 21.1 Implement Employer Dashboard
    - `pages/employer/Dashboard.jsx` — Recharts charts for active vacancies, applicants, hired count
    - _Requirements: 22.2_
  - [~] 21.2 Implement Company Profile page
    - `pages/employer/Profile.jsx` — edit company name, industry, address, contact, description, logo upload
    - _Requirements: 5.2, 5.3_
  - [~] 21.3 Implement Vacancy Management pages
    - `pages/employer/Vacancies.jsx` — TanStack Table with status badges; create/edit vacancy form (React Hook Form + Zod); close vacancy action
    - `pages/employer/VacancyDetail.jsx` — vacancy details + applicant list with AI match scores; status update dropdown per applicant
    - _Requirements: 6.1, 6.4, 7.3, 8.2_
  - [~] 21.4 Implement Interview Management page
    - `pages/employer/Interviews.jsx` — schedule interview form (date/time picker with Day.js); list of scheduled interviews; edit/cancel actions
    - _Requirements: 9.1, 9.2_
  - [~] 21.5 Implement Employer Job Fair and Notifications pages
    - `pages/employer/JobFairs.jsx` — list job fairs with participation status
    - `pages/employer/Notifications.jsx` — notification list
    - _Requirements: 10.5, 14.3_

- [ ] 22. Frontend — PESO Staff Pages (15 modules)
  - [~] 22.1 Implement Staff Dashboard
    - `pages/staff/Dashboard.jsx` — Recharts charts for jobseekers, vacancies, pending approvals, job fairs, program enrollments
    - _Requirements: 22.3_
  - [~] 22.2 Implement Vacancy Approval module
    - `pages/staff/VacancyApprovals.jsx` — list pending vacancies; approve/reject with reason modal
    - _Requirements: 6.2, 6.3, 6.5_
  - [~] 22.3 Implement Application Oversight and Referral Letter module
    - `pages/staff/Applications.jsx` — all applications across employers; generate referral letter button; PDF viewer modal
    - _Requirements: 8.4_
  - [~] 22.4 Implement Job Fair Management and QR Scanner module
    - `pages/staff/JobFairs.jsx` — create/manage job fair events; attendance list with real-time updates
    - `pages/staff/QRScanner.jsx` — React Webcam + html5-qrcode scanner; real-time attendance feedback; export attendance to Excel
    - _Requirements: 10.1, 10.3, 10.4, 10.6_
  - [~] 22.5 Implement Program Management modules (SPES, DILP, OWWA, MST)
    - `pages/staff/Programs.jsx` — tabbed interface per program; application list with OCR data display; approve/reject with reason; Excel export
    - _Requirements: 11.2, 11.3, 11.4, 11.6_
  - [~] 22.6 Implement Employment Monitoring module
    - `pages/staff/Employment.jsx` — TanStack Table of all employment records; inline edit for start/end date, type, status
    - _Requirements: 12.1, 12.2_
  - [~] 22.7 Implement LMI Reports module
    - `pages/staff/LMIReports.jsx` — list generated reports with PDF/Excel download links; manual generation form with date range picker
    - _Requirements: 13.3, 13.4_
  - [~] 22.8 Implement Announcements and Interview Oversight modules
    - `pages/staff/Announcements.jsx` — create announcement form; target audience selector (all jobseekers / all employers)
    - `pages/staff/InterviewOversight.jsx` — read-only view of all interview schedules
    - _Requirements: 14.5, 9.4_


- [ ] 23. Frontend — Admin Pages (17 modules)
  - [~] 23.1 Implement Admin Dashboard
    - `pages/admin/Dashboard.jsx` — all staff stats + active session count + recent audit trail entries; Recharts system health charts
    - _Requirements: 22.4_
  - [~] 23.2 Implement Staff Account Management module
    - `pages/admin/StaffAccounts.jsx` — TanStack Table of staff accounts; create staff form; activate/deactivate toggle with confirmation modal
    - _Requirements: 16.1, 16.3, 16.4_
  - [~] 23.3 Implement Audit Trail module
    - `pages/admin/AuditTrail.jsx` — TanStack Table with server-side pagination; filter panel (user, role, action_type, date range, resource_type)
    - _Requirements: 17.4_
  - [~] 23.4 Implement System Settings module
    - `pages/admin/SystemSettings.jsx` — form for all configurable settings (session timeouts, rate limits, OTP expiry, file size limit); save applies immediately
    - _Requirements: 18.1, 18.2, 18.3_
  - [~] 23.5 Implement Admin LMI Reports and User Overview modules
    - `pages/admin/LMIReports.jsx` — same as staff LMI module with admin access
    - `pages/admin/Users.jsx` — overview of all users by role with account status
    - _Requirements: 13.3, 22.4_

- [~] 24. Checkpoint — All frontend pages complete
  - Ensure all React components render without errors. Test ProtectedRoute and RoleGuard with all four roles. Verify Socket.io notifications end-to-end. Ask the user if questions arise.

- [ ] 25. Integration — Wire Frontend to Backend
  - [~] 25.1 Implement all React Query hooks for API calls
    - Write `src/hooks/` files per domain: `useAuth`, `useJobseeker`, `useEmployer`, `useStaff`, `useAdmin`
    - Configure query keys, stale time, cache invalidation on mutations
    - _Requirements: 8.5, 14.4_
  - [~] 25.2 Implement Zod validation schemas for all forms
    - Write `src/utils/validators.js` with Zod schemas for: registration, login, profile, vacancy, application, program application, job fair, interview, staff creation, system settings
    - _Requirements: 1.1, 4.1, 6.1_
  - [~] 25.3 Implement session timeout idle detection
    - Write `useIdleTimeout` hook: track user activity events (mousemove, keydown, click); after role-specific timeout (from system_settings), call logout and redirect to login
    - _Requirements: 2.4_
  - [~] 25.4 Implement Framer Motion page transitions
    - Wrap page components with Framer Motion `AnimatePresence` and `motion.div` for smooth route transitions
    - _Requirements: (UX enhancement)_


- [ ] 26. Deployment Configuration
  - [~] 26.1 Configure backend for production deployment
    - Write `Procfile` and `gunicorn.conf.py` for Gunicorn with gevent worker class (required for Flask-SocketIO)
    - Configure CORS to allow only the Vercel frontend domain
    - Write `Dockerfile` for containerized deployment (optional)
    - _Requirements: 20.4_
  - [~] 26.2 Configure frontend for production build
    - Set `VITE_API_BASE_URL` and `VITE_SOCKET_URL` environment variables for production
    - Configure Vite build output for Vercel deployment (`vercel.json` with SPA rewrite rules)
    - _Requirements: 20.4_
  - [~] 26.3 Configure environment variables and secrets
    - Document all required environment variables in `backend/.env.example` and `frontend/.env.example`
    - Verify Supabase credentials, Gmail SMTP app password, Redis URL, Google Vision credentials, Dialogflow project ID are all configured
    - _Requirements: 1.1, 2.1, 15.2_

- [~] 27. Final Checkpoint — Full system integration
  - Run full test suite (pytest + vitest). Verify end-to-end flows: registration → OTP → login → job application → status update → notification. Verify LMI report generation via manual trigger. Verify QR attendance scan flow. Ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for a faster MVP
- Each task references specific requirements for traceability
- Checkpoints at tasks 4, 12, 17, 24, 27 ensure incremental validation
- Property tests use `hypothesis` library (Python) with minimum 100 iterations each
- Unit tests use `pytest` + `pytest-flask` (backend) and `vitest` + `@testing-library/react` (frontend)
- All property tests are tagged: **Feature: jobbridge-system, Property N: <property_text>**
- The Supabase credentials, Gmail SMTP credentials, and other secrets must be stored in `.env` files and never committed to version control
- The `audit_trail` table must have RLS policies that prevent UPDATE and DELETE for all roles including service_role
- Celery workers must be started separately from the Flask app: `celery -A celery_worker.celery worker --loglevel=info`
- APScheduler runs inside the Flask app process; ensure only one instance runs in production (use Redis lock)
