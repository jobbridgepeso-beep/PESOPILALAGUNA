# Deployment Guide — JobBridge / PESOPILA

Hybrid topology used here:

```
Browser ──► Vercel (React frontend) ──HTTPS──► Render (Flask backend) ──► Supabase (PostgreSQL + Storage)
```

Both Vercel and Render have free tiers. Total monthly cost: **$0**.

---

## 1. Prerequisites

- GitHub account with this repo pushed (already done).
- Free accounts on:
  - <https://vercel.com> (sign in with GitHub)
  - <https://render.com> (sign in with GitHub)
- Supabase project (already configured — keys are in `backend/.env`).

---

## 2. Deploy backend to Render

### 2.1 Create the service

1. Go to <https://dashboard.render.com/blueprints>.
2. Click **New Blueprint Instance**.
3. Connect the GitHub repo `jobbridgepeso-beep/PESOPILALAGUNA`.
4. Render auto-detects `backend/render.yaml` and shows the
   `jobbridge-backend` service.
5. Click **Apply**.

### 2.2 Add the secret env vars

Open the service → **Environment** tab → add each of these
(get the values from your local `backend/.env`):

| Key | Value source |
| --- | --- |
| `SECRET_KEY` | any long random string |
| `JWT_SECRET_KEY` | any long random string (different from above) |
| `SUPABASE_URL` | `https://dlexnkpbudtjwzobiumr.supabase.co` |
| `SUPABASE_KEY` | Supabase **anon** key |
| `SUPABASE_SERVICE_KEY` | Supabase **service-role** key |
| `DATABASE_URL` | Supabase pooler URI |
| `MAIL_USERNAME` | `jobbridgepeso@gmail.com` |
| `MAIL_PASSWORD` | Gmail **App Password** (rotate before deploying!) |
| `CORS_ORIGINS` | Leave blank for now — set after step 3 |
| `DIALOGFLOW_PROJECT_ID` | optional |

Click **Save Changes**. Render rebuilds automatically.

### 2.3 Verify

Once status is **Live**, open the service URL (e.g.
`https://jobbridge-backend.onrender.com`) and hit:

```
GET https://jobbridge-backend.onrender.com/api/health
```

You should get:

```json
{ "success": true, "data": { "status": "ok" }, "message": "JobBridge API is running." }
```

**Important:** copy this URL — we need it for Vercel in the next step.

---

## 3. Deploy frontend to Vercel

### 3.1 Import the repo

1. Go to <https://vercel.com/new>.
2. Click **Import Git Repository** → pick `PESOPILALAGUNA`.
3. **Root Directory** → click **Edit** → select `frontend`.
4. Framework Preset: **Vite** (auto-detected).
5. Build/Output already configured via `frontend/vercel.json`.

### 3.2 Set environment variables

In the import screen, expand **Environment Variables** and add:

| Key | Value |
| --- | --- |
| `VITE_API_BASE_URL` | `https://jobbridge-backend.onrender.com` |
| `VITE_SOCKET_URL` | `https://jobbridge-backend.onrender.com` |
| `VITE_SUPABASE_URL` | `https://dlexnkpbudtjwzobiumr.supabase.co` |
| `VITE_SUPABASE_ANON_KEY` | Supabase anon key |

Click **Deploy**. First build takes 2–3 minutes.

### 3.3 Note the production URL

After deploy, Vercel gives you a URL like `https://pesopila.vercel.app`.
Copy it.

---

## 4. Wire frontend → backend (CORS)

1. Open the Render dashboard → `jobbridge-backend` → **Environment**.
2. Edit `CORS_ORIGINS` and set it to your Vercel URL:

   ```
   https://pesopila.vercel.app,https://pesopila-git-main-yourname.vercel.app
   ```

   (Include both production and preview URLs if you want preview
   deploys to work. Comma-separated, no spaces.)

3. Click **Save Changes**. Render restarts in ~30 seconds.

---

## 5. Smoke test

1. Open `https://pesopila.vercel.app`.
2. Try registering a new account.
3. Check OTP email arrives.
4. Verify OTP, log in.
5. DevTools → Network → confirm requests go to the Render URL and
   return `200`.

---

## 6. Known free-tier quirks

| Tier | Quirk | Workaround |
| --- | --- | --- |
| Render free | Auto-sleeps after 15 min idle; first request takes ~30 s to wake | Upgrade to Starter ($7/mo) or hit `/api/health` from a cron (uptimerobot.com) |
| Render free | 512 MB RAM | spaCy lazy-loads, sklearn ~50 MB — fits |
| Vercel free | 100 GB bandwidth/month | More than enough for PESO use |
| Vercel free | Build minutes: 6000/mo | Plenty |

---

## 7. Custom domain (optional)

### Frontend (Vercel)

1. Vercel → Project → **Settings → Domains** → Add your domain.
2. Update DNS A/CNAME as instructed.
3. SSL auto-issues via Let's Encrypt.

### Backend (Render)

1. Render → service → **Settings → Custom Domains** → add e.g.
   `api.yourdomain.gov.ph`.
2. Update DNS CNAME.
3. Update `VITE_API_BASE_URL` and `VITE_SOCKET_URL` on Vercel.

---

## 8. Updating after first deploy

Push to `main`:

```powershell
git add .
git commit -m "Your change"
git push origin main
```

- **Vercel** redeploys automatically.
- **Render** redeploys automatically (because `autoDeploy: true` in
  `render.yaml`).

That's it.
