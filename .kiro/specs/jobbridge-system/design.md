# Design Document: JobBridge System

## Overview

JobBridge is a full-stack web application for PESO Pila, Laguna that digitizes employment operations. It serves four roles (Jobseeker, Employer, PESO Staff, Admin) across dedicated route namespaces. The system integrates AI-powered job matching (TF-IDF + Cosine Similarity), OCR resume parsing (Google Vision API + spaCy), a Dialogflow ES chatbot, real-time notifications (Socket.io), QR-based attendance, automated LMI report generation (APScheduler), and PDF/Excel export capabilities.

**Technology Stack:**
- Frontend: React 18 + Vite, Tailwind CSS, Shadcn/UI, React Router v6, Axios, React Query, Socket.io-client, Zustand, Recharts, React Hook Form + Zod, Framer Motion, Day.js, Lucide React, TanStack Table, html5-qrcode, React Webcam, React Dropzone, React PDF Viewer, React Hot Toast
- Backend: Python 3.11+, Flask, Flask-SocketIO, Flask-Mail, Flask-JWT-Extended, Flask-CORS, supabase-py, Google Vision API, scikit-learn, spaCy, Dialogflow ES, APScheduler, Celery + Redis, WeasyPrint, OpenPyXL, Marshmallow, Gunicorn
- Database: Supabase (PostgreSQL) + Supabase Storage + Supabase Realtime
- Cache/Queue: Redis (Celery broker + rate limiting)


## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT (Browser)                          │
│  React 18 + Vite SPA                                            │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │Jobseeker │ │Employer  │ │PESO Staff│ │  Admin   │          │
│  │/jobseeker│ │/employer │ │ /staff   │ │ /admin   │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  Zustand (state) │ React Query (server state) │ Socket.io-client│
└──────────────────────────────────────────────────────────────────┘
                          │ HTTPS / WSS
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (Flask + Gunicorn)                   │
│  Flask Blueprints per role + shared services                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐          │
│  │auth_bp   │ │jobseeker │ │employer  │ │staff_bp  │          │
│  │          │ │_bp       │ │_bp       │ │admin_bp  │          │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘          │
│  ┌──────────────────────────────────────────────────┐          │
│  │  Shared Services                                  │          │
│  │  AI_Matcher │ OCR_Processor │ Notification_Service│          │
│  │  QR_Scanner │ LMI_Generator │ Audit_Trail_Service │          │
│  └──────────────────────────────────────────────────┘          │
│  Flask-SocketIO (WebSocket) │ APScheduler │ Celery Workers      │
└──────────────────────────────────────────────────────────────────┘
         │                    │                    │
┌────────┴──────┐   ┌─────────┴──────┐   ┌────────┴──────┐
│   Supabase    │   │     Redis       │   │  External APIs │
│  PostgreSQL   │   │  Cache + Queue  │   │  Google Vision │
│  Storage      │   │  Rate Limiting  │   │  Dialogflow ES │
│  Realtime     │   │  Celery Broker  │   │  Gmail SMTP    │
└───────────────┘   └────────────────┘   └───────────────┘
```


### Request Flow

```
Browser → Vite Dev Server (dev) / CDN (prod)
       → Axios (with JWT Bearer header)
       → Flask Blueprint route
       → JWT verification middleware
       → Role guard decorator
       → Business logic / service layer
       → supabase-py (DB queries)
       → JSON response { success, data, message }
```

### Real-Time Flow

```
Event (e.g., application status change)
  → Flask route updates DB
  → Notification_Service.emit(user_id, event_type, payload)
  → Flask-SocketIO broadcasts to user's room
  → Socket.io-client receives event
  → React Query cache invalidated / Zustand store updated
  → UI re-renders with new notification badge
```

### Background Task Flow

```
APScheduler trigger (monthly/quarterly/annual)
  → Celery task dispatched via Redis broker
  → Worker: query DB, compute LMI stats
  → WeasyPrint → PDF, OpenPyXL → Excel
  → Upload to Supabase Storage
  → Insert LMI report record in DB
  → Notify PESO Staff / Admin via Notification_Service
```


## Components and Interfaces

### Backend Blueprint Structure

```
backend/
├── app/
│   ├── __init__.py              # Flask app factory, register blueprints
│   ├── extensions.py            # JWT, CORS, SocketIO, Mail, Supabase client
│   ├── config.py                # Config classes (Dev, Prod) from .env
│   ├── blueprints/
│   │   ├── auth/                # /api/auth — login, register, OTP, refresh, logout
│   │   ├── jobseeker/           # /api/jobseeker — profile, jobs, applications, programs
│   │   ├── employer/            # /api/employer — profile, vacancies, applicants, interviews
│   │   ├── staff/               # /api/staff — approvals, job fairs, programs, reports
│   │   └── admin/               # /api/admin — staff mgmt, audit trail, settings
│   ├── services/
│   │   ├── ai_matcher.py        # TF-IDF + Cosine Similarity
│   │   ├── ocr_processor.py     # Google Vision API + spaCy
│   │   ├── notification_service.py  # Socket.io emit + Flask-Mail
│   │   ├── qr_service.py        # QR code generation + validation
│   │   ├── lmi_generator.py     # LMI report computation + export
│   │   ├── audit_service.py     # Append-only audit trail writes
│   │   ├── pdf_service.py       # WeasyPrint PDF generation
│   │   └── excel_service.py     # OpenPyXL Excel export
│   ├── models/                  # SQLAlchemy ORM models
│   ├── schemas/                 # Marshmallow serialization schemas
│   ├── tasks/                   # Celery task definitions
│   ├── scheduler.py             # APScheduler job definitions
│   └── utils/
│       ├── decorators.py        # role_required, audit_action decorators
│       ├── validators.py        # File type/size validators
│       └── helpers.py           # OTP generation, token helpers
├── celery_worker.py
├── wsgi.py
└── requirements.txt
```

### Frontend Module Structure

```
frontend/
├── src/
│   ├── main.jsx
│   ├── App.jsx                  # Router root with ProtectedRoute + RoleGuard
│   ├── store/                   # Zustand stores (auth, notifications, ui)
│   ├── api/                     # Axios instance + per-module API functions
│   ├── hooks/                   # Custom React Query hooks per domain
│   ├── components/
│   │   ├── common/              # Shared UI (Navbar, Sidebar, NotificationBell)
│   │   ├── auth/                # Login, Register, OTP, ForgotPassword forms
│   │   └── chatbot/             # Floating chatbot widget
│   ├── pages/
│   │   ├── jobseeker/           # 13 modules
│   │   ├── employer/            # 10 modules
│   │   ├── staff/               # 15 modules
│   │   └── admin/               # 17 modules
│   └── utils/
│       ├── socket.js            # Socket.io-client singleton
│       └── validators.js        # Zod schemas
```


### Key API Interfaces

#### Authentication Blueprint (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /register | Jobseeker/Employer registration |
| POST | /verify-otp | OTP verification + account activation |
| POST | /resend-otp | Invalidate old OTP, issue new |
| POST | /login | Issue JWT + refresh token cookie |
| POST | /refresh | Rotate access token using refresh cookie |
| POST | /logout | Invalidate refresh token |
| POST | /forgot-password | Send password reset OTP |
| POST | /reset-password | Validate OTP + update password hash |

#### Jobseeker Blueprint (`/api/jobseeker`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | /profile | Get/update jobseeker profile |
| POST | /profile/upload-resume | OCR resume parsing |
| GET | /jobs | Job search with AI match scores |
| POST | /jobs/:id/apply | Submit application |
| GET | /applications | List applications with status |
| GET | /interviews | List scheduled interviews |
| POST | /programs/:type/apply | Apply for SPES/DILP/OWWA/MST |
| GET | /programs | List program applications |
| GET | /employment | Employment history |
| GET | /notifications | List notifications |
| PATCH | /notifications/:id/read | Mark notification read |
| POST | /chatbot | Proxy to Dialogflow ES |
| GET | /job-fairs | List available job fairs |
| POST | /job-fairs/:id/register | Register for job fair |

#### Employer Blueprint (`/api/employer`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/PUT | /profile | Company profile |
| GET/POST | /vacancies | List/create vacancies |
| GET/PUT/DELETE | /vacancies/:id | Manage single vacancy |
| GET | /vacancies/:id/applicants | Applicants with match scores |
| PATCH | /applications/:id/status | Update application status |
| GET/POST | /interviews | List/schedule interviews |
| PUT/DELETE | /interviews/:id | Update/cancel interview |
| GET | /job-fairs | Employer job fair participation |
| GET | /notifications | Notifications |
| GET | /dashboard | Dashboard stats |

#### Staff Blueprint (`/api/staff`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /vacancies/pending | Pending vacancy approvals |
| PATCH | /vacancies/:id/approve | Approve vacancy |
| PATCH | /vacancies/:id/reject | Reject vacancy with reason |
| GET | /applications | All applications oversight |
| POST | /applications/:id/referral | Generate referral letter PDF |
| GET/POST | /job-fairs | List/create job fair events |
| POST | /job-fairs/:id/scan | QR attendance scan |
| GET | /job-fairs/:id/attendance | Attendance report |
| GET/POST | /programs/spes | SPES management |
| GET/POST | /programs/dilp | DILP management |
| GET/POST | /programs/owwa | OWWA management |
| GET/POST | /programs/mst | Manpower Skills Training |
| GET | /employment | Employment monitoring |
| GET | /lmi-reports | LMI report list |
| POST | /lmi-reports/generate | Manual LMI generation |
| POST | /announcements | Create announcement |
| GET | /interviews | Interview oversight |
| GET | /dashboard | Staff dashboard stats |

#### Admin Blueprint (`/api/admin`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET/POST | /staff | List/create staff accounts |
| PATCH | /staff/:id/activate | Activate/deactivate staff |
| GET | /audit-trail | Search/filter audit trail |
| GET/PUT | /settings | System settings |
| GET | /dashboard | Admin dashboard stats |
| GET | /users | All users overview |


### Service Interfaces

#### AI_Matcher Service
```python
class AIMatcher:
    def compute_match_score(jobseeker_profile: dict, vacancy: dict) -> float:
        """Returns cosine similarity score 0.0–1.0 using TF-IDF on skills + experience text."""

    def rank_vacancies(jobseeker_profile: dict, vacancies: list[dict]) -> list[dict]:
        """Returns vacancies sorted by match_score descending."""

    def rank_applicants(vacancy: dict, applicants: list[dict]) -> list[dict]:
        """Returns applicants sorted by match_score descending."""
```

#### OCR_Processor Service
```python
class OCRProcessor:
    def extract_from_file(file_bytes: bytes, mime_type: str) -> dict:
        """Calls Google Vision API, then spaCy NLP to extract structured resume data."""
        # Returns: { name, email, phone, education: [], experience: [], skills: [] }

    def validate_file(file_bytes: bytes, filename: str) -> tuple[bool, str]:
        """Validates MIME type and file size. Returns (is_valid, error_message)."""
```

#### Notification_Service
```python
class NotificationService:
    def send_inapp(user_id: str, event_type: str, payload: dict) -> None:
        """Emits Socket.io event to user's room and inserts notification record."""

    def send_email(to_email: str, subject: str, template: str, context: dict) -> None:
        """Sends email via Flask-Mail (Gmail SMTP)."""

    def notify(user_id: str, event_type: str, payload: dict, email_context: dict) -> None:
        """Calls both send_inapp and send_email."""
```

#### QR_Service
```python
class QRService:
    def generate_qr(participant_id: str, event_id: str) -> bytes:
        """Generates QR code PNG bytes encoding a signed token."""

    def validate_scan(token: str, event_id: str) -> tuple[bool, dict]:
        """Validates scanned QR token. Returns (is_valid, participant_data)."""
```


## Data Models

### Entity Relationship Overview

```
users ──< jobseeker_profiles
users ──< employer_profiles ──< company_profiles
users ──< otp_tokens
users ──< notifications
users ──< audit_trail

job_vacancies >── employer_profiles
job_vacancies ──< job_applications
job_vacancies ──< employment_records

job_applications >── jobseeker_profiles
job_applications ──< interviews
job_applications ──< referral_letters

job_fairs ──< job_fair_registrations >── jobseeker_profiles
job_fairs ──< job_fair_attendance

program_applications >── jobseeker_profiles
program_applications ──< program_documents

employment_records >── jobseeker_profiles
employment_records >── employer_profiles

lmi_reports
system_settings
```

### Core Tables (Supabase PostgreSQL)

#### `users`
```sql
id            UUID PRIMARY KEY DEFAULT gen_random_uuid()
email         VARCHAR(255) UNIQUE NOT NULL
password_hash VARCHAR(255) NOT NULL
role          VARCHAR(20) NOT NULL  -- 'jobseeker','employer','staff','admin'
is_active     BOOLEAN DEFAULT false
is_verified   BOOLEAN DEFAULT false
first_login   BOOLEAN DEFAULT true  -- for staff forced password change
created_at    TIMESTAMPTZ DEFAULT now()
updated_at    TIMESTAMPTZ DEFAULT now()
```

#### `otp_tokens`
```sql
id          UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id     UUID REFERENCES users(id) ON DELETE CASCADE
token       VARCHAR(6) NOT NULL
purpose     VARCHAR(30) NOT NULL  -- 'registration','password_reset'
expires_at  TIMESTAMPTZ NOT NULL
used_at     TIMESTAMPTZ
created_at  TIMESTAMPTZ DEFAULT now()
```

#### `jobseeker_profiles`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE
first_name      VARCHAR(100)
last_name       VARCHAR(100)
middle_name     VARCHAR(100)
birthdate       DATE
gender          VARCHAR(20)
civil_status    VARCHAR(30)
address         TEXT
phone           VARCHAR(20)
education       JSONB   -- [{degree, school, year_graduated}]
experience      JSONB   -- [{company, position, start_date, end_date, description}]
skills          TEXT[]
resume_url      TEXT
profile_photo   TEXT
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

#### `employer_profiles`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE
company_name    VARCHAR(255)
industry        VARCHAR(100)
address         TEXT
phone           VARCHAR(20)
website         VARCHAR(255)
description     TEXT
logo_url        TEXT
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```


#### `job_vacancies`
```sql
id                UUID PRIMARY KEY DEFAULT gen_random_uuid()
employer_id       UUID REFERENCES employer_profiles(id) ON DELETE CASCADE
title             VARCHAR(255) NOT NULL
description       TEXT NOT NULL
requirements      TEXT NOT NULL
skills_required   TEXT[]
employment_type   VARCHAR(50)   -- 'full-time','part-time','contract','temporary'
salary_min        NUMERIC(12,2)
salary_max        NUMERIC(12,2)
slots             INTEGER DEFAULT 1
status            VARCHAR(20) DEFAULT 'pending'  -- 'pending','active','rejected','closed'
rejection_reason  TEXT
approved_by       UUID REFERENCES users(id)
approved_at       TIMESTAMPTZ
created_at        TIMESTAMPTZ DEFAULT now()
updated_at        TIMESTAMPTZ DEFAULT now()
```

#### `job_applications`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
vacancy_id      UUID REFERENCES job_vacancies(id) ON DELETE CASCADE
jobseeker_id    UUID REFERENCES jobseeker_profiles(id) ON DELETE CASCADE
status          VARCHAR(30) DEFAULT 'pending'  -- 'pending','reviewed','shortlisted','rejected','hired'
match_score     NUMERIC(5,4)
cover_letter    TEXT
applied_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
UNIQUE(vacancy_id, jobseeker_id)
```

#### `interviews`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
application_id  UUID REFERENCES job_applications(id) ON DELETE CASCADE
scheduled_at    TIMESTAMPTZ NOT NULL
location        TEXT
meeting_link    TEXT
notes           TEXT
status          VARCHAR(20) DEFAULT 'scheduled'  -- 'scheduled','completed','cancelled'
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

#### `referral_letters`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
application_id  UUID REFERENCES job_applications(id) ON DELETE CASCADE
generated_by    UUID REFERENCES users(id)
pdf_url         TEXT NOT NULL
generated_at    TIMESTAMPTZ DEFAULT now()
```

#### `job_fairs`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
title           VARCHAR(255) NOT NULL
description     TEXT
event_date      DATE NOT NULL
start_time      TIME NOT NULL
end_time        TIME NOT NULL
venue           TEXT NOT NULL
status          VARCHAR(20) DEFAULT 'upcoming'  -- 'upcoming','ongoing','completed','cancelled'
created_by      UUID REFERENCES users(id)
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

#### `job_fair_registrations`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
job_fair_id     UUID REFERENCES job_fairs(id) ON DELETE CASCADE
jobseeker_id    UUID REFERENCES jobseeker_profiles(id) ON DELETE CASCADE
qr_token        TEXT UNIQUE NOT NULL
qr_url          TEXT
registered_at   TIMESTAMPTZ DEFAULT now()
UNIQUE(job_fair_id, jobseeker_id)
```

#### `job_fair_attendance`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
registration_id UUID REFERENCES job_fair_registrations(id) ON DELETE CASCADE
scanned_by      UUID REFERENCES users(id)
scanned_at      TIMESTAMPTZ DEFAULT now()
```


#### `program_applications`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
jobseeker_id    UUID REFERENCES jobseeker_profiles(id) ON DELETE CASCADE
program_type    VARCHAR(20) NOT NULL  -- 'spes','dilp','owwa','mst'
status          VARCHAR(20) DEFAULT 'pending'  -- 'pending','approved','rejected'
decision_reason TEXT
reviewed_by     UUID REFERENCES users(id)
reviewed_at     TIMESTAMPTZ
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

#### `program_documents`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
application_id  UUID REFERENCES program_applications(id) ON DELETE CASCADE
document_type   VARCHAR(100) NOT NULL
file_url        TEXT NOT NULL
ocr_data        JSONB
uploaded_at     TIMESTAMPTZ DEFAULT now()
```

#### `employment_records`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
jobseeker_id    UUID REFERENCES jobseeker_profiles(id) ON DELETE CASCADE
employer_id     UUID REFERENCES employer_profiles(id)
vacancy_id      UUID REFERENCES job_vacancies(id)
application_id  UUID REFERENCES job_applications(id)
employment_type VARCHAR(50)
start_date      DATE
end_date        DATE
status          VARCHAR(20) DEFAULT 'active'  -- 'active','ended'
created_at      TIMESTAMPTZ DEFAULT now()
updated_at      TIMESTAMPTZ DEFAULT now()
```

#### `notifications`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
user_id         UUID REFERENCES users(id) ON DELETE CASCADE
event_type      VARCHAR(100) NOT NULL
title           VARCHAR(255) NOT NULL
body            TEXT
payload         JSONB
is_read         BOOLEAN DEFAULT false
created_at      TIMESTAMPTZ DEFAULT now()
```

#### `audit_trail`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
actor_id        UUID REFERENCES users(id)
actor_role      VARCHAR(20) NOT NULL
action_type     VARCHAR(100) NOT NULL
resource_type   VARCHAR(100)
resource_id     UUID
ip_address      INET
metadata        JSONB
created_at      TIMESTAMPTZ DEFAULT now()
-- No UPDATE or DELETE permissions granted on this table
```

#### `lmi_reports`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
report_type     VARCHAR(20) NOT NULL  -- 'monthly','quarterly','annual','custom'
period_start    DATE NOT NULL
period_end      DATE NOT NULL
pdf_url         TEXT
excel_url       TEXT
generated_by    UUID REFERENCES users(id)
generated_at    TIMESTAMPTZ DEFAULT now()
```

#### `system_settings`
```sql
id              UUID PRIMARY KEY DEFAULT gen_random_uuid()
key             VARCHAR(100) UNIQUE NOT NULL
value           TEXT NOT NULL
description     TEXT
updated_by      UUID REFERENCES users(id)
updated_at      TIMESTAMPTZ DEFAULT now()
```

### Supabase Storage Buckets
| Bucket | Contents | Access |
|--------|----------|--------|
| `resumes` | Jobseeker resume files | Owner + Staff + Admin |
| `program-docs` | Program application documents | Owner + Staff + Admin |
| `referral-letters` | Generated referral PDFs | Owner + Staff + Admin |
| `lmi-reports` | LMI PDF + Excel files | Staff + Admin |
| `qr-codes` | Job fair QR code images | Owner + Staff |
| `company-logos` | Employer company logos | Public read |
| `profile-photos` | Jobseeker profile photos | Public read |


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system — essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

**Property Reflection:** After prework analysis, the following redundancies were resolved:
- Properties 1.1 and 1.2 (account creation + OTP creation) are combined into one registration round-trip property.
- Properties 4.3 and 19.1/19.2 (file validation) are consolidated into one file validation property.
- Properties 7.1 and 7.4 (match score computation + ordering) are combined into one AI matching property.

---

### Property 1: OTP Registration Round-Trip

*For any* valid registration payload (email, password, role), calling register() should create a user in pending state with an associated unexpired OTP record, and calling verify_otp() with that OTP within the expiry window should activate the account.

**Validates: Requirements 1.1, 1.2**

---

### Property 2: OTP Expiry Rejection

*For any* OTP record whose `expires_at` timestamp is in the past, submitting that OTP to verify_otp() should return a rejection error and leave the account in its current state.

**Validates: Requirements 1.3**

---

### Property 3: OTP Single-Use Idempotence

*For any* OTP that has been successfully used once (used_at is set), submitting the same OTP again should be rejected, regardless of whether it is still within the expiry window.

**Validates: Requirements 1.4**

---

### Property 4: OTP Resend Invalidation

*For any* user with an existing OTP, calling resend_otp() should result in the previous OTP being invalid (rejected by verify_otp()) and a new valid OTP being issued with a fresh expiry.

**Validates: Requirements 1.5**

---

### Property 5: JWT Token Issuance Correctness

*For any* valid user credentials, calling login() should return a JWT access token whose decoded claims contain the correct user_id, role, and an expiry approximately 15 minutes from issuance, and set an httpOnly refresh token cookie.

**Validates: Requirements 2.1**

---

### Property 6: Logout Invalidates Refresh Token

*For any* logged-in user session, calling logout() followed by calling refresh() with the previously issued refresh token should return an authentication error.

**Validates: Requirements 2.5**

---

### Property 7: Password Hash Correctness

*For any* plaintext password string, hash_password() should produce a bcrypt hash that (a) verifies correctly with bcrypt.checkpw(), and (b) has a cost factor of 12 as encoded in the hash prefix.

**Validates: Requirements 2.6**

---

### Property 8: File Validation Rejects Invalid Inputs

*For any* file where either (a) the MIME type is not in {image/jpeg, image/png, application/pdf}, or (b) the file size in bytes exceeds 5 × 1024 × 1024, validate_file() should return (False, non-empty error string) and the file should not be stored.

**Validates: Requirements 4.3, 19.1, 19.2**

---

### Property 9: AI Match Score Range and Ordering

*For any* jobseeker profile and non-empty list of active vacancies, rank_vacancies() should return a list where (a) every match_score is a float in the closed interval [0.0, 1.0], and (b) the list is sorted in non-increasing order of match_score.

**Validates: Requirements 7.1, 7.4**

---

### Property 10: Login Brute-Force Blocking

*For any* IP address, after 5 consecutive failed login attempts within a 15-minute window, the 6th login attempt from that IP should return an HTTP 429 or 403 response regardless of credential validity.

**Validates: Requirements 2.3**

---

### Property 11: QR Token Uniqueness

*For any* set of N job fair registrations (N ≥ 2) for the same event, all generated QR tokens should be pairwise distinct — no two registrations share the same token.

**Validates: Requirements 10.1**

---

### Property 12: QR Attendance Round-Trip

*For any* valid job fair registration with a generated QR token, calling validate_scan() with that token and the correct event_id should return (True, participant_data), and an attendance record with a non-null scanned_at timestamp should be created.

**Validates: Requirements 10.3**

---

### Property 13: Invalid QR Rejection

*For any* token string that does not correspond to a registered participant for the given event_id, validate_scan() should return (False, error_message) and no attendance record should be created.

**Validates: Requirements 10.4**

---

### Property 14: Audit Trail Append on Significant Actions

*For any* significant action (login, logout, account creation, profile update, vacancy approval/rejection, application status change, program decision, report generation, settings change), the audit_trail table should contain exactly one new entry with non-null actor_id, actor_role, action_type, resource_type, ip_address, and created_at fields after the action completes.

**Validates: Requirements 17.1, 17.2**

---

### Property 15: API Response Shape Invariant

*For any* API endpoint in the JobBridge system, the JSON response body should always contain exactly the keys `success` (boolean), `data` (object or null), and `message` (string), regardless of whether the request succeeded or failed.

**Validates: Requirements 20.1, 20.2, 20.3**


## Error Handling

### Backend Error Handling Strategy

All Flask blueprints use a centralized error handler registered in the app factory:

```python
@app.errorhandler(Exception)
def handle_exception(e):
    # Log to audit trail if actor context available
    return jsonify({"success": False, "data": None, "message": str(e)}), status_code
```

**HTTP Status Code Conventions:**
| Scenario | Status Code |
|----------|-------------|
| Success | 200 / 201 |
| Validation error | 422 |
| Authentication failure | 401 |
| Authorization failure | 403 |
| Resource not found | 404 |
| Rate limit exceeded | 429 |
| Server error | 500 |

**Specific Error Scenarios:**
- OTP expired → 422 with message "OTP has expired. Please request a new one."
- OTP already used → 422 with message "OTP has already been used."
- File too large → 413 with message "File exceeds the 5MB size limit."
- Unsupported file type → 415 with message "Only JPG, PNG, and PDF files are accepted."
- JWT expired → 401 with message "Access token expired." (triggers frontend refresh)
- Role mismatch → 403 with message "Access denied for your role."
- Duplicate application → 409 with message "You have already applied for this vacancy."

### Frontend Error Handling Strategy

- Axios interceptor catches 401 responses and triggers token refresh automatically.
- Axios interceptor catches 403 responses and redirects to role dashboard.
- React Query `onError` callbacks display React Hot Toast notifications.
- Zod form validation provides inline field-level error messages before API calls.
- Socket.io `connect_error` event triggers a reconnection toast notification.

### OCR and AI Service Error Handling

- Google Vision API failures: return partial data with `ocr_confidence: 0`, allow manual entry.
- spaCy NLP failures: return raw text without structured extraction, log error.
- AI Matcher failures: return `match_score: null`, display vacancies without score sorting.
- Dialogflow ES timeout (>3s): return fallback message directing user to PESO Staff.


## Testing Strategy

### Dual Testing Approach

Both unit/example tests and property-based tests are used. Unit tests cover specific scenarios and integration points; property tests verify universal correctness across generated inputs.

### Property-Based Testing

**Library:** `hypothesis` (Python) for backend property tests.

Each property test runs a minimum of 100 iterations. Tests are tagged with the design property they validate.

**Configuration:**
```python
from hypothesis import given, settings, HealthCheck
from hypothesis import strategies as st

@settings(max_examples=100, suppress_health_check=[HealthCheck.too_slow])
@given(st.text(min_size=1), st.emails())
def test_property_N_description(password, email):
    # Feature: jobbridge-system, Property N: <property_text>
    ...
```

**Properties to implement as hypothesis tests:**
- Property 1: OTP Registration Round-Trip
- Property 2: OTP Expiry Rejection
- Property 3: OTP Single-Use Idempotence
- Property 4: OTP Resend Invalidation
- Property 5: JWT Token Issuance Correctness
- Property 6: Logout Invalidates Refresh Token
- Property 7: Password Hash Correctness
- Property 8: File Validation Rejects Invalid Inputs
- Property 9: AI Match Score Range and Ordering
- Property 10: Login Brute-Force Blocking
- Property 11: QR Token Uniqueness
- Property 12: QR Attendance Round-Trip
- Property 13: Invalid QR Rejection
- Property 14: Audit Trail Append on Significant Actions
- Property 15: API Response Shape Invariant

### Unit and Integration Tests

**Framework:** `pytest` with `pytest-flask` for backend; `vitest` + `@testing-library/react` for frontend.

**Backend unit test coverage targets:**
- Auth service: OTP generation, JWT issuance, bcrypt hashing
- AI Matcher: score computation, ranking
- OCR Processor: file validation, data extraction (mocked Vision API)
- QR Service: token generation, validation
- Notification Service: emit + email dispatch (mocked SMTP + SocketIO)
- Audit Service: entry creation, append-only enforcement

**Frontend unit test coverage targets:**
- ProtectedRoute: redirects unauthenticated users
- RoleGuard: blocks wrong-role access
- Zod schemas: form validation edge cases
- API hooks: loading/error/success states

**Integration tests:**
- Full registration → OTP → login flow
- Application submission → status update → notification delivery
- Job fair registration → QR generation → attendance scan
- LMI report generation → PDF/Excel creation → storage upload

### Test Database Strategy

- Use a separate Supabase project or local PostgreSQL instance for tests.
- Each test suite uses database transactions rolled back after each test.
- Celery tasks tested with `CELERY_TASK_ALWAYS_EAGER=True` in test config.

