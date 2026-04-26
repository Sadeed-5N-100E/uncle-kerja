"""
Database layer — Supabase (PostgreSQL).

Uses the service role key which bypasses Row Level Security.
All three tables must exist first — run supabase_migration.sql in the
Supabase Dashboard → SQL Editor once.

Tables:
  public.analyses    — every resume analysis session
  public.job_alerts  — email alert subscriptions
  public.sent_emails — outbound job alert email log
"""
from __future__ import annotations
import os, json, logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv(Path(__file__).parents[2] / ".env", override=True)

log = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("NEXT_PUBLIC_SUPABASE_URL", "")
SERVICE_KEY  = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_sb: Client | None = None


def _client() -> Client:
    global _sb
    if _sb is None:
        if not SUPABASE_URL or not SERVICE_KEY:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
        _sb = create_client(SUPABASE_URL, SERVICE_KEY)
    return _sb


def init_db() -> None:
    """Verify connection. Tables must already exist (run supabase_migration.sql)."""
    try:
        _client().table("analyses").select("id").limit(1).execute()
        log.info("Supabase DB connected — analyses table OK")
    except Exception as e:
        log.error(f"Supabase init failed: {e}. Did you run supabase_migration.sql?")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── analyses ──────────────────────────────────────────────────────────────────

def save_analysis(session: dict) -> None:
    """Persist a completed session to Supabase analyses table."""
    try:
        score   = session.get("score")   or {}
        profile = session.get("profile") or {}
        roast   = session.get("roast")   or {}
        jobs    = session.get("jobs")    or {}

        local_jobs  = jobs.get("local_jobs",  []) or []
        remote_jobs = jobs.get("remote_jobs", []) or []

        _client().table("analyses").upsert({
            "id":             session.get("session_id", ""),
            "user_email":     session.get("user_email", "anonymous"),
            "created_at":     session.get("created_at", _now()),
            "job_title":      session.get("job_title"),
            "overall_score":  score.get("overall_score"),
            "verdict":        score.get("verdict"),
            "summary":        score.get("one_line_summary"),
            "roast_opening":  roast.get("opening_roast"),
            "skills_matched": score.get("matched_skills", []),
            "jobs_count":     len(local_jobs) + len(remote_jobs),
            "errors":         session.get("errors", []),
            "score_json":     score,
            "profile_json":   profile,
        }).execute()
        log.info(f"Analysis saved: {session.get('session_id')}")
    except Exception as e:
        log.error(f"save_analysis failed: {e}")


def get_analyses_for(user_email: str, limit: int = 10) -> list[dict]:
    """Return recent analyses for one user, newest first."""
    try:
        r = (_client().table("analyses")
             .select("id,created_at,job_title,overall_score,verdict,summary,roast_opening,jobs_count,user_email")
             .eq("user_email", user_email)
             .order("created_at", desc=True)
             .limit(limit)
             .execute())
        return r.data or []
    except Exception as e:
        log.error(f"get_analyses_for failed: {e}")
        return []


def get_all_analyses(limit: int = 50) -> list[dict]:
    """Admin view — all analyses, newest first."""
    try:
        r = (_client().table("analyses")
             .select("id,created_at,job_title,overall_score,verdict,summary,roast_opening,jobs_count,user_email")
             .order("created_at", desc=True)
             .limit(limit)
             .execute())
        return r.data or []
    except Exception as e:
        log.error(f"get_all_analyses failed: {e}")
        return []


def get_analysis_by_id(session_id: str) -> dict | None:
    """Return full analysis row including score_json and profile_json."""
    try:
        r = (_client().table("analyses")
             .select("*")
             .eq("id", session_id)
             .single()
             .execute())
        return r.data
    except Exception as e:
        log.error(f"get_analysis_by_id failed: {e}")
        return None


# ── job_alerts ────────────────────────────────────────────────────────────────

def upsert_alert(user_email: str, session_id: str = "") -> None:
    try:
        _client().table("job_alerts").upsert({
            "user_email":     user_email,
            "is_active":      True,
            "subscribed_at":  _now(),
            "last_session_id": session_id,
        }, on_conflict="user_email").execute()
    except Exception as e:
        log.error(f"upsert_alert failed: {e}")


def deactivate_alert(user_email: str) -> None:
    try:
        _client().table("job_alerts").update({"is_active": False}).eq("user_email", user_email).execute()
    except Exception as e:
        log.error(f"deactivate_alert failed: {e}")


def get_active_alerts() -> list[dict]:
    try:
        r = _client().table("job_alerts").select("*").eq("is_active", True).execute()
        return r.data or []
    except Exception as e:
        log.error(f"get_active_alerts failed: {e}")
        return []


# ── sent_emails ───────────────────────────────────────────────────────────────

def log_sent_email(to_email: str, subject: str, thread_id: str = "",
                   message_id: str = "", email_type: str = "job_alert") -> None:
    try:
        _client().table("sent_emails").insert({
            "to_email":   to_email,
            "subject":    subject,
            "sent_at":    _now(),
            "thread_id":  thread_id,
            "message_id": message_id,
            "email_type": email_type,
        }).execute()
    except Exception as e:
        log.error(f"log_sent_email failed: {e}")


def get_sent_emails_for(email: str, limit: int = 10) -> list[dict]:
    try:
        r = (_client().table("sent_emails")
             .select("subject,sent_at,thread_id,email_type")
             .eq("to_email", email)
             .order("sent_at", desc=True)
             .limit(limit)
             .execute())
        return r.data or []
    except Exception as e:
        log.error(f"get_sent_emails_for failed: {e}")
        return []


def get_all_sent_emails(limit: int = 30) -> list[dict]:
    try:
        r = (_client().table("sent_emails")
             .select("*")
             .order("sent_at", desc=True)
             .limit(limit)
             .execute())
        return r.data or []
    except Exception as e:
        log.error(f"get_all_sent_emails failed: {e}")
        return []


# ── stats ─────────────────────────────────────────────────────────────────────

def db_stats() -> dict:
    try:
        sb = _client()
        analyses    = sb.table("analyses").select("id", count="exact").execute().count or 0
        alerts      = sb.table("job_alerts").select("user_email", count="exact").eq("is_active", True).execute().count or 0
        sent_emails = sb.table("sent_emails").select("id", count="exact").execute().count or 0
        return {
            "analyses":    analyses,
            "alerts":      alerts,
            "sent_emails": sent_emails,
            "backend":     "supabase",
            "project":     SUPABASE_URL,
        }
    except Exception as e:
        return {"error": str(e), "backend": "supabase"}
