# Courier & Logistics Tracking System — Phase 1 (Core MVP)

## What's in Phase 1
- Project structure for a FastAPI + Jinja2 + Supabase app
- `profiles` and `packages` tables (SQL)
- Role-based login routing:
  - **Customer**: Phone number + 6-digit PIN
  - **Admin / Dispatcher**: Email + Password (via Supabase Auth)
  - **Rider**: Phone + PIN (same mechanism as Customer, different role)
- A basic endpoint for Admin/Dispatcher to add a new package
- Customer dashboard showing packages linked to their phone number
- Staff dashboard with a form to add a package

**Not included yet** (Phase 2/3, as agreed): GPS simulation, in-app OTP delivery proof, COD wallet, bulk upload, email automation.

## Architecture note (important)
Unlike a pure frontend-only app, here the **browser never talks to Supabase directly**. FastAPI is the only thing that holds the Supabase **service role key** (kept server-side, in `.env`, never sent to the browser). This is what lets us safely store PIN hashes and control exactly who sees what — the browser only ever talks to our own FastAPI routes, which decide what to return based on the logged-in session.

## 1. Supabase setup
1. Create a Supabase project.
2. Open **SQL Editor** and run `sql/schema.sql`.
3. Go to **Project Settings → API** and copy:
   - Project URL
   - **service_role** key (NOT the anon key — this backend needs full access since it enforces access control itself, in code)
4. For Admin/Dispatcher accounts, go to **Authentication → Users → Add user** and create their email/password logins. Then insert a matching row in `profiles` (see `sql/schema.sql` comments) linking `auth_user_id` to that user and setting their `role`.

## 2. Local setup
```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill in your real values
uvicorn app.main:app --reload
```
Visit `http://127.0.0.1:8000`

## 3. Deploying (Render / Railway)
- Push this folder to a GitHub repo
- Create a new Web Service on Render/Railway pointing at the repo
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Add the same environment variables from `.env` in the host's dashboard (never commit `.env` itself)

## Phase 1 simplification — Customer/Rider PINs
There's no signup screen yet and no email automation yet, so for Phase 1: when a Dispatcher adds a package for a phone number that doesn't exist in `profiles`, the system auto-creates a Customer profile with a randomly generated 6-digit PIN, and **returns it in the dispatcher's response** so it can be relayed manually (by call/SMS) for now. Phase 3 (email automation) will replace this with an automatic email.

## Folder structure
```
courier-system/
├── app/
│   ├── main.py            # FastAPI app, mounts routers & static files
│   ├── config.py          # loads environment variables
│   ├── database.py        # Supabase client (service role)
│   ├── security.py        # PIN hashing + session helpers
│   ├── schemas.py         # Pydantic request/response models
│   ├── routers/
│   │   ├── pages.py       # HTML page routes (index, dashboards)
│   │   ├── auth.py        # login/logout routes (customer, staff, rider)
│   │   └── packages.py    # package creation/listing API routes
│   ├── templates/         # Jinja2 HTML templates
│   └── static/css/        # stylesheet
├── sql/schema.sql
├── requirements.txt
└── .env.example
```
