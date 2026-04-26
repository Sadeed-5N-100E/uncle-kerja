"""
Orchestrator — runs the full Career Copilot pipeline.

Execution order (optimised for latency):
  1. Parser Agent           (blocking — all others need the profile)
  2. Scorer                 (blocking — roaster, coach, job-finder need it)
  3. Roaster + Coach + Jobs (parallel — all three only need profile + score)
  4. Return merged SessionState

Running all three in parallel at step 3 avoids serial API timeouts that plagued
the old scorer||jobs approach. Each parallel call gets its own TCP connection.
"""
from __future__ import annotations
import sys, time, uuid, logging
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from agents import (
    parser_agent,
    scorer_agent,
    roaster_agent,
    coach_agent,
    job_finder_agent,
    email_agent,
)
from core import mailer

log = logging.getLogger(__name__)

# In-memory session store  {session_id: SessionState}
_sessions: dict[str, dict] = {}


def get_session(session_id: str) -> dict | None:
    return _sessions.get(session_id)


def run_pipeline(
    resume_text: str,
    job_description: str,
    alert_email: str | None = None,
    user_email: str = "anonymous",
    progress_cb=None,
) -> dict:
    """
    Run the full 6-agent pipeline. Returns a completed session dict.
    progress_cb(step, pct) is called after each major step for SSE streaming.
    """
    from datetime import datetime, timezone
    session_id = str(uuid.uuid4())
    session: dict = {
        "session_id":  session_id,
        "user_email":  user_email,
        "created_at":  datetime.now(timezone.utc).isoformat(),
        "status":      "running",
        "profile":     None,
        "score":       None,
        "roast":       None,
        "action_plan": None,
        "jobs":        {"local_jobs": [], "remote_jobs": []},
        "cover_letter": None,
        "alert_email": alert_email,
        "alert_active": bool(alert_email),
        "errors":      [],
        "timings":     {},
    }
    _sessions[session_id] = session

    def _emit(step: str, pct: int):
        session["current_step"] = step
        session["progress_pct"] = pct
        if progress_cb:
            try:
                progress_cb(step, pct)
            except Exception:
                pass

    # ── Step 1: Parse resume ──────────────────────────────────────────────────
    _emit("Parsing resume…", 10)
    t0 = time.time()
    try:
        session["profile"] = parser_agent.run(resume_text)
    except Exception as e:
        log.exception("Parser failed")
        session["errors"].append(f"Parser: {e}")
        session["status"] = "error"
        return session
    session["timings"]["parser"] = round(time.time() - t0, 1)
    _emit("Resume parsed", 30)

    profile = session["profile"]

    # ── Step 2: Score (sequential — needed before roast/coach/jobs) ───────────
    _emit("Scoring resume…", 35)
    t0 = time.time()
    try:
        session["score"] = scorer_agent.run(profile, job_description)
    except Exception as e:
        log.exception("Scorer failed")
        session["errors"].append(f"Scorer: {e}")
        session["score"] = {}
    session["timings"]["scorer"] = round(time.time() - t0, 1)
    _emit("Resume scored", 55)

    score = session["score"]
    job_title = job_description.split("\n")[0][:80] if job_description else "this role"
    session["job_title"] = job_title

    # ── Step 3: Sequential — job finder (no LLM) → roaster → coach ───────────
    # Running all three in parallel overloads ILMU; sequential is reliable.
    # Job finder uses external APIs only (SerpAPI/TheirStack), so it's instant.
    t0 = time.time()

    _emit("Finding matching jobs…", 60)
    try:
        session["jobs"] = job_finder_agent.run(profile, score)
    except Exception as e:
        log.exception("Job finder failed")
        session["errors"].append(f"Jobs: {e}")

    _emit("Roasting your resume…", 70)
    try:
        session["roast"] = roaster_agent.run(profile, score, job_title)
    except Exception as e:
        log.exception("Roaster failed")
        session["errors"].append(f"Roaster: {e}")

    _emit("Building action plan…", 83)
    try:
        session["action_plan"] = coach_agent.run(score, profile)
    except Exception as e:
        log.exception("Coach failed")
        session["errors"].append(f"Coach: {e}")

    session["timings"]["jobs+roast+coach"] = round(time.time() - t0, 1)
    _emit("Analysis complete", 92)

    # ── Step 4: Send job alert email if subscribed ────────────────────────────
    if alert_email and mailer.is_configured():
        all_jobs = (
            (session["jobs"] or {}).get("local_jobs", []) +
            (session["jobs"] or {}).get("remote_jobs", [])
        )
        if all_jobs:
            try:
                alert = email_agent.build_job_alert_html(profile, all_jobs)
                mailer.send(alert_email, alert["subject"], alert["html_body"])
                _emit("Job alert email sent", 97)
            except Exception as e:
                session["errors"].append(f"Email: {e}")

    session["status"] = "done"

    # ── Step 5: Persist to database ───────────────────────────────────────────
    try:
        from core.db import save_analysis, upsert_alert
        save_analysis(session)
        if alert_email:
            upsert_alert(alert_email, session_id)
    except Exception as e:
        log.error(f"DB save failed (non-critical): {e}")

    _emit("Done", 100)
    return session


def generate_cover_letter(session_id: str, job_index: int = 0) -> dict:
    """Generate a cover letter for one of the matched jobs in a session."""
    session = _sessions.get(session_id)
    if not session or not session.get("profile"):
        return {"error": "Session not found or not analysed yet"}

    local_jobs = (session.get("jobs") or {}).get("local_jobs", [])
    if not local_jobs:
        return {"error": "No local jobs found in session"}
    if job_index >= len(local_jobs):
        return {"error": f"Job index {job_index} out of range (max {len(local_jobs)-1})"}

    job = local_jobs[job_index]
    result = email_agent.draft_cover_letter(session["profile"], job)
    session["cover_letter"] = result
    return result
