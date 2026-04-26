# Uncle Kerja — AI Career Intelligence for Malaysia

# Deliverables Link
https://drive.google.com/drive/folders/18KONGjWuFz-Bp08mt0AzZx7__I3CyTBy?usp=sharing

> Built at UMhack · Powered by **Z AI GLM-5.1**

Uncle Kerja is a multi-agent AI platform that analyses your resume against a Malaysian job description, gives you a calibrated score, roasts your resume honestly, builds a personalised 6-week improvement plan, finds real live job matches, and keeps you updated with daily email alerts — all in under 90 seconds.

---

## What It Does

Upload a resume (PDF or text) and paste a job description. Seven AI agents run sequentially and hand off results to each other:

| # | Agent | What it produces |
|---|-------|-----------------|
| 1 | **Parser Agent** | Structured profile — name, skills, experience, education, certifications |
| 2 | **Scorer Agent** | Score 0–100 across Skills (40%), Experience (35%), Education (15%), ATS Keywords (10%) |
| 3 | **Roaster Agent** | Sharp, specific critique — no sugar-coating. Malaysian recruiter energy. |
| 4 | **Coach Agent** | Ranked 6-week action plan with HRDF-claimable courses and resume rewrites |
| 5 | **Job Finder** | Live Malaysian job matches via Google Jobs + aidevboard (no LLM — pure API) |
| 6 | **Email Agent** | Bilingual cover letters (English + Bahasa Malaysia) + daily job alert emails |
| 7 | **Reply Agent** | Reads email replies autonomously — users control their job search via email |

---

## Architecture

```
Browser (React + Vite)
        │
        │  POST /analyze  (PDF + Job Description)
        ▼
┌────────────────────────────────────────────┐
│           FastAPI Backend (:8000)          │
│                                            │
│  Parser → Scorer → Job Finder             │
│                   → Roaster → Coach        │
│                                            │
│  Orchestrator merges session → Supabase DB │
│                                            │
│  Email Agent → AgentMail (usm.z.ai@...)   │
│                                            │
│  APScheduler (5 min)                       │
│    └─ Reply Agent ← inbound email replies  │
└────────────────────────────────────────────┘
        │
        ▼
  AgentMail  usm.z.ai@agentmail.to
  Supabase   PostgreSQL (analyses, alerts, sent_emails)
```

**LLM:** Z AI GLM-5.1 via `https://api.ilmu.ai/anthropic`  
**Database:** Supabase (PostgreSQL) — persistent history, alert subscriptions, email log  
**Auth:** Dual-mode — Supabase JWT for real accounts, local HS256 JWT for offline demo  
**Job search:** SerpAPI Google Jobs → aidevboard (free) → TheirStack (fallback)  
**Email:** AgentMail bidirectional inbox — sends alerts, reads replies autonomously  

---

## Pages

| Route | Description | Auth |
|-------|-------------|------|
| `/` | Landing — agent showcase, feature cubes, recent alerts | Public |
| `/login` | Sign in with demo accounts or Supabase credentials | Public |
| `/analyse` | Resume upload + job description form | Public |
| `/results/:id` | Tabbed results — Score / Roast / Action Plan / Jobs | Public |
| `/history` | Past analyses from database | Login required |
| `/alerts` | Job alert subscription + inbox of alerts sent to you | Login required |
| `/admin` | System health, AgentMail inbox, DB stats, Reply Agent trigger | Admin only |

---

## Demo Accounts

| Role | Email | Password | Access |
|------|-------|----------|--------|
| Admin | `tomleeatwork+Admin@gmail.com` | `Admin@1234` | All sessions, AgentMail inbox, system health |
| User | `teamusm20+user@gmail.com` | `User@1234` | Own analyses, own job alert emails |
| Demo Admin (offline) | `admin@demo.local` | `Admin@1234` | Same as admin, no network needed |
| Demo User (offline) | `user@demo.local` | `User@1234` | Same as user, no network needed |

---

## Running Locally

### Prerequisites

- Python 3.11+
- Node.js 18+
- A `.env` file in the project root (see below)

### 1 — Clone and install dependencies

```bash
# Backend
cd backend
pip install -r ../requirements.txt

# Frontend
cd ../frontend
npm install
```

### 2 — Configure environment variables

Create `.env` in the project root (`career-copilot-my/.env`):

```env
# Z AI GLM-5.1 (via ILMU API)
ILMU_API_KEY=your_ilmu_api_key

# AgentMail — bidirectional email inbox
AGENTMAIL_API_KEY=your_agentmail_key
AGENTMAIL_INBOX_ID=usm.z.ai@agentmail.to

# Gmail SMTP — fallback sender
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Supabase
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY=sb_publishable_...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Auth
JWT_SECRET=your-secret-key

# Job search
SERPAPI_KEY=your_serpapi_key
THEIRSTACK_API_KEY=your_theirstack_jwt
```

### 3 — Set up the Supabase database

Run `supabase_migration.sql` once in your Supabase Dashboard → SQL Editor. This creates the three tables (`analyses`, `job_alerts`, `sent_emails`).

### 4 — Start the backend

```bash
cd backend
uvicorn api.main:app --port 8000 --reload
```

You should see:
```
Uncle Kerja ready. AgentMail: usm.z.ai@agentmail.to
```

### 5 — Start the frontend (development)

```bash
cd frontend
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 6 — (Optional) Build for production

```bash
cd frontend
npm run build
# FastAPI will serve the built app from /frontend/dist
# Just run the backend — no separate frontend server needed
uvicorn api.main:app --port 8000
```

---

## How the Email Alert Loop Works

```
1.  User subscribes on /alerts with their email
2.  System sends a welcome email from usm.z.ai@agentmail.to immediately
3.  Daily job alerts are emailed with live Malaysian job matches
4.  User replies to the email to control their search:
      "find me React jobs in Penang"  → Job Finder re-runs for Penang
      "show me data science roles"    → role changed, new search
      "unsubscribe"                   → subscription deactivated in DB
5.  Reply Agent (runs every 5 min via APScheduler) reads inbound replies,
    classifies intent via GLM-5.1, and responds in the same email thread
6.  Entirely autonomous — no app login required after initial subscription
```

---

## Malaysian-Specific Features

- **HRDF / HRD Corp courses** — Coach Agent recommends claimable training for skill gaps
- **EPF & SOCSO awareness** — job descriptions assessed for registration status
- **Malaysian job hubs** — specialised search for KL, PJ, Cyberjaya, Penang, JB
- **Local university recognition** — UM, UTM, UiTM, MMU, UTAR and others scored accurately
- **Bilingual cover letters** — English + Bahasa Malaysia (Surat Permohonan Pekerjaan format)
- **MYR salary benchmarks** — all salary data in Ringgit Malaysia

---

## Agent Pipeline (Sequential by Design)

Agents run one after another to avoid overloading the GLM-5.1 endpoint. Each agent waits for the previous result before starting.

```
Parser (~30s) → Scorer (~12s) → Job Finder (instant) → Roaster (~15s) → Coach (~25s)
                                                         Total: ~90 seconds
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Z AI GLM-5.1 |
| Backend | FastAPI + Uvicorn (Python) |
| Frontend | React + Vite + Tailwind CSS v4 |
| Database | Supabase (PostgreSQL) |
| Auth | Supabase auth + local JWT |
| PDF parsing | pdfplumber + pypdf fallback |
| Email | AgentMail API (bidirectional) |
| Job search | SerpAPI + aidevboard + TheirStack |
| Scheduling | APScheduler (in-process, no Redis) |

---

*Uncle Kerja — Because your career deserves an uncle who tells it like it is.*
