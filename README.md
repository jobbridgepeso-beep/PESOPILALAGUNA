# PESOPILA — JobBridge System

Intelligent chatbot and OCR-assisted job matching platform for **PESO Pila, Laguna**.

- **Frontend:** React 18 + Vite (`frontend/`)
- **Backend:** Python 3.11 + Flask (`backend/`)
- **Database:** [Supabase](https://dlexnkpbudtjwzobiumr.supabase.co) (PostgreSQL + Storage)

## Quick start

### 1. Supabase setup

1. Open [Supabase Dashboard](https://supabase.com/dashboard/project/dlexnkpbudtjwzobiumr) for project `dlexnkpbudtjwzobiumr`.
2. Copy `backend/.env.example` → `backend/.env` and set:
   - `SUPABASE_URL=https://dlexnkpbudtjwzobiumr.supabase.co`
   - `SUPABASE_KEY` (anon key)
   - `SUPABASE_SERVICE_KEY` (service role key)
   - `DATABASE_URL` (Session pooler connection string from **Settings → Database**)
3. Apply database migrations:

```bash
cd backend
pip install -r requirements.txt
python database/apply_migrations.py
python database/create_buckets.py
python seed.py
```

**Default admin login** (after `seed.py`):

- Email: `admin@jobbridge.ph`
- Password: `Admin@JobBridge2026` (change after first login)

### 2. Backend

```bash
cd backend
pip install -r requirements.txt
python wsgi.py
```

API runs at `http://localhost:5000`.

### 3. Frontend

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

App runs at `http://localhost:5173`.

Or start both with:

```powershell
.\scripts\start-dev.ps1
```

## Repository

- GitHub: [jobbridgepeso-beep/PESOPILALAGUNA](https://github.com/jobbridgepeso-beep/PESOPILALAGUNA)

## Specs

Implementation plan and requirements live in `.kiro/specs/jobbridge-system/`.

## Security

Do **not** commit `.env` files. Use `.env.example` as templates only.
