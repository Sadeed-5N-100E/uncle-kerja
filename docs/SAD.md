# SYSTEM ANALYSIS DOCUMENTATION (SAD)
## UMHackathon 2026

**Project Name:** Uncle Kerja
**Version:** 1.0
**Team:** [FILL IN — Team Name]
**Date:** 25 April 2026

---

## 1. Introduction

### 1.1 Purpose
This System Analysis Document (SAD) describes the technical scope, architectural decisions, and design rationale behind Uncle Kerja — an AI-powered career intelligence platform built for Malaysian job seekers.

The key elements covered in this document are:

1. **Architecture** — A monolithic Python FastAPI server hosting a sequential 7-agent pipeline, with a React + Vite frontend and Supabase (PostgreSQL) for persistence.
2. **Data Flows** — How a resume and job description travel through 7 agents, are merged by the orchestrator, persisted to Supabase, and initiate an autonomous email alert lifecycle.
3. **GLM Integration** — How Z AI GLM-5.1 is integrated as a structured tool-call service layer across 6 of the 7 agents.
4. **Role of Reference** — This document serves as the reference for developers and testers to understand the end-to-end architecture, API contracts, and data schema.

### 1.2 Background
Prior to Uncle Kerja, Malaysian job seekers had no accessible, affordable tool that gave calibrated, role-specific feedback on their resumes. Existing tools (Jobstreet, LinkedIn, VMock) are either generic, expensive, or not Malaysia-aware. Uncle Kerja was conceived as a 30-hour hackathon project at UMHackathon 2026 to address this gap.

**Previous state:** No prior version existed. This is a greenfield build.

**New capabilities introduced:**
- Sequential multi-agent pipeline with structured GLM-5.1 tool-call outputs
- Bidirectional email agent (send + read + autonomously reply)
- Malaysia-specific context: HRDF courses, Malaysian job hubs, bilingual cover letters, local university recognition

### 1.3 Target Stakeholders

| Stakeholder | Role | Expectations |
|-------------|------|--------------|
| Job Seeker (User) | Uploads resume, receives analysis, subscribes to alerts, replies via email | Fast, honest, specific feedback; live job matches; low friction email control |
| Admin (Tom Lee) | Monitors platform health, views full AgentMail inbox, manages system | System visibility, inbox monitoring, ability to manually trigger reply agent |
| Reply Agent (Autonomous) | Reads inbound email replies, classifies intent, responds in thread | No human intervention required; operates on 5-minute polling cycle |
| Development Team | Built and maintains the platform | Modular agent files, clear API contracts, documented schema |
| QA Team | Validates agent outputs, API responses, and email flows | Defined input/output schemas per agent, testable endpoints, observable error states |

---

## 2. System Architecture & Design

### 2.1 High Level Architecture

#### 2.1.1 Overview

| Type | Details |
|------|---------|
| System | Web Application (Browser-based, responsive) |
| Architecture | Monolith FastAPI backend + React SPA frontend + Supabase (PostgreSQL) + AgentMail (external) |

Uncle Kerja is a client-server application. The React frontend (Vite, port 3000 in development) communicates with the FastAPI backend (Uvicorn, port 8000) via REST API calls proxied through Vite's dev server. In production, FastAPI serves the built React `dist/` folder as a static SPA.

The backend hosts the full 7-agent pipeline in-process. Agents run sequentially in the Orchestrator. Z AI GLM-5.1 is called over HTTPS via the ILMU API (`https://api.ilmu.ai/anthropic`) using an Anthropic-compatible messages endpoint. Supabase provides the PostgreSQL database accessed via the `supabase-py` client. AgentMail provides the bidirectional email inbox at `usm.z.ai@agentmail.to`.

#### 2.1.2 GLM-5.1 as Service Layer

GLM-5.1 is not a generic "AI module" — it is the reasoning core of 6 discrete agents, each with its own system prompt and enforced JSON schema via `tool_choice`. The `llm_client.py` module wraps all GLM calls with a single retry on HTTP 504.

**How prompts are constructed:**
Each agent builds a prompt from two parts:
1. A **system prompt** that defines the agent's identity, responsibility, and output constraints (e.g., "You are a resume scorer. Score the candidate only against the job description provided.")
2. A **user message** that contains the structured input (resume text, profile JSON, score JSON, etc.)

The `tool_choice` parameter forces GLM to respond exclusively in the defined schema. No free-text output is accepted.

**What goes into the context window (per agent):**

| Agent | Context Window Contents |
|-------|------------------------|
| Parser | System prompt (~300 tokens) + raw resume text (~2,500 tokens) |
| Scorer | System prompt (~300 tokens) + ResumeProfile JSON (~400 tokens) + Job description (~1,000 tokens) |
| Roaster | System prompt (~300 tokens) + ResumeProfile JSON (~400 tokens) + ScoreReport JSON (~300 tokens) + job title |
| Coach | System prompt (~300 tokens) + ScoreReport JSON (~300 tokens) + ResumeProfile JSON (~400 tokens) |
| Email Agent (cover letter) | System prompt (~300 tokens) + ResumeProfile JSON (~400 tokens) + job dict (~300 tokens) |
| Reply Agent (classify) | System prompt (~200 tokens) + inbound email body (~300 tokens) |

**How responses are parsed:**
GLM returns a `tool_calls` array. The `llm_client.py` extracts `tool_calls[0].function.arguments`, parses it as JSON, and returns the dict to the calling agent. Each agent validates required fields before handing off to the orchestrator.

**Token limits and enforcement:**
- Resume text is passed as-is up to ~3,000 words. There is no hard truncation gate — if the text overflows GLM's context, GLM truncates internally and returns a partial profile.
- Job description is passed as-is. Oversized JDs result in scoring against the visible portion of the JD.
- Email replies in the Reply Agent are truncated at 500 words before the classification call.

#### 2.1.3 Dependency Diagram

```
┌──────────────────────────────────────────────────────────────────┐
│                     Browser (React + Vite)                       │
│  /login  /analyse  /results/:id  /history  /alerts  /admin       │
└──────────────────────┬───────────────────────────────────────────┘
                       │  REST API  (proxied via Vite → :8000 in dev)
                       ▼
┌──────────────────────────────────────────────────────────────────┐
│                 FastAPI Backend (:8000)                           │
│                                                                  │
│  POST /analyze                                                   │
│    │                                                             │
│    ├─▶ [1] Parser Agent ──────────────────────────────────────┐  │
│    │       │  tool_choice=extract_resume                       │  │
│    │       ▼                                                   │  │
│    ├─▶ [2] Scorer Agent ─────────────────────────────────────┐│  │
│    │       │  tool_choice=score_resume                        ││  │
│    │       ▼                                                  ││  │
│    ├─▶ [3] Job Finder ◄─── SerpAPI / aidevboard / TheirStack ││  │
│    │       │  (no LLM call)                                   ││  │
│    │       │                                                  ││  │
│    ├─▶ [4] Roaster Agent ────────────────────────────────────┘│  │
│    │       │  tool_choice=roast_resume                         │  │
│    │       ▼                                                   │  │
│    └─▶ [5] Coach Agent ─────────────────────────────────────┘  │
│            │  tool_choice=build_action_plan                      │
│            ▼                                                     │
│       Orchestrator ──────────────────────▶ Supabase             │
│         merges session                    PostgreSQL             │
│            │                              (analyses,             │
│            ▼                               job_alerts,           │
│       [6] Email Agent                      sent_emails)          │
│            │  AgentMail API                                      │
│            ▼                                                     │
│       usm.z.ai@agentmail.to                                     │
│            │                                                     │
│   APScheduler (every 5 min)                                     │
│            ▼                                                     │
│       [7] Reply Agent                                            │
│            │  reads inbound replies                              │
│            │  tool_choice=classify_email_intent                  │
│            │  GLM generates response                             │
│            └─▶ AgentMail reply (same thread)                     │
│                                                                  │
│  All GLM calls ──────────────────────▶ ILMU API                 │
│                                         https://api.ilmu.ai/     │
│                                         anthropic                │
│                                         model: Z AI GLM-5.1      │
└──────────────────────────────────────────────────────────────────┘
```

#### 2.1.4 Sequence Diagram — Core Analysis Flow

```
User          Browser          FastAPI          GLM-5.1         Supabase      AgentMail
  │               │                │                │                │              │
  │ Upload PDF+JD │                │                │                │              │
  │──────────────▶│                │                │                │              │
  │               │ POST /analyze  │                │                │              │
  │               │───────────────▶│                │                │              │
  │               │                │ [Parser]       │                │              │
  │               │                │ tool_choice=   │                │              │
  │               │                │ extract_resume │                │              │
  │               │                │───────────────▶│                │              │
  │               │                │ ResumeProfile  │                │              │
  │               │                │◀───────────────│                │              │
  │               │                │ [Scorer]       │                │              │
  │               │                │ tool_choice=   │                │              │
  │               │                │ score_resume   │                │              │
  │               │                │───────────────▶│                │              │
  │               │                │ ScoreReport    │                │              │
  │               │                │◀───────────────│                │              │
  │               │                │ [Job Finder]   │                │              │
  │               │                │ SerpAPI call ──────────────────────────────── │
  │               │                │ jobs[]         │                │              │
  │               │                │ [Roaster]      │                │              │
  │               │                │ tool_choice=   │                │              │
  │               │                │ roast_resume   │                │              │
  │               │                │───────────────▶│                │              │
  │               │                │ RoastReport    │                │              │
  │               │                │◀───────────────│                │              │
  │               │                │ [Coach]        │                │              │
  │               │                │ tool_choice=   │                │              │
  │               │                │ build_action_  │                │              │
  │               │                │ plan           │                │              │
  │               │                │───────────────▶│                │              │
  │               │                │ ActionPlan     │                │              │
  │               │                │◀───────────────│                │              │
  │               │                │ save_analysis()│                │              │
  │               │                │───────────────────────────────▶│              │
  │               │                │ send alert     │                │              │
  │               │                │────────────────────────────────────────────── │
  │               │ session JSON   │                │                │              │
  │               │◀───────────────│                │                │              │
  │ /results/:id  │                │                │                │              │
  │◀──────────────│                │                │                │              │
```

### 2.2 Technology Stack

#### 2.2.1 Frontend
**React 18 + Vite + Tailwind CSS v4**
- React chosen for component-based UI with fast re-renders — tab switching on results, real-time progress bar, cover letter modal all benefit from reactive state.
- Vite provides instant HMR and a built-in proxy to forward `/api`, `/analyze`, `/history`, etc. to the FastAPI backend during development.
- Tailwind CSS v4 for utility-first styling with no build-time overhead.

#### 2.2.2 Backend
**Python 3.11 + FastAPI + Uvicorn**
- FastAPI chosen for async support, automatic OpenAPI docs, and clean dependency injection. Multipart form upload (`UploadFile`) handles PDF resumes natively.
- Uvicorn provides ASGI server with reload support in development.
- APScheduler runs the 5-minute Reply Agent polling loop in-process — no Redis or Celery needed for this scale.

#### 2.2.3 Database
**Supabase (PostgreSQL)**
- Three tables: `analyses`, `job_alerts`, `sent_emails`.
- Backend uses the Supabase service role key — bypasses Row Level Security for all backend operations.
- Frontend uses the publishable key only for auth (login/signup) — never touches raw data directly.

#### 2.2.4 AI / LLM
**Z AI GLM-5.1 via ILMU API**
- Anthropic-compatible messages endpoint: `https://api.ilmu.ai/anthropic`
- Tool-call structured output enforced per agent.
- Single retry on HTTP 504.

#### 2.2.5 Email
**AgentMail** (`usm.z.ai@agentmail.to`)
- Bidirectional: can send alerts AND read inbound replies.
- Gmail SMTP (`tomleeatwork@gmail.com`) as fallback sender if AgentMail fails.

#### 2.2.6 Job Search APIs
- **SerpAPI** — Google Jobs (primary, `gl=my` filter for Malaysia)
- **aidevboard** — free AI/tech job board (fallback)
- **TheirStack** — company tech stack job search (backup, max 3 credits per call)

#### 2.2.7 Auth
- **Supabase Auth** — email + password, JWT returned by Supabase and stored in `localStorage`
- **Local JWT** — HS256 signed with `JWT_SECRET`, used for demo accounts (`admin@demo.local`, `user@demo.local`) — works offline with no Supabase dependency

---

### 2.3 Key Data Flows

#### 2.3.1 Data Flow — Resume Analysis

```
[User] ──PDF+JD──▶ [POST /analyze]
                         │
                   pdfplumber extracts text
                         │
                   Parser Agent ──▶ GLM-5.1 ──▶ ResumeProfile JSON
                         │
                   Scorer Agent ──▶ GLM-5.1 ──▶ ScoreReport JSON
                         │
                 ┌────────────────┐
                 ▼                ▼
           Job Finder        Roaster Agent ──▶ GLM-5.1 ──▶ RoastReport JSON
           SerpAPI call            │
           jobs[] returned    Coach Agent ──▶ GLM-5.1 ──▶ ActionPlan JSON
                 │                 │
                 └────────┬────────┘
                          ▼
                    Orchestrator merges:
                    {session_id, profile, score, roast,
                     action_plan, jobs, errors, created_at}
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
           Supabase DB         In-memory
           (analyses table)    session cache
                          │
                    Email Agent ──▶ AgentMail ──▶ usm.z.ai@agentmail.to
                          │          (send alert)
                    log_sent_email ──▶ Supabase sent_emails table
```

#### 2.3.2 Data Flow — Email Reply Loop

```
[User Gmail] ──reply──▶ usm.z.ai@agentmail.to
                                │
                   APScheduler triggers every 5 min
                                │
                   Reply Agent reads AgentMail inbox
                                │
                   Filter: not from agent, not labelled "processed"
                                │
                   GLM-5.1: classify_email_intent
                   → find_more_jobs | change_location | change_role
                     | question | apply_help | unsubscribe
                                │
                   GLM-5.1: generate response
                                │
                   AgentMail: reply in same thread
                                │
                   AgentMail: label message "processed"
                                │
                   If unsubscribe: UPDATE job_alerts SET is_active=false
```

#### 2.3.3 Database Schema (Supabase PostgreSQL)

```sql
-- Every resume analysis run
analyses (
    id              TEXT PRIMARY KEY,      -- UUID session identifier
    user_email      TEXT,                  -- logged-in user or 'anonymous'
    created_at      TIMESTAMPTZ,
    job_title       TEXT,                  -- first line extracted from JD
    overall_score   INTEGER,               -- 0–100 weighted score
    verdict         TEXT,                  -- Strong Fit / Good Fit / Partial Fit / Weak Fit / Not a Fit
    summary         TEXT,                  -- one-line summary from Scorer
    roast_opening   TEXT,                  -- first line of roast (shown on history card)
    skills_matched  JSONB,                 -- ["Python", "FastAPI", ...]
    jobs_count      INTEGER,               -- total jobs found
    errors          JSONB,                 -- list of agent errors (if any)
    score_json      JSONB,                 -- full ScoreReport
    profile_json    JSONB                  -- full ResumeProfile
)

-- Email alert subscriptions (one per user_email)
job_alerts (
    user_email      TEXT PRIMARY KEY,
    is_active       BOOLEAN DEFAULT TRUE,
    subscribed_at   TIMESTAMPTZ,
    last_sent_at    TIMESTAMPTZ,
    last_session_id TEXT                   -- most recent analysis session for this user
)

-- Outbound email log (persists across server restarts)
sent_emails (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    to_email    TEXT,
    subject     TEXT,
    sent_at     TIMESTAMPTZ,
    thread_id   TEXT,                      -- AgentMail thread ID for reply tracking
    message_id  TEXT,                      -- AgentMail message ID
    email_type  TEXT                       -- 'job_alert' | 'welcome' | 'cover_letter'
)
```

**Normalisation:** The schema is in 3NF. `analyses` stores one row per session — no many-to-many relationships. `job_alerts` uses `user_email` as the primary key (one subscription per user, upserted). `sent_emails` is a pure log table with no foreign key constraints to keep it writable even if a user is deleted from auth.

---

## 3. Functional Requirements & Scope

### 3.1 Minimum Viable Product

| # | Feature | Description |
|---|---------|-------------|
| 1 | Resume Analysis Pipeline | Parse, score, roast, coach, and match jobs for any resume + JD pair in under 90 seconds |
| 2 | Live Job Matching | Return up to 8 real Malaysian job listings with apply URLs via SerpAPI |
| 3 | Bilingual Cover Letter | Generate cover letters in English and Bahasa Malaysia on demand |
| 4 | Email Alert Subscription | Send daily job alert emails from `usm.z.ai@agentmail.to` |
| 5 | Autonomous Email Reply Agent | Read inbound email replies and respond intelligently without app login |

### 3.2 Non-Functional Requirements (NFRs)

| Quality | Requirement | Implementation |
|---------|-------------|----------------|
| Reliability | Analysis pipeline must complete or return a graceful partial result — never a blank screen | Each agent returns `{}` on failure; orchestrator continues with defaults; errors logged in `session.errors[]` |
| Latency | End-to-end analysis ≤ 90 seconds under normal GLM-5.1 load | Sequential pipeline with progress bar. `llm_client.py` timeout set to 120s per call. |
| GLM Token Latency | Each individual GLM call must return within 60 seconds | Uvicorn async executor wraps GLM calls. 504 retried once after 5s. |
| Cost Efficiency | Token spend per session ≤ ~9,100 tokens | Job Finder uses no LLM. Reply Agent classification call ~500 tokens. No redundant calls. |
| Security | API keys must not be exposed to the frontend | All keys in `.env` loaded server-side only. Frontend uses only publishable Supabase key. |
| Scalability | Platform must handle demo-scale concurrent users (2–5 simultaneous) | In-process pipeline; APScheduler single-threaded. Not designed for production scale — explicitly out of scope for hackathon. |
| Maintainability | Each agent isolated in its own module | `backend/agents/` — one file per agent, one responsibility per file |

### 3.3 Out of Scope / Future Enhancements

- Production-scale deployment (AWS, GCP, or Azure with load balancing)
- Parallel LLM agent execution (intentionally sequential during hackathon)
- Real-time streaming token output to the browser
- Mobile native application (iOS / Android)
- LinkedIn / JobStreet OAuth integration
- In-app resume editor or PDF export of results
- Paid tier / subscription billing
- Multi-user collaborative sessions
- Scheduled daily alert cron job (currently manual-trigger + on-demand)

---

## 4. Monitor, Evaluation, Assumptions & Dependencies

### 4.1 Technical Evaluation

#### 4.1.1 Deployment Strategy
Uncle Kerja is deployed locally during UMHackathon 2026 (localhost:8000 backend, localhost:3000 frontend dev server). For production: the frontend is built via `npm run build` and served as static files from `/frontend/dist` by FastAPI. No separate web server (nginx) is required.

For post-hackathon deployment: a single VPS (e.g., DigitalOcean Droplet, 2 vCPU / 4GB RAM) running Uvicorn behind Caddy (HTTPS reverse proxy) is sufficient for demo-scale traffic.

#### 4.1.2 Emergency Rollback
As this is a hackathon build, rollback is managed via Git. The `main` branch represents the stable demo build. If a breaking change is introduced, `git revert` restores the previous state. The backend holds no in-memory state that is critical — session cache is lost on restart but all analyses are persisted in Supabase and restored from DB on demand.

#### 4.1.3 Priority Matrix

| Priority | Condition | Action |
|----------|-----------|--------|
| P0 Critical | GLM-5.1 API returns 503/504 on all retries — pipeline fails completely | Display error: "Analysis temporarily unavailable. GLM server is busy. Please try again in 2 minutes." Log error. No data lost. |
| P1 High | AgentMail send fails and Gmail SMTP also fails — no welcome email | Subscription saved to DB. User notified in UI: "Subscribed! Email may be delayed." |
| P2 Medium | Supabase DB unreachable — analysis completes but cannot be saved | Session returned to user from in-memory cache. History tab shows error. User can still view results via direct URL. |
| P3 Low | SerpAPI returns 0 results | Cascade to aidevboard → TheirStack. If all return 0, user sees empty jobs tab with guidance to broaden resume skills. |

### 4.2 Monitoring
During the hackathon, monitoring is manual:
- `/health` endpoint returns system status, AgentMail configuration status, and inbox address. Admin panel polls this on load.
- Backend logs all agent start/complete/error events via Python `logging` at INFO level.
- Supabase dashboard provides real-time row counts for `analyses`, `job_alerts`, and `sent_emails`.
- AgentMail dashboard at `agentmail.to` shows full inbox and thread history.

Post-hackathon recommendation: integrate Sentry for error tracking and UptimeRobot for `/health` monitoring.

### 4.3 Assumptions

- Users have a stable internet connection (required for GLM-5.1 API calls and AgentMail)
- The ILMU API server hosting GLM-5.1 is accessible and responsive during the demo
- Supabase project is active and the migration SQL (`supabase_migration.sql`) has been run
- AgentMail inbox `usm.z.ai@agentmail.to` is active and the API key is valid
- SerpAPI key has sufficient remaining credits for live job searches during the demo
- Demo accounts (`admin@demo.local` / `user@demo.local`) work offline via local JWT — no Supabase dependency

### 4.4 External Dependencies

| Tool | Purpose | Risk Level | Mitigation |
|------|---------|-----------|------------|
| Z AI GLM-5.1 (ILMU API) | Core LLM reasoning — all agent tool-call outputs | **High** — if API rate-limited or overloaded, pipeline fails | Single retry on 504. Progress bar keeps user informed during wait. Partial results returned if one agent fails. |
| Supabase (PostgreSQL) | Persistent storage — analyses, alerts, email log | **Medium** — if DB unavailable, history and email logs are inaccessible | In-memory session cache serves live results. DB failure isolated from analysis pipeline. |
| AgentMail | Bidirectional email (send alerts + read replies) | **Medium** — if inbox API fails, email loop breaks | Gmail SMTP fallback for sending. Reply Agent skips processing cycle gracefully if inbox unreachable. |
| SerpAPI | Google Jobs search — primary job source | **Medium** — API credits may be exhausted | 3-layer fallback: SerpAPI → aidevboard → TheirStack. System degrades gracefully to fewer results. |
| Supabase Auth | User authentication (real accounts) | **Low** — Supabase has 99.9% uptime SLA | Local JWT demo accounts work independently of Supabase Auth. |

---

## 5. Project Management & Team Contributions

### 5.1 Project Timeline

| Period | Activity |
|--------|----------|
| Day 1 (24 Apr, AM) | Project scoping, agent architecture design, repo setup, .env configuration |
| Day 1 (24 Apr, PM) | Backend scaffolding: FastAPI structure, `llm_client.py`, Parser Agent, Scorer Agent with Z AI GLM-5.1 |
| Day 1 (24 Apr, Evening) | Roaster Agent, Coach Agent, Job Finder Agent (SerpAPI integration), Orchestrator |
| Day 2 (25 Apr, AM) | Email Agent (AgentMail send), Reply Agent (inbox polling, intent classification), Supabase schema + migration |
| Day 2 (25 Apr, PM) | React frontend: Landing, Login, Analyse, Results pages; NavBar; Auth context |
| Day 2 (25 Apr, Evening) | History page, Alerts page, Admin panel; light theme; bug fixes; README + documentation |

### 5.2 Team Members

| Member | Role | Contributions |
|--------|------|--------------|
| [FILL IN] | [FILL IN] | [FILL IN] |
| [FILL IN] | [FILL IN] | [FILL IN] |
| [FILL IN] | [FILL IN] | [FILL IN] |

### 5.3 Recommendations (Post-Hackathon)

| Area | Recommendation |
|------|---------------|
| Scalability | Move APScheduler to Celery + Redis to support multiple concurrent reply agent workers |
| Caching | Cache SerpAPI job results per (role, location) pair for 6 hours to reduce credit spend |
| Streaming | Replace polling progress bar with Server-Sent Events (SSE) to stream real-time agent status |
| Security | Add rate limiting (SlowAPI) on `/analyze` to prevent abuse. Move to environment-based secrets manager. |
| Database | Add `scores_history` table to track a user's score progression across multiple analyses of the same role |
| Monitoring | Integrate Sentry for error tracking. Add UptimeRobot health checks on `/health` endpoint. |
