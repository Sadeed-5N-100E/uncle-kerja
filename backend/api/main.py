"""
Career Copilot MY — FastAPI server

Start: uvicorn api.main:app --reload --port 8000

Dev:   run frontend separately → cd frontend && npm run dev  (port 3000)
Prod:  cd frontend && npm run build  →  FastAPI serves dist/ as SPA
"""
from __future__ import annotations
import sys, io, os, logging
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]))

from contextlib import asynccontextmanager
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from apscheduler.schedulers.background import BackgroundScheduler

import pdfplumber
from agents import orchestrator, reply_agent
from api.schemas import CoverLetterRequest, AlertSubscribeRequest
from core import mailer

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler()


def _poll_inbox():
    results = reply_agent.process_inbox(sessions=orchestrator._sessions)
    if results:
        log.info(f"Reply agent: {len(results)} messages processed")


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.db import init_db
    init_db()
    scheduler.add_job(_poll_inbox, "interval", minutes=5, id="inbox_poll")
    scheduler.start()
    log.info(f"Uncle Kerja ready. AgentMail: {mailer.inbox_address()}")
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Career Copilot MY", version="1.0.0", lifespan=lifespan)

# ── CORS (allow Vite dev server + any origin) ─────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000", "*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Auth routes ───────────────────────────────────────────────────────────────
from api.routes.auth_routes import router as auth_router
app.include_router(auth_router)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _extract_pdf_text(file_bytes: bytes) -> str:
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
        text = "\n".join(pages).strip()
        if not text:
            # Fallback: try pypdf
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(p.extract_text() or "" for p in reader.pages)
        return text
    except Exception as e:
        log.warning(f"PDF extract error: {e}")
        return ""


# ── API routes ────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "agentmail_inbox": mailer.inbox_address(), "email_ready": mailer.is_configured()}


@app.post("/analyze")
async def analyze(
    request:         Request,
    job_description: str = Form(...),
    alert_email:     str = Form(""),
    resume_text:     str = Form(""),
    resume_file: UploadFile = File(None),
):
    if resume_file and resume_file.filename:
        raw  = await resume_file.read()
        text = _extract_pdf_text(raw) if resume_file.filename.lower().endswith(".pdf") \
               else raw.decode("utf-8", errors="ignore")
    elif resume_text:
        text = resume_text
    else:
        raise HTTPException(400, "Provide either resume_file or resume_text")

    if not text.strip():
        raise HTTPException(400, "Could not extract text from resume")

    # Extract user identity from Bearer token if present
    user_email = "anonymous"
    auth_header = request.headers.get("authorization", "")
    if auth_header.startswith("Bearer "):
        from core.auth import get_user
        u = get_user(auth_header.split(" ", 1)[1])
        if u:
            user_email = u.get("email", "anonymous")

    import asyncio
    session = await asyncio.get_event_loop().run_in_executor(
        None, lambda: orchestrator.run_pipeline(
            text, job_description,
            alert_email.strip() or None,
            user_email=user_email,
        )
    )
    return JSONResponse(session)


@app.get("/session/{session_id}")
def get_session(session_id: str):
    s = orchestrator.get_session(session_id)
    if not s: raise HTTPException(404, "Session not found")
    return JSONResponse(s)


@app.post("/cover-letter")
async def cover_letter(req: CoverLetterRequest):
    import asyncio
    result = await asyncio.get_event_loop().run_in_executor(
        None, lambda: orchestrator.generate_cover_letter(req.session_id, req.job_index)
    )
    if "error" in result: raise HTTPException(400, result["error"])
    return JSONResponse(result)


@app.post("/alerts/subscribe")
def subscribe_alerts(req: AlertSubscribeRequest):
    session = orchestrator.get_session(req.session_id)
    if not session: raise HTTPException(404, "Session not found")
    session["alert_email"]  = req.email
    session["alert_active"] = True

    sent = False
    if mailer.is_configured():
        from agents.email_agent import build_job_alert_html, _build_welcome_html
        profile  = session.get("profile") or {}
        all_jobs = (session.get("jobs") or {}).get("local_jobs", []) + \
                   (session.get("jobs") or {}).get("remote_jobs", [])
        if all_jobs:
            a    = build_job_alert_html(profile, all_jobs)
            html, subj = a["html_body"], a["subject"]
        else:
            html = _build_welcome_html(profile, mailer.inbox_address())
            subj = "Welcome to Career Copilot MY job alerts"
        sent = bool(mailer.send(req.email, subj, html))

    return {"subscribed": True, "welcome_email_sent": sent,
            "sent_from": mailer.inbox_address(),
            "note": f"Replies to {mailer.inbox_address()} are handled by the AI agent."}


@app.delete("/alerts/unsubscribe/{session_id}")
def unsubscribe(session_id: str):
    s = orchestrator.get_session(session_id)
    if s: s["alert_active"] = False
    return {"unsubscribed": True}


@app.post("/inbox/poll")
def poll_inbox_now():
    results = reply_agent.process_inbox(sessions=orchestrator._sessions)
    return {"processed": results, "count": len(results)}


@app.get("/inbox/messages")
def inbox_messages(limit: int = 20):
    msgs = mailer.list_unread_messages(limit=limit)
    return {"messages": msgs, "count": len(msgs), "inbox": mailer.inbox_address()}


@app.get("/inbox/job-emails")
def job_emails(email: str = "", limit: int = 10):
    """
    Return job alert emails sent to a specific address.
    Pass ?email=user@gmail.com to filter by recipient.
    Falls back to all recent sent msgs if email not provided.
    """
    if email:
        entries = mailer.get_sent_emails_for(email, limit=limit)
        # Shape matches the AgentMail message format the frontend expects
        shaped = [{
            "subject":    e["subject"],
            "created_at": e["sent_at"],
            "labels":     ["sent"],
            "from":       f"Uncle Kerja <{mailer.inbox_address()}>",
        } for e in entries]
        return {"emails": shaped, "count": len(shaped)}

    # No email — return all recent sent job alerts (admin view)
    msgs = mailer.list_unread_messages(limit=limit)
    JOB_KEYWORDS = ("jobs match", "job alert", "uncle kerja", "career copilot", "🎯")
    job_msgs = [
        m for m in msgs
        if any(kw.lower() in (m.get("subject") or "").lower() for kw in JOB_KEYWORDS)
        and "sent" in (m.get("labels") or [])
    ]
    return {"emails": job_msgs[:10], "count": len(job_msgs)}


@app.get("/history")
def get_history(request: Request, limit: int = 10):
    """Return analyses for the logged-in user. Admin sees all."""
    from core.db import get_analyses_for, get_all_analyses
    auth = request.headers.get("authorization", "")
    user_email = "anonymous"
    is_admin   = False
    if auth.startswith("Bearer "):
        from core.auth import get_user
        u = get_user(auth.split(" ", 1)[1])
        if u:
            user_email = u.get("email", "anonymous")
            is_admin   = u.get("role") == "admin"

    rows = get_all_analyses(limit=limit) if is_admin else get_analyses_for(user_email, limit=limit)
    # Strip heavy fields for list view
    slim = [{
        "id":            r["id"],
        "created_at":    r["created_at"],
        "job_title":     r["job_title"],
        "overall_score": r["overall_score"],
        "verdict":       r["verdict"],
        "summary":       r["summary"],
        "roast_opening": r["roast_opening"],
        "jobs_count":    r["jobs_count"],
        "user_email":    r["user_email"] if is_admin else None,
    } for r in rows]
    return {"analyses": slim, "count": len(slim)}


@app.get("/history/{session_id}/full")
def get_history_full(session_id: str):
    """Return persisted full session (score + profile JSON) for a past analysis."""
    from core.db import get_analysis_by_id
    import json as _json
    row = get_analysis_by_id(session_id)
    if not row:
        raise HTTPException(404, "Analysis not found")
    result = dict(row)
    # Deserialise JSON columns
    for col in ("score_json", "profile_json", "skills_matched", "errors"):
        if result.get(col):
            try:
                result[col] = _json.loads(result[col])
            except Exception:
                pass
    return result


@app.get("/db/stats")
def db_stats():
    """Admin: database statistics."""
    from core.db import db_stats as _stats
    return _stats()


# ── SPA / static file serving ─────────────────────────────────────────────────
# Serve built Vite assets; fall through to index.html for client-side routing.
# During dev, use `npm run dev` on port 3000 instead.
_DIST = Path(__file__).parents[2] / "frontend" / "dist"

if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=str(_DIST / "assets")), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_catch_all(full_path: str):
        # Don't intercept API paths (shouldn't reach here anyway)
        return FileResponse(str(_DIST / "index.html"))
