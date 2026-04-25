"""
Reply Agent — processes inbound emails to the Career Copilot MY inbox.

When a user replies to a job alert or writes in directly, this agent:
  1. Reads the email content
  2. Classifies the intent (more jobs / different location / unsubscribe / question)
  3. Runs the appropriate tool (re-run job finder, answer question, etc.)
  4. Replies via AgentMail keeping the thread intact

Designed to be called on a schedule (e.g., every 5 min) or from a webhook.
"""
from __future__ import annotations
import sys, logging
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat, extract_tool_input
from core import mailer

log = logging.getLogger(__name__)

# ── Intent classifier tool ────────────────────────────────────────────────────
CLASSIFY_TOOL = {
    "name": "classify_email_intent",
    "description": "Classify the user's intent from their email reply and extract key parameters.",
    "input_schema": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "enum": [
                    "find_more_jobs",       # "find me more jobs", "any Django jobs?"
                    "change_location",      # "looking for jobs in Penang now"
                    "change_role",          # "actually I want frontend jobs"
                    "question",             # general career question
                    "unsubscribe",          # "stop sending me emails"
                    "apply_help",           # "how do I apply for the Shopee job?"
                    "other",
                ],
            },
            "new_location":    {"type": "string",  "description": "If intent=change_location, the new city/state"},
            "new_role":        {"type": "string",  "description": "If intent=change_role, the new role type"},
            "question_text":   {"type": "string",  "description": "If intent=question, the question verbatim"},
            "job_name":        {"type": "string",  "description": "If intent=apply_help, the job title/company mentioned"},
            "confidence":      {"type": "string",  "enum": ["high", "medium", "low"]},
            "user_sentiment":  {"type": "string",  "enum": ["positive", "neutral", "frustrated"]},
        },
        "required": ["intent", "confidence", "user_sentiment"],
    },
}

CLASSIFY_SYSTEM = (
    "You classify inbound emails from job-seekers replying to a career AI assistant. "
    "Read the email and identify what the user wants. Use classify_email_intent tool."
)


def _classify(email_text: str) -> dict:
    resp = chat(
        system=CLASSIFY_SYSTEM,
        messages=[{"role": "user", "content": f"Email content:\n\n{email_text}"}],
        tools=[CLASSIFY_TOOL],
        tool_choice={"type": "tool", "name": "classify_email_intent"},
        max_tokens=512,
    )
    return extract_tool_input(resp, "classify_email_intent")


# ── Response builder ──────────────────────────────────────────────────────────
RESPOND_SYSTEM = (
    "You are Career Copilot MY, an AI career assistant. "
    "You're replying to a user's email. Be helpful, concise, and warm. "
    "You use HTML for emails. Sign off as 'Career Copilot MY 🎯'."
)


def _build_response(intent: dict, email_text: str, session: dict | None) -> str:
    """Generate an HTML reply body for the given intent."""
    action = intent.get("intent", "other")

    if action == "unsubscribe":
        return (
            "<p>No problem — you've been unsubscribed from Career Copilot MY job alerts.</p>"
            "<p>If you ever want to come back, just upload your resume again at the app.</p>"
            "<p>Best of luck in your job search! 🎯</p>"
        )

    if action == "find_more_jobs":
        # Re-run job finder with the user's stored profile
        if session and session.get("profile") and session.get("score"):
            from agents import job_finder_agent, email_agent
            jobs = job_finder_agent.run(session["profile"], session["score"])
            all_jobs = jobs.get("local_jobs", []) + jobs.get("remote_jobs", [])
            if all_jobs:
                alert = email_agent.build_job_alert_html(session["profile"], all_jobs)
                return alert["html_body"]
        return "<p>I've noted your request! Please upload your resume via the app to get fresh job matches.</p>"

    if action == "question":
        question = intent.get("question_text", email_text)
        resp = chat(
            system=RESPOND_SYSTEM,
            messages=[{"role": "user", "content": f"User's career question (reply as HTML email):\n\n{question}"}],
            max_tokens=600,
        )
        from core.llm_client import extract_text
        answer = extract_text(resp)
        return f"<div>{answer}</div><br><p>— Career Copilot MY 🎯</p>"

    if action == "apply_help":
        job = intent.get("job_name", "the job")
        resp = chat(
            system=RESPOND_SYSTEM,
            messages=[{"role": "user", "content": f"User wants help applying for: {job}. Reply as HTML email with practical application tips."}],
            max_tokens=500,
        )
        from core.llm_client import extract_text
        answer = extract_text(resp)
        return f"<div>{answer}</div><br><p>— Career Copilot MY 🎯</p>"

    # Default: acknowledge + offer help
    resp = chat(
        system=RESPOND_SYSTEM,
        messages=[{"role": "user", "content": f"Reply to this user email as Career Copilot MY (HTML):\n\n{email_text}"}],
        max_tokens=400,
    )
    from core.llm_client import extract_text
    return f"<div>{extract_text(resp)}</div><br><p>— Career Copilot MY 🎯</p>"


# ── Main entry point ──────────────────────────────────────────────────────────

def process_inbox(sessions: dict | None = None) -> list[dict]:
    """
    Poll for unprocessed inbound messages, classify each, and reply.
    sessions: the in-memory session store from orchestrator (to find user profiles).
    Returns list of processed message summaries.
    """
    pending = mailer.list_pending_replies()
    processed = []

    for msg in pending:
        msg_id      = msg.get("message_id", "")
        from_addr   = msg.get("from", "")
        subject     = msg.get("subject", "")
        body        = msg.get("extracted_text") or msg.get("text") or ""
        thread_id   = msg.get("thread_id", "")

        log.info(f"Processing reply from {from_addr}: {subject!r}")

        # Find session by matching alert_email to from_addr
        session = None
        if sessions:
            for s in sessions.values():
                if s.get("alert_email", "").lower() == from_addr.lower():
                    session = s
                    break

        try:
            intent       = _classify(body or subject)
            action       = intent.get("intent", "other")

            # Handle unsubscribe in session
            if action == "unsubscribe" and session:
                session["alert_active"] = False

            html_reply   = _build_response(intent, body or subject, session)
            mailer.reply_to_message(msg_id, html_reply)
            mailer.mark_processed(msg_id)

            processed.append({
                "from":    from_addr,
                "subject": subject,
                "intent":  action,
                "replied": True,
            })
            log.info(f"Replied to {from_addr} (intent={action})")

        except Exception as e:
            log.error(f"Failed to process message {msg_id}: {e}")
            processed.append({"from": from_addr, "subject": subject, "error": str(e)})

    return processed
