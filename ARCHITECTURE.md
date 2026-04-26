# Uncle Kerja — Architecture

## What it does

An agentic AI career assistant for Malaysian job seekers:
1. Parses a resume (PDF or text) into a structured profile
2. Scores it against a job description across 4 weighted dimensions
3. Roasts it with a sharp, specific critique (no sugar-coating)
4. Coaches the user with a ranked 6-week improvement plan
5. Finds real Malaysian job matches (Google Jobs + aidevboard)
6. Drafts cover letters in English and Bahasa Malaysia
7. Sends daily job alert emails via Gmail through AgentMail
8. **Reads email replies and responds autonomously** (Reply Agent)

---

## Tech Stack

| Layer | Choice | Notes |
|---|---|---|
| **LLM** |  Z.AI GLM-5.1 through ILMU |
| **LLM approach** | Native Gemini REST API (`?key=`) via `httpx` | OpenAI-compat endpoint returned 400 for this key; native works |
| **Web framework** | FastAPI + Uvicorn | Async, CORS, multipart file upload, SSE-ready |
| **PDF parsing** | `pdfplumber` + `pypdf` fallback | Handles image-heavy/complex Malaysian resume formats |
| **Database** | Supabase (PostgreSQL) | Persistent history, email log, alert subscriptions |
| **Auth** | Supabase auth + local JWT fallback | Dual-mode: Supabase for real accounts, local for offline demo |
| **Email sending** | AgentMail API (`usm.z.ai@agentmail.to`) | Gmail SMTP as fallback |
| **Email replies** | AgentMail inbox polling (APScheduler, 5 min) | Reply Agent processes inbound emails autonomously |
| **Job search** | SerpAPI Google Jobs → aidevboard → TheirStack | Three-layer: real-time → free AI/tech → credit-conserving fallback |
| **Scheduling** | APScheduler (in-process) | No Redis/Celery overhead |
| **Frontend** | React + Vite + Tailwind CSS v4 | 5 pages, dark theme, Supabase JS SDK for auth |

---

## System Diagram

```
User (browser)
    │
    │  Upload PDF + JD
    ▼
┌─────────────────────────────────────────┐
│         FastAPI Backend (:8000)         │
│                                         │
│  POST /analyze                          │
│         │                               │
│         ▼                               │
│  ┌─────────────┐                        │
│  │ Parser Agent│  PDF → ResumeProfile   │
│  └──────┬──────┘  (Gemini tool call)    │
│         │                               │
│         ▼                               │
│  ┌─────────────┐                        │
│  │ Scorer Agent│  Profile + JD          │
│  └──────┬──────┘  → ScoreReport         │
│         │                               │
│  ┌──────┴──────────────────┐            │
│  │                         │            │
│  ▼ (no LLM)                ▼            │
│  ┌──────────────┐   ┌─────────────┐    │
│  │  Job Finder  │   │Roaster Agent│    │
│  │SerpAPI+aidev │   │→ RoastReport│    │
│  └──────┬───────┘   └──────┬──────┘    │
│         │                  │            │
│         │           ┌──────▼──────┐    │
│         │           │ Coach Agent │    │
│         │           │ → ActionPlan│    │
│         │           └──────┬──────┘    │
│         │                  │            │
│  ┌──────▼──────────────────▼──────┐    │
│  │          Orchestrator           │    │
│  │  Merges session → saves to DB  │    │
│  └──────────────┬─────────────────┘    │
│                 │                       │
│     ┌───────────┴───────────┐           │
│     ▼                       ▼           │
│  ┌──────────┐      ┌───────────────┐   │
│  │  Email   │      │  Supabase DB  │   │
│  │  Agent   │      │  analyses     │   │
│  └────┬─────┘      │  job_alerts   │   │
│       │            │  sent_emails  │   │
│       ▼            └───────────────┘   │
│  AgentMail API                          │
│  usm.z.ai@agentmail.to                  │
│       │                                 │
│  APScheduler (every 5 min)              │
│       ▼                                 │
│  ┌─────────────┐                        │
│  │ Reply Agent │  ← inbound email reply │
│  │ Classifies  │    from any user       │
│  │ intent →    │                        │
│  │ LLM responds│                        │
│  │ → AgentMail │                        │
│  └─────────────┘                        │
└─────────────────────────────────────────┘
         │
         ▼
  Gmail (tomleeatwork@gmail.com)
  receives job alert emails
```

---

## Agent Descriptions

### 1. Parser Agent (`parser_agent.py`)
- **Input**: raw resume text (extracted from PDF or pasted)
- **Output**: `ResumeProfile` — name, email, phone, location, years_experience, current_role, skills[], experience[], education[], certifications[]
- **LLM call**: `tool_choice=extract_resume`

### 2. Scorer Agent (`scorer_agent.py`)
- **Input**: `ResumeProfile`, `job_description: str`
- **Output**: `ScoreReport` — overall_score (0-100), skills_score (40%), experience_score (35%), education_score (15%), keyword_score (10%), matched_skills[], missing_skills[], missing_keywords[], verdict, one_line_summary
- **LLM call**: `tool_choice=score_resume`

### 3. Roaster Agent (`roaster_agent.py`)
- **Input**: `ResumeProfile`, `ScoreReport`, `job_title: str`
- **Output**: `RoastReport` — opening_roast, skills_roast, experience_roast, formatting_roast, silver_lining, closing_line, emoji_rating
- **LLM call**: `tool_choice=roast_resume`, temperature=0.8

### 4. Coach Agent (`coach_agent.py`)
- **Input**: `ScoreReport`, `ResumeProfile`
- **Output**: `ActionPlan` — priority_actions[{rank, action, effort, impact, resources[]}], resume_rewrites[], quick_wins[], timeline_weeks
- **LLM call**: `tool_choice=build_action_plan`
- **Malaysian specifics**: recommends HRDF/HRD Corp claimable courses for skill gaps

### 5. Job Finder Agent (`job_finder_agent.py`)
- **Input**: `ResumeProfile`, `ScoreReport`
- **Output**: `{ local_jobs[5], remote_jobs[3] }` — all with real apply URLs
- **No LLM call** — pure API calls (faster, saves credits)
- **Sources**: SerpAPI Google Jobs (primary, `gl=my`) → aidevboard (AI/tech, free) → TheirStack (backup, max 3 credits)

### 6. Email Agent (`email_agent.py`)
- **Input A** (cover letter): `ResumeProfile`, `job: dict`
- **Output A**: `{ subject_en, body_en, subject_ms, body_ms }` — bilingual (EN + Bahasa Malaysia)
- **Input B** (job alert): `ResumeProfile`, `list[job]`
- **Output B**: HTML email body for the alert
- **LLM call**: `tool_choice=draft_cover_letter` (for cover letters only)

### 7. Reply Agent (`reply_agent.py`)
- **What it does**: Closes the agentic loop — users can control their job search entirely through email replies, without logging into the app
- **Trigger**: APScheduler polls AgentMail inbox every 5 minutes
- **Flow**:
  1. Reads unprocessed inbound messages at `usm.z.ai@agentmail.to`
  2. Classifies user intent via LLM (`tool_choice=classify_email_intent`):
     - `find_more_jobs` — re-runs Job Finder with stored profile
     - `change_location` — e.g. "find jobs in Penang"
     - `change_role` — e.g. "show me frontend jobs instead"
     - `question` — general career question, answered by LLM
     - `apply_help` — help applying for a specific job
     - `unsubscribe` — deactivates alert subscription in DB
  3. Generates a response and replies via AgentMail (same thread)
  4. Labels message as `processed` to avoid double-handling
- **Agentic significance**: This is the only fully autonomous agent — it runs without any user interaction, triggered by an external event (an email arrival)

---

## Database — Supabase PostgreSQL

### Schema

```sql
-- Every resume analysis run
analyses (
    id              TEXT PRIMARY KEY,      -- session UUID
    user_email      TEXT,                  -- who ran it
    created_at      TIMESTAMPTZ,
    job_title       TEXT,                  -- first line of JD
    overall_score   INTEGER,               -- 0-100
    verdict         TEXT,                  -- Strong Fit / Partial Fit / etc.
    summary         TEXT,                  -- one-line summary
    roast_opening   TEXT,                  -- shown on history card
    skills_matched  JSONB,                 -- ["Python", "Django", ...]
    jobs_count      INTEGER,
    errors          JSONB,
    score_json      JSONB,                 -- full ScoreReport
    profile_json    JSONB                  -- full ResumeProfile
)

-- Email alert subscriptions
job_alerts (
    user_email      TEXT PRIMARY KEY,
    is_active       BOOLEAN,
    subscribed_at   TIMESTAMPTZ,
    last_sent_at    TIMESTAMPTZ,
    last_session_id TEXT
)

-- Outbound email log (persists across server restarts)
sent_emails (
    id          UUID PRIMARY KEY,
    to_email    TEXT,
    subject     TEXT,
    sent_at     TIMESTAMPTZ,
    thread_id   TEXT,                      -- AgentMail thread
    message_id  TEXT,
    email_type  TEXT                       -- job_alert / welcome / cover_letter
)
```

### Access pattern
- Backend uses `SUPABASE_SERVICE_ROLE_KEY` — bypasses Row Level Security
- RLS is enabled on all tables (anon key cannot read raw data)
- Frontend auth uses `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` for login/signup only

---

## API Endpoints

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET  | `/health` | — | Service health, AgentMail status |
| POST | `/analyze` | optional | Upload resume + JD → full 7-agent pipeline → saves to DB |
| GET  | `/session/{id}` | — | In-memory session (live results, includes full data) |
| POST | `/cover-letter` | — | Generate bilingual cover letter for a matched job |
| POST | `/alerts/subscribe` | — | Subscribe email → sends welcome email immediately |
| DELETE | `/alerts/unsubscribe/{id}` | — | Deactivate alert subscription |
| GET  | `/history` | Bearer | User's past analyses from DB (admin sees all) |
| GET  | `/history/{id}/full` | — | Full persisted analysis with score + profile JSON |
| GET  | `/db/stats` | — | DB row counts (analyses, alerts, sent emails) |
| GET  | `/inbox/messages` | — | Recent AgentMail inbox messages |
| GET  | `/inbox/job-emails?email=` | — | Sent job alert emails for a specific address |
| POST | `/inbox/poll` | — | Manually trigger Reply Agent |
| POST | `/api/auth/login` | — | Login → returns JWT |
| POST | `/api/auth/signup` | — | Create Supabase account |
| GET  | `/api/auth/me` | Bearer | Validate token → return user |

---

## Auth & Roles

| Role | Account | Access |
|------|---------|--------|
| **admin** | `tomleeatwork@gmail.com` / `admin@demo.local` | All analyses, all inbox messages, DB stats, system health |
| **user** | `teamusm20@gmail.com` / `user@demo.local` | Own analyses only, own job alert emails |

Auth is dual-mode:
- **Supabase JWT** — for real accounts (email + password, no email confirmation required)
- **Local JWT** (`HS256`, `JWT_SECRET`) — for demo accounts, instant login, no network required

---

## Job Alert Flow (agentic workflow)

```
1. User subscribes with email → saved to job_alerts table
2. System immediately sends welcome email via AgentMail
3. Next morning (or on demand): Job Finder runs for subscriber profile
4. Email Agent builds HTML email → AgentMail sends from usm.z.ai@agentmail.to
5. Email logged to sent_emails table
6. User receives email in Gmail
7. User REPLIES to email (e.g. "find me React jobs in Penang")
8. Reply Agent (APScheduler, 5 min) detects inbound message
9. Intent classified → LLM generates response → AgentMail replies in same thread
10. Loop continues — entirely autonomous
```

---

## Frontend Pages

| Route | Page | Auth |
|-------|------|------|
| `/` | Landing — hero slider, 6 mascot agent cards, feature cubes | Public |
| `/login` | Sign in — demo account buttons | Public |
| `/analyse` | Resume upload + JD form + progress tracker | Public |
| `/results/:id` | Tabbed results — Score / Roast / Plan / Jobs | Public |
| `/history` | Past analyses from Supabase DB | Login required |
| `/alerts` | Job alert management + inbox view | Login required |
| `/admin` | System health, DB stats, inbox table, Reply Agent trigger | Admin only |

---

## Latency (Gemini 2.5 Flash Lite)

| Step | Time | Notes |
|------|------|-------|
| Parser | ~3s | Gemini is ~10x faster than GLM was |
| Scorer | ~3s | |
| Job Finder | ~2s | No LLM — SerpAPI + aidevboard |
| Roaster | ~3s | temperature=0.8 |
| Coach | ~4s | Longest — complex structured output |
| **Total** | **~15s** | Sequential to avoid API overload |

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `GEMINI_API_KEY` | Google AI Studio key (active LLM) |
| `ILMU_API_KEY` | ILMU GLM-5.1 key (commented out, overloaded) |
| `GMAIL_USER` | `tomleeatwork@gmail.com` — email sender |
| `GMAIL_APP_PASSWORD` | Gmail app password |
| `AGENTMAIL_API_KEY` | AgentMail API key |
| `AGENTMAIL_INBOX_ID` | `usm.z.ai@agentmail.to` |
| `NEXT_PUBLIC_SUPABASE_URL` | Supabase project URL |
| `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_DEFAULT_KEY` | Frontend auth (login/signup) |
| `SUPABASE_SERVICE_ROLE_KEY` | Backend DB operations (bypasses RLS) |
| `JWT_SECRET` | Signs local demo account tokens |
| `THEIRSTACK_API_KEY` | Job search fallback (1 credit/result, use sparingly) |
| `SERPAPI_KEY` | Google Jobs search (primary job source) |
