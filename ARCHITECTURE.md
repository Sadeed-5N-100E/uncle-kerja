# Career Copilot MY — Architecture

## What it does
A multi-agent AI career assistant that:
1. Parses a resume (PDF or text)
2. Scores it against a job description with a multi-dimensional rubric
3. Roasts it with specific, funny critique
4. Coaches the user with a ranked improvement plan
5. Finds matching jobs (Malaysian companies + live remote listings)
6. Drafts a cover letter in English and Bahasa Malaysia
7. Sends job alert emails on a schedule via Gmail

---

## Tech Stack

| Layer | Choice | Why |
|---|---|---|
| LLM | `ilmu-glm-5.1` via ILMU API | Only available model on this key; tool calling confirmed working |
| LLM SDK | `anthropic` (Anthropic-compat endpoint) | Cleaner tool_use blocks than OpenAI endpoint |
| Web framework | FastAPI + Uvicorn | Async, fast, Pydantic schemas, great for SSE streaming |
| PDF parsing | pdfplumber | Best text extraction fidelity for Malaysian resume formats |
| Email | yagmail (Gmail SMTP) | Simplest path; App Password auth; no third-party email service needed |
| Job alerts | APScheduler | In-process scheduler; no Redis/Celery overhead |
| Session store | In-memory Python dict | Sufficient for hackathon; swap for Redis later |
| No LangChain | — | Cold start penalty, opaque abstractions; direct API calls are faster and debuggable |
| No FAISS | — | LLM does skill matching natively; vector DB is overkill here |

---

## Agent Pipeline

```
User uploads PDF + pastes JD
            │
            ▼
    ┌─────────────────┐
    │  Parser Agent   │  PDF/text → structured ResumeProfile (tool call)
    └────────┬────────┘
             │ profile dict
     ┌───────┴────────────────────────────────┐
     │                                        │   (parallel)
     ▼                                        ▼
┌──────────────┐                    ┌──────────────────┐
│ Scorer Agent │                    │ Job Finder Agent │
│ profile + JD │                    │ profile → 5 MY   │
│ → ScoreReport│                    │ jobs + live feed │
└──────┬───────┘                    └────────┬─────────┘
       │                                     │
       ▼                                     │
┌──────────────┐                             │
│ Roaster Agent│                             │
│ score →      │                             │
│ RoastReport  │                             │
└──────┬───────┘                             │
       │                                     │
       ▼                                     │
┌──────────────┐                             │
│ Coach Agent  │                             │
│ score →      │                             │
│ ActionPlan   │                             │
└──────┬───────┘                             │
       │                                     │
       ▼                                     ▼
┌─────────────────────────────────────────────────┐
│                  Orchestrator                   │
│  Merges all results into a single session state │
│  Exposes via FastAPI SSE stream to frontend     │
└──────────────────────┬──────────────────────────┘
                       │
         ┌─────────────┴──────────────┐
         ▼                            ▼
  ┌─────────────┐            ┌─────────────────┐
  │ Email Agent │            │  Frontend Chat  │
  │ cover letter│            │  Score gauge    │
  │ + job alert │            │  Roast card     │
  └─────────────┘            │  Job matches    │
         │                   └─────────────────┘
         ▼
  Gmail SMTP (yagmail)
  + APScheduler daily re-run
```

---

## Agent I/O Contracts

### Parser Agent
- **Input**: `raw_text: str` (extracted from PDF or pasted)
- **Output**: `ResumeProfile` — name, email, years_exp, skills[], experience[], education[], certifications[]
- **LLM call**: tool_choice=`extract_resume`

### Scorer Agent
- **Input**: `ResumeProfile`, `job_description: str`
- **Output**: `ScoreReport` — overall(0-100), skills_score, experience_score, education_score, keyword_score, matched_skills[], missing_skills[], missing_keywords[], verdict, one_line_summary
- **LLM call**: tool_choice=`score_resume`

### Roaster Agent
- **Input**: `ResumeProfile`, `ScoreReport`, `job_title: str`
- **Output**: `RoastReport` — opening_roast, skills_roast, experience_roast, formatting_roast, silver_lining, closing_line, emoji_rating
- **LLM call**: tool_choice=`roast_resume`, temperature=0.8

### Coach Agent
- **Input**: `ScoreReport`, `ResumeProfile`
- **Output**: `ActionPlan` — priority_actions[{rank, action, effort, impact, resources[]}], resume_rewrites[{section, current, improved}], timeline_weeks
- **LLM call**: tool_choice=`build_action_plan`

### Job Finder Agent
- **Input**: `ResumeProfile`, `ScoreReport`
- **Output**: `JobMatches` — local_jobs[5] from LLM (Malaysian companies), remote_jobs[3] from Remotive API
- **LLM call**: tool_choice=`find_jobs` for local curation
- **External call**: `GET https://remotive.com/api/remote-jobs?category=software-dev&limit=50` → filter by skills

### Email Agent
- **Input**: `ResumeProfile`, `job: dict`, `purpose: "cover_letter"|"job_alert"`
- **Output**: `EmailDraft` — subject, body_en, body_ms (for cover letters), html_body (for job alert emails)
- **LLM call**: tool_choice=`draft_email`

---

## Data Schemas (Python dicts, validated by Pydantic in API layer)

```python
ResumeProfile = {
    "full_name": str, "email": str, "phone": str, "location": str,
    "summary": str, "years_experience": float, "current_role": str,
    "skills": list[str], "education": list[dict], "experience": list[dict],
    "certifications": list[str], "languages": list[str]
}

ScoreReport = {
    "overall_score": int,          # 0-100, weighted
    "skills_score": int,           # 40% weight
    "experience_score": int,        # 35% weight
    "education_score": int,         # 15% weight
    "keyword_score": int,           # 10% weight
    "matched_skills": list[str],
    "missing_skills": list[str],
    "bonus_skills": list[str],
    "missing_keywords": list[str],
    "experience_gap": str,
    "verdict": "Strong Fit"|"Good Fit"|"Partial Fit"|"Weak Fit"|"Not a Fit",
    "one_line_summary": str
}

JobMatch = {
    "title": str, "company": str, "location": str,
    "salary_range": str, "match_score": int,
    "why_matched": str, "apply_url": str,
    "source": "ai_curated" | "remotive_live"
}

SessionState = {
    "session_id": str,
    "profile": ResumeProfile | None,
    "score": ScoreReport | None,
    "roast": RoastReport | None,
    "action_plan": ActionPlan | None,
    "jobs": list[JobMatch],
    "alert_email": str | None,
    "alert_active": bool,
    "created_at": str
}
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/analyze` | Upload PDF + JD → triggers full agent pipeline, returns session_id |
| GET | `/session/{id}` | Poll session state (profile, score, roast, jobs) |
| GET | `/health` | Service health check |
| POST | `/cover-letter` | Generate cover letter for a specific job |
| POST | `/alerts/subscribe` | Subscribe email for job alerts |
| DELETE | `/alerts/unsubscribe` | Unsubscribe |

---

## Job Alert Flow

```
1. User opts in with email address after analysis
2. System saves: { session_id, email, profile, job_prefs }
3. APScheduler runs daily at 09:00 MYT
4. For each subscriber: re-run Job Finder Agent → compare with last sent jobs
5. If new matches → Email Agent drafts HTML email → yagmail sends it
6. Email subject: "5 new jobs match your Python profile — Career Copilot MY"
```

---

## Latency Budget

| Step | Time | Strategy |
|------|------|----------|
| Parser Agent | ~10s | Run first, required for all others |
| Scorer + Job Finder | ~15s each | **Run in parallel** after parser |
| Roaster + Coach | ~12s each | **Run in parallel** after scorer |
| Total visible wait | ~37s | Show progress per-agent in UI |

Frontend shows a live progress tracker so each agent's completion is visible — no blank-screen waiting.

---

## Email Setup (Gmail)

1. Create a Gmail account (or use existing)
2. Enable 2-Factor Authentication
3. Go to: Google Account → Security → App passwords → Generate 16-digit App Password
4. Set in `.env`: `GMAIL_USER=you@gmail.com` and `GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx`
5. yagmail handles the rest — no OAuth, no API keys

> Note: yagmail uses `smtplib` under the hood with `smtp.gmail.com:587`.
> The App Password bypasses 2FA for SMTP without exposing your main password.
