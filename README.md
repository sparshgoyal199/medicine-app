# Regrowth OS — README

## What This App Does
A web-based habit tracker for Man Matters hair regrowth treatment (Minoxidil 5% + Finasteride 0.1%).
Helps users stay consistent during the critical first 90 days when drop-off is highest.

## Features
- ✅ User login / registration with JWT auth
- 📊 Biological phase timeline (Adaptation → Shedding → Growth → Densification)
- 💊 Daily 1-tap check-in (Morning + Night) with streak counter & badges
- 💧 Virtual medicine bottle tracker (depletes with each dose, refill reminder)
- 📸 Progress photo upload + before/after comparison slider
- 🤖 "Is This Normal?" AI symptom checker (Mistral AI)
- 📧 Email reminders via Gmail SMTP

## Tech Stack
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Backend**: FastAPI (Python)
- **Database**: Supabase (PostgreSQL)
- **AI**: Mistral AI API
- **Email**: Gmail SMTP

## Project Structure
```
medicine_app/
├── database_schema.sql          ← Run this in Supabase SQL Editor FIRST
├── frontend/
│   ├── index.html               ← Login / Register page
│   ├── css/styles.css
│   ├── js/
│   │   ├── config.js            ← API helpers, auth guard, utilities
│   │   └── auth.js
│   └── pages/
│       ├── dashboard.html       ← Main dashboard
│       ├── photos.html          ← Progress photo comparison
│       ├── symptoms.html        ← "Is This Normal?" AI helper
│       └── milestones.html      ← Badges & treatment milestones
└── backend/
    ├── main.py                  ← FastAPI app entry point
    ├── requirements.txt
    ├── .env                     ← Your API keys (copy from .env.example)
    ├── routers/                 ← API endpoints
    ├── models/schemas.py
    └── utils/                   ← Supabase, Mistral AI, email helpers
```

## Setup Instructions

### Step 1: Set Up Supabase Database
1. Go to https://supabase.com → Create project
2. Go to SQL Editor → New Query
3. Copy contents of `database_schema.sql` → Run it
4. Go to Storage → Create bucket named `progress-photos` (set to public)

### Step 2: Configure Environment Variables
Copy `backend/.env.example` to `backend/.env` and fill in your keys:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
MISTRAL_API_KEY=your_mistral_api_key
JWT_SECRET=any_random_secret_string
SMTP_EMAIL=your@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

### Step 3: Start the Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
Backend runs at: http://localhost:8000
API Docs at: http://localhost:8000/docs

### Step 4: Open the Frontend
Open `frontend/index.html` in your browser.
(Or serve it with: `python -m http.server 3000` from the `frontend/` folder)

## Email reminders (Gmail)
Scheduled reminders are **not** automatic until you add a simple Windows Task Scheduler job (or cron on Linux):

1. Set `CRON_SECRET` in `backend/.env`
2. Twice daily, call:
   - `POST http://localhost:8000/notifications/run-daily` with header `X-Cron-Secret: your_secret`
   - Optional weekly: `POST http://localhost:8000/notifications/refill-check` with the same header
3. Test once while logged in: `POST http://localhost:8000/notifications/test-reminder` (Bearer token) from http://localhost:8000/docs

## Gmail Setup (for email notifications)
1. Enable 2-Factor Authentication on your Gmail
2. Go to Google Account → Security → App Passwords
3. Create an App Password for "Mail"
4. Use that 16-character password as `SMTP_PASSWORD` in `.env`

## API Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| /auth/register | POST | Create account |
| /auth/login | POST | Login |
| /auth/me | GET | Get profile |
| /checkin/ | POST | Log a dose |
| /checkin/today | GET | Today's status |
| /checkin/streak | GET | Streak info |
| /timeline/phase | GET | Current phase |
| /timeline/milestones | GET | All milestones |
| /photos/upload | POST | Upload photo |
| /photos/ | GET | Get all photos |
| /photos/compare | GET | Compare first vs latest |
| /symptoms/check | POST | AI symptom check |
| /medicine/inventory | GET | Bottle level |
| /medicine/refill | POST | Reset bottle |
