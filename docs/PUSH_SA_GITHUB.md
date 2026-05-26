# Paano i-push ang PESOPILA sa GitHub mo

Repository: **https://github.com/jobbridgepeso-beep/PESOPILALAGUNA**

---

## Bakit hindi ako makapag-push?

Ang PC mo ay naka-login sa GitHub bilang **`WendellBlaze15`**, pero ang repo ay pag-aari ng account **`jobbridgepeso-beep`**. Kailangan mong mag-sign in gamit ang tamang account o gumamit ng **Personal Access Token (PAT)**.

---

## Hakbang 1: Ihanda ang Git (isang beses lang)

Buksan **PowerShell** sa folder ng project:

```powershell
cd c:\Users\UserAccount\Desktop\PESOPILA

git config user.name "JobBridge PESO Pila"
git config user.email "YOUR_EMAIL@example.com"
```

Palitan ang email ng email na naka-link sa GitHub account **`jobbridgepeso-beep`**.

---

## Hakbang 2: Gumawa ng Personal Access Token

### Option A — Classic token (recommended, mas simple)

1. Mag-login sa GitHub bilang **jobbridgepeso-beep**
2. Pumunta sa: https://github.com/settings/tokens
3. **Generate new token (classic)**
4. Lagyan ng pangalan, hal. `PESOPILA-push`
5. Piliin ang scope: **`repo`** (full control) — kailangan ito para makapag-**push**
6. I-generate at **kopyahin** ang token (makikita mo lang ito isang beses)

### Option B — Fine-grained token

Kung **Fine-grained** ang ginamit mo at 403 / "Permission denied" ang lumalabas:

1. https://github.com/settings/tokens?type=beta → **Generate new token**
2. **Repository access:** Only select repositories → piliin **`PESOPILALAGUNA`**
3. **Permissions → Repository permissions:**
   - **Contents:** Read and write
   - **Metadata:** Read-only (auto)
4. I-save at gamitin ang bagong token

> Ang token na walang **Contents: Write** ay hindi makakapag-push kahit tama ang account.

---

## Hakbang 3: I-push ang code

```powershell
cd c:\Users\UserAccount\Desktop\PESOPILA
git status
git push -u origin main
```

Kapag humingi ng credentials:

| Field | Ilagay |
|--------|--------|
| **Username** | `jobbridgepeso-beep` |
| **Password** | ang **token** (hindi ang GitHub password) |

---

## Alternatibo: Gamitin ang GitHub Desktop

1. I-download ang [GitHub Desktop](https://desktop.github.com/)
2. Sign in bilang **jobbridgepeso-beep**
3. **File → Add Local Repository** → piliin ang `c:\Users\UserAccount\Desktop\PESOPILA`
4. I-click ang **Publish repository** o **Push origin**

---

## Kung may bagong changes ka pa

```powershell
cd c:\Users\UserAccount\Desktop\PESOPILA
git add -A
git commit -m "Describe your changes here"
git push origin main
```

---

## Mahalaga: Huwag i-commit ang `.env`

Naka-`.gitignore` na ang `backend/.env` at `frontend/.env` para hindi ma-leak ang Supabase keys sa GitHub.

Kung kailangan ng team, kopyahin lang ang `.env.example` at lagyan ng sariling keys.

---

## Pagkatapos ma-push

Tingnan ang repo: https://github.com/jobbridgepeso-beep/PESOPILALAGUNA

Dapat makita mo ang `backend/`, `frontend/`, `README.md`, at iba pa.
