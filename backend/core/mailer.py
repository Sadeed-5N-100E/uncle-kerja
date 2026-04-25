"""
Mailer — sends emails via AgentMail API (primary) or Gmail SMTP (fallback).

AgentMail gives us bidirectional email: we can also READ replies from users.
Inbox: usm.z.ai@agentmail.to  /  display name: Career Copilot MY
"""
from __future__ import annotations
import os, json, logging
from pathlib import Path
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env")

log = logging.getLogger(__name__)

# In-memory log of sent job alert emails {to_email: [{subject, sent_at, thread_id}]}
_sent_log: dict[str, list[dict]] = {}

AGENTMAIL_API_KEY  = os.getenv("AGENTMAIL_API_KEY", "")
AGENTMAIL_INBOX_ID = os.getenv("AGENTMAIL_INBOX_ID", "usm.z.ai@agentmail.to")
AGENTMAIL_BASE     = "https://api.agentmail.to"

GMAIL_USER     = os.getenv("GMAIL_USER", "")
GMAIL_APP_PASS = os.getenv("GMAIL_APP_PASSWORD", "")


# ── AgentMail helpers ─────────────────────────────────────────────────────────

def _am_headers() -> dict:
    return {
        "Authorization": f"Bearer {AGENTMAIL_API_KEY}",
        "Content-Type":  "application/json",
        "Accept":        "application/json",
    }


def _am_request(method: str, path: str, body: dict | None = None) -> dict:
    url = AGENTMAIL_BASE + path
    resp = httpx.request(
        method, url,
        headers=_am_headers(),
        json=body,
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json() if resp.text.strip() else {}


# ── Public send API ───────────────────────────────────────────────────────────

def send(
    to: str | list[str],
    subject: str,
    html_body: str,
    plain_body: str = "",
    reply_to: str | None = None,
    thread_id: str | None = None,
) -> dict | None:
    """
    Send via AgentMail. Returns the sent message metadata, or None on error.
    to can be a single address or a list.
    """
    recipients = [to] if isinstance(to, str) else to
    payload: dict[str, Any] = {
        "to":      recipients,
        "subject": subject,
        "html":    html_body,
        "text":    plain_body or _strip_html(html_body),
    }
    if reply_to:
        payload["reply_to"] = reply_to
    # thread_id is not a send param — AgentMail threads by In-Reply-To header;
    # for job alerts we always open a new thread.

    try:
        result = _am_request(
            "POST",
            f"/inboxes/{AGENTMAIL_INBOX_ID}/messages/send",
            payload,
        )
        log.info(f"AgentMail sent to {recipients}: thread={result.get('thread_id')}")
        # Track in sent log so users see only their own emails
        import datetime
        entry = {
            "subject":    subject,
            "sent_at":    datetime.datetime.utcnow().isoformat() + "Z",
            "thread_id":  result.get("thread_id", ""),
            "message_id": result.get("message_id", ""),
        }
        for r in recipients:
            _sent_log.setdefault(r.lower(), []).append(entry)
        return result
    except Exception as e:
        log.error(f"AgentMail send failed: {e}. Falling back to Gmail SMTP.")
        return _gmail_fallback(recipients[0], subject, html_body, plain_body)


def reply_to_message(message_id: str, html: str, text: str = "") -> dict | None:
    """Reply to a specific inbound message (keeps the thread together)."""
    try:
        result = _am_request(
            "POST",
            f"/inboxes/{AGENTMAIL_INBOX_ID}/messages/{message_id}/reply",
            {"html": html, "text": text or _strip_html(html)},
        )
        log.info(f"AgentMail replied to {message_id}")
        return result
    except Exception as e:
        log.error(f"AgentMail reply failed: {e}")
        return None


# ── Inbox reading ─────────────────────────────────────────────────────────────

def list_unread_messages(limit: int = 20) -> list[dict]:
    """Fetch recent inbox messages (all, since AgentMail has no 'unread' label by default)."""
    try:
        data = _am_request("GET", f"/inboxes/{AGENTMAIL_INBOX_ID}/messages?limit={limit}")
        return data.get("messages", [])
    except Exception as e:
        log.error(f"AgentMail list failed: {e}")
        return []


def get_thread(thread_id: str) -> dict:
    """Get all messages in a thread."""
    try:
        return _am_request("GET", f"/threads/{thread_id}")
    except Exception as e:
        log.error(f"AgentMail get_thread failed: {e}")
        return {}


def mark_processed(message_id: str) -> None:
    """Label a message as processed so the reply agent doesn't handle it twice."""
    try:
        _am_request(
            "PATCH",
            f"/inboxes/{AGENTMAIL_INBOX_ID}/messages/{message_id}",
            {"add_labels": ["processed"]},
        )
    except Exception as e:
        log.warning(f"Could not label message {message_id}: {e}")


def list_pending_replies(limit: int = 10) -> list[dict]:
    """Messages that arrived in our inbox and haven't been labelled 'processed' yet."""
    try:
        # Get all messages, then filter out ones we sent (check 'from' field)
        data = _am_request(
            "GET",
            f"/inboxes/{AGENTMAIL_INBOX_ID}/messages?limit={limit}",
        )
        msgs = data.get("messages", [])
        # Inbound = from address is NOT our inbox
        inbound = [m for m in msgs if AGENTMAIL_INBOX_ID not in m.get("from", "")
                   and "processed" not in (m.get("labels") or [])]
        return inbound
    except Exception as e:
        log.error(f"AgentMail list_pending_replies failed: {e}")
        return []


def get_sent_emails_for(email: str, limit: int = 10) -> list[dict]:
    """Return job alert emails sent to a specific address (from in-memory log)."""
    return list(reversed(_sent_log.get(email.lower(), [])))[:limit]


# ── Status ────────────────────────────────────────────────────────────────────

def is_configured() -> bool:
    return bool(AGENTMAIL_API_KEY)


def inbox_address() -> str:
    return AGENTMAIL_INBOX_ID


# ── Gmail SMTP fallback ───────────────────────────────────────────────────────

def _gmail_fallback(to: str, subject: str, html: str, plain: str) -> None:
    if not (GMAIL_USER and GMAIL_APP_PASS):
        log.error("No Gmail fallback configured either.")
        return None
    try:
        import yagmail
        yag = yagmail.SMTP(GMAIL_USER, GMAIL_APP_PASS)
        yag.send(to=to, subject=subject, contents=[html or plain])
        log.info(f"Gmail fallback sent to {to}")
    except Exception as e:
        log.error(f"Gmail fallback also failed: {e}")
    return None


def _strip_html(html: str) -> str:
    """Very basic HTML → plain text for text/plain part."""
    import re
    return re.sub(r"<[^>]+>", "", html).strip()
