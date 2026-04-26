# PRODUCT REQUIREMENT DOCUMENT (PRD)
## UMHackathon 2026

**Project Name:** Uncle Kerja
**Version:** 1.0
**Team:** [FILL IN — Team Name]
**Date:** 25 April 2026

---

## 1. Project Overview

### Problem Statement
Malaysian job seekers, particularly fresh graduates and mid-career professionals, struggle to objectively evaluate their own resumes against specific job requirements. Professional resume review services are expensive, generic, and slow — often taking days. Meanwhile, employers receive hundreds of applications filtered by ATS systems that most applicants do not understand. There is no accessible, affordable, and Malaysia-aware tool that gives a job seeker honest, calibrated, and actionable feedback in real time.

### Target Domain
AI-powered career assistance — specifically resume intelligence, job matching, and autonomous email-based job alerts targeting the Malaysian employment market.

### Proposed Solution Summary
Uncle Kerja removes the friction of career guesswork by enabling any Malaysian job seeker to upload a resume, paste a job description, and receive within 90 seconds: a calibrated fit score, brutally honest feedback, a personalised 6-week improvement plan, live Malaysian job matches, and a bilingual cover letter. An autonomous email agent then monitors the user's email replies and updates their job search — without requiring them to log in again.

---

## 2. Background & Business Objective

### Background of the Problem
Resume screening in Malaysia follows a rigid, manual pipeline. A candidate submits a PDF, an ATS system filters it based on keyword matches, and a recruiter skims it for 6–8 seconds. Candidates have no visibility into why they are rejected. Tools like JobStreet and LinkedIn provide job listings but no feedback loop. Resume writing services cost RM 300–800 and are not calibrated to specific job descriptions.

### Importance of Solving This Issue
By compressing the feedback cycle from weeks to 90 seconds, Uncle Kerja enables candidates to iterate rapidly — like A/B testing their career. Breaking the skill barrier means a diploma holder in Kedah gets the same quality of feedback as someone who can afford a career coach in KL. The email-based reply agent means the system continues serving users autonomously, closing the loop between job alert and application without requiring repeated app logins.

### Strategic Fit / Impact
Uncle Kerja aligns with the Malaysian government's MyDigital Blueprint and HRD Corp's mandate to upskill the workforce. The Coach Agent specifically recommends HRDF-claimable training programmes to close identified skill gaps. The platform is powered by Z AI's GLM-5.1 — a large language model capable of structured tool-call outputs — accessed via the ILMU API, reinforcing local AI infrastructure adoption.

---

## 3. Product Purpose

### 3.1 Main Goal of the System
To provide an AI-powered, Malaysia-aware career intelligence partner that analyses resumes against job descriptions, delivers honest and specific feedback, matches users to live job openings, and maintains an autonomous email-based job alert loop.

### 3.2 Intended Users (Target Audience)

| User Type | Description |
|-----------|-------------|
| Fresh Graduates | SPM / Diploma / Degree holders entering the workforce for the first time |
| Mid-Career Professionals | Employees seeking a role change or promotion with existing experience |
| Job Switchers | Professionals moving between industries who need to understand transferable skill gaps |
| Career Advisors | Counsellors or coaches who want an objective second opinion tool |
| Hiring Managers | Admins who want to monitor system usage and inbox activity |

---

## 4. System Functionalities

### 4.1 Description
Uncle Kerja operates as a sequential multi-agent pipeline powered by Z AI GLM-5.1. Upon receiving a resume and job description, it dispatches seven specialised AI agents in a defined order. Each agent completes one discrete task and passes structured output to the next. The orchestrator merges all outputs into a session, persists it to a Supabase PostgreSQL database, and triggers the Email Agent to begin the alert lifecycle.

### 4.2 Key Functionalities

**Resume Scoring**
Translate a raw resume and job description into a calibrated score (0–100) across four weighted dimensions: Skills (40%), Experience (35%), Education (15%), ATS Keywords (10%). Returns matched skills, missing skills, missing ATS keywords, and a one-line verdict.

**Resume Roasting**
Deliver a sharp, specific critique in the tone of a senior Malaysian recruiter — no generic feedback. Sections cover skills assessment, experience review, presentation quality, a silver lining, and a closing line. Temperature is raised to 0.8 to allow personality in the output.

**Action Planning**
Convert identified gaps into a ranked, effort-tagged 6-week action plan with specific HRDF/HRD Corp-claimable course recommendations, resume rewrite suggestions, and quick wins the candidate can act on immediately.

**Job Matching**
Search live Malaysian job listings from Google Jobs via SerpAPI (primary), AI Dev Board (free fallback for tech roles), and TheirStack (credit-conserving backup). Return up to 8 listings with real apply URLs, match scores, and matched skills.

**Bilingual Cover Letters**
Generate cover letters in both English and formal Bahasa Malaysia (Surat Permohonan Pekerjaan) for any matched job, on demand, personalised to the candidate's profile and the specific company.

**Email Job Alerts**
Send daily HTML job alert emails from `usm.z.ai@agentmail.to` to subscribed users. Emails are logged to the database so the user's personal inbox history is trackable.

**Autonomous Email Reply Agent**
Poll the AgentMail inbox every 5 minutes. Classify inbound user email replies by intent (find more jobs, change location, change role, ask a question, request apply help, unsubscribe). Generate an appropriate response via GLM-5.1 and reply in the same email thread — with no app interaction required from the user.

### 4.3 AI Model & Prompt Design

#### 4.3.1 Model Selection: Z AI GLM-5.1

**Model:** Z AI GLM-5.1, accessed via the ILMU API (`https://api.ilmu.ai/anthropic`).

**Justification:**

| Capability | Why it matters for Uncle Kerja |
|------------|-------------------------------|
| Structured tool-call output | Every agent uses `tool_choice` to force GLM to return a validated JSON schema (ResumeProfile, ScoreReport, RoastReport, ActionPlan). This eliminates free-text parsing fragility. |
| Instruction following | Each agent receives a tightly scoped system prompt with a single responsibility. GLM-5.1 reliably stays within task boundaries without hallucinating extraneous fields. |
| Malaysian context awareness | GLM-5.1 handles Bahasa Malaysia, Malaysian institution names (UM, UTM, UiTM, MMU), Malaysian salary benchmarks (MYR), and local regulatory context (EPF, SOCSO, HRDF). |
| Multi-step reasoning | The Coach Agent requires GLM to cross-reference the ScoreReport and ResumeProfile simultaneously to produce a coherent ranked improvement plan — a multi-input reasoning task. |
| ILMU API access | GLM-5.1 is accessible via the ILMU API during UMHackathon 2026, which was available to the team on 24–25 April 2026 for building and testing the full pipeline. |

#### 4.3.2 Prompting Strategy

**Strategy: Multi-step agentic prompting with enforced tool-call schemas.**

Each of the six GLM-calling agents uses a distinct system prompt with a single `tool_choice` that forces GLM to respond only in a predefined JSON schema. This is a **structured multi-step agentic** approach, not zero-shot or few-shot.

**Why this strategy:**
- **Zero-shot** would produce free-text responses requiring fragile regex parsing. A resume score expressed as prose is useless to the frontend.
- **Few-shot** would inflate token usage per request and is impractical at 5 agents × ~500 tokens = significant cost.
- **Tool-call enforcement** means GLM must fill in every field of the schema or fail validation — the orchestrator catches failures and retries once before recording an error. This gives deterministic, machine-readable output on the first try >95% of the time.

The Reply Agent uses a two-step approach: first classify intent (tool_choice=`classify_email_intent`), then generate a response based on the classified intent. This prevents the model from mixing classification and generation in a single pass.

#### 4.3.3 Context & Input Handling

| Component | Maximum Input | Handling on Overflow |
|-----------|--------------|---------------------|
| Resume text | ~3,000 words (~4,000 tokens) | Text is truncated at extraction time; pdfplumber extracts all pages sequentially and the orchestrator passes the raw extracted string. If the resume exceeds the token window, GLM returns a partial profile — missing fields default to empty lists or `null`. |
| Job description | ~1,500 words (~2,000 tokens) | Passed as-is. If oversized, GLM focuses on the first ~2,000 tokens (the role summary and requirements section, which always appears first in Malaysian JDs). |
| Email reply (Reply Agent) | ~500 words | Truncated at 500 words before classification. Intent classification is a short task and does not need the full email body in most cases. |

The system does not chunk inputs across multiple calls. Truncation is applied before the GLM call. There is no rejection — oversized inputs are silently truncated and the user sees results based on the parsed subset.

#### 4.3.4 Fallback & Failure Behaviour

| Failure Type | Behaviour |
|-------------|-----------|
| GLM returns malformed JSON (tool-call parse failure) | Orchestrator retries once with the same prompt. On second failure, the agent returns `{}` and logs the error in the session's `errors[]` array. The pipeline continues with the next agent using defaults. |
| GLM returns HTTP 504 (timeout) | `llm_client.py` catches the 504 and retries once with a 5-second delay. If the second call also times out, the agent is marked as failed and downstream agents receive an empty input schema. |
| Job search APIs return 0 results | Job Finder cascades to the next source (SerpAPI → aidevboard → TheirStack). If all three return 0 results, `local_jobs=[]` and `remote_jobs=[]` are returned. The user sees an empty jobs tab with a message to broaden their resume. |
| AgentMail send failure | Mailer falls back to Gmail SMTP (`tomleeatwork@gmail.com`). If SMTP also fails, the subscription is saved to the database but no welcome email is sent. The user can trigger a resend from `/alerts`. |
| Reply Agent intent: unrecognised | If GLM classifies intent as `other`, the Reply Agent sends a default "I'm not sure what you mean — here are your options" email and does not label the message as processed, so it will be re-evaluated on the next poll cycle. |

---

## 5. User Stories & Use Cases

### User Stories

| # | As a… | I want to… | So that… |
|---|-------|------------|----------|
| US-01 | Fresh graduate | Upload my resume and paste a software engineer JD | I can see exactly where my skills fall short before applying |
| US-02 | Mid-career professional | Get a score and verdict on my resume against a specific role | I can decide whether to apply or upskill first |
| US-03 | Job seeker | Read honest, specific feedback on my resume | I know what to rewrite, not just "improve your skills" |
| US-04 | Job seeker | Receive a ranked action plan | I have a concrete 6-week improvement roadmap |
| US-05 | Job seeker | See live Malaysian job matches with apply links | I can act on the results immediately |
| US-06 | Job seeker | Generate a cover letter in Bahasa Malaysia | I can apply to government-linked companies with a proper Surat Permohonan |
| US-07 | Subscriber | Receive daily job alerts by email | I stay updated without logging into the app |
| US-08 | Subscriber | Reply to the alert email to change my search | I can refine my job search in seconds from my phone |
| US-09 | Admin | View the full AgentMail inbox and system health | I can monitor the platform and process replies manually if needed |

### Use Cases (Main Interactions)

**Resume Analysis Flow**
User navigates to `/analyse`, uploads a PDF or pastes resume text, pastes the job description, and optionally enters an email for alerts. Clicking "Analyse Resume" triggers `POST /analyze`. The 7-agent pipeline runs sequentially. After ~90 seconds, the user is redirected to `/results/:id` with four tabbed views: Score, Roast, Action Plan, Jobs.

**Cover Letter Generation**
On the Jobs tab, user clicks "Cover Letter" on any matched job. `POST /cover-letter` triggers the Email Agent to generate both English and Bahasa Malaysia versions using the stored profile. The bilingual modal opens with copy-to-clipboard support.

**Alert Subscription & Email Reply Loop**
User enters their email on `/alerts` and clicks Subscribe. A welcome email arrives from `usm.z.ai@agentmail.to`. The next morning, a job alert arrives. The user replies: *"Can you find me React jobs in Penang instead?"* Within 5 minutes, the Reply Agent reads the reply, classifies intent as `change_location`, re-runs the Job Finder with `location=Penang`, and replies in the same email thread with updated listings.

**Admin Monitoring**
Admin logs in with `tomleeatwork+Admin@gmail.com`. The `/admin` panel loads system health (🟢 OK), AgentMail inbox status, DB statistics (total analyses, active alerts, emails sent), and the full AgentMail inbox table. Admin can manually trigger the Reply Agent and refresh all data.

---

## 6. Features Included (Scope Definition)

- Sequential 7-agent AI pipeline (Parser → Scorer → Job Finder → Roaster → Coach → Email → Reply)
- Resume upload (PDF via pdfplumber) and text paste input
- Score output across 4 weighted dimensions with skill gap visualisation
- Roast with 5 subsections (skills, experience, formatting, silver lining, closing)
- 6-week ranked action plan with HRDF course recommendations
- Live Malaysian job search via SerpAPI + aidevboard + TheirStack (3-layer fallback)
- Bilingual cover letter generation (English + Bahasa Malaysia)
- Daily job alert email subscription via AgentMail (`usm.z.ai@agentmail.to`)
- Autonomous email reply agent (runs every 5 minutes via APScheduler)
- Analysis history persisted in Supabase — viewable across sessions and logins
- Dual-mode authentication (Supabase JWT for real accounts, local JWT for offline demo)
- Role-based access (admin vs. user) with separate inbox views
- Admin panel with health monitoring, inbox table, DB stats, and manual Reply Agent trigger
- Responsive React frontend (7 pages) with light theme

---

## 7. Features Not Included (Scope Control)

- Real-time streaming of agent responses (results appear all at once after pipeline completion)
- Parallel LLM calls (intentionally sequential to prevent ILMU API overload during demo)
- Mobile native application (web-responsive only)
- Resume builder or editor (analysis only — no in-app resume editing)
- Job application tracking (click-through to external apply URLs only)
- Multi-language UI (English only; cover letters bilingual by output, not interface)
- LinkedIn or JobStreet OAuth integration
- Team or collaborative features (single-user sessions only)
- Paid subscription or payment processing
- PDF export of results or action plan

---

## 8. Assumptions & Constraints

### LLM Cost Constraint

**Estimated token cost per average user session:**

| Agent | Input tokens (est.) | Output tokens (est.) |
|-------|--------------------|--------------------|
| Parser | ~2,500 | ~400 |
| Scorer | ~1,000 | ~300 |
| Roaster | ~1,200 | ~500 |
| Coach | ~800 | ~600 |
| Email Agent (cover letter) | ~1,000 | ~800 |
| **Total per session** | **~6,500** | **~2,600** |
| **Grand total** | **~9,100 tokens/session** | |

**Cost-reduction decisions made:**
- **Sequential execution** — no redundant parallel calls to GLM; each agent runs only once.
- **Tool-call enforcement** — structured output eliminates retry loops caused by free-text parsing failures, reducing token waste.
- **Job Finder uses no LLM** — the most token-hungry step (searching many listings) uses pure API calls.
- **Reply Agent truncates emails at 500 words** — short classification prompts (~300 tokens) keep the autonomous loop cost-minimal.

### Technical Constraints
- The GLM-5.1 server via ILMU API was intermittently overloaded during the hackathon on 24–25 April 2026. The `llm_client.py` implements a single retry on HTTP 504. A fallback LLM can be substituted by changing one environment variable (`ILMU_API_KEY` and updating `config.py`).
- PDF parsing relies on `pdfplumber` with `pypdf` fallback. Image-based PDFs (scanned resumes) return empty text and the system returns HTTP 400 with a clear error message.
- AgentMail inbox polling is in-process via APScheduler. There is no Redis or Celery. If the server restarts, the scheduler restarts automatically via the FastAPI lifespan hook but in-flight polls are lost.

### Performance Constraints
- End-to-end pipeline latency is ~90 seconds on the ILMU GLM-5.1 server. The frontend displays a real-time progress bar with step-by-step status updates so users understand the wait is expected.
- The platform is designed for single-user demo use. Concurrent analyses may queue behind each other due to sequential GLM calls.

### User Input
- The system requires at minimum a non-empty resume text and a non-empty job description. Both inputs are validated on the backend before the pipeline starts.
- The email alert feature requires a valid email address. No email verification is performed — users can subscribe with any address.
