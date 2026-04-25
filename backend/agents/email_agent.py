"""
Email Agent — two responsibilities:
  1. draft_cover_letter(profile, job)  →  bilingual cover letter (EN + BM)
  2. build_job_alert_html(profile, jobs)  →  HTML email body for job alerts

Input  (cover letter): ResumeProfile dict, job dict
Input  (alert):        ResumeProfile dict, list[JobMatch]
Output (cover letter): { subject_en, body_en, subject_ms, body_ms }
Output (alert):        { subject, html_body }
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat, extract_tool_input

# ── Cover Letter Tool ──────────────────────────────────────────────────────────
COVER_TOOL = {
    "name": "draft_cover_letter",
    "description": "Draft a professional cover letter in English AND Bahasa Malaysia.",
    "input_schema": {
        "type": "object",
        "properties": {
            "subject_en": {"type": "string"},
            "body_en":    {"type": "string", "description": "Full cover letter in English (3 paragraphs, professional tone)"},
            "subject_ms": {"type": "string"},
            "body_ms":    {"type": "string", "description": "Full cover letter in Bahasa Malaysia (formal Malaysian style, 3 paragraphs)"},
            "highlight_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3-4 skills from the resume most relevant to this job",
            },
        },
        "required": ["subject_en", "body_en", "subject_ms", "body_ms", "highlight_skills"],
    },
}

COVER_SYSTEM = (
    "You are a professional cover letter writer specialising in Malaysian job applications. "
    "English style: confident, concise, 3 paragraphs (hook → skills match → call to action). "
    "Bahasa Malaysia style: formal Surat Permohonan Pekerjaan format. "
    "Never use generic filler — reference specific skills, the company name, and the role. "
    "Use the draft_cover_letter tool."
)


def draft_cover_letter(profile: dict, job: dict) -> dict:
    context = (
        f"Candidate: {profile.get('full_name')}\n"
        f"Email: {profile.get('email', '')}\n"
        f"Current role: {profile.get('current_role', 'Software Developer')}\n"
        f"Years experience: {profile.get('years_experience', 0)}\n"
        f"Skills: {', '.join(profile.get('skills', []))}\n\n"
        f"Applying for: {job.get('title')} at {job.get('company')}\n"
        f"Job location: {job.get('location', 'Malaysia')}\n"
        f"Key requirements: {', '.join(job.get('requirements', []))}\n"
        f"Why matched: {job.get('why_matched', '')}"
    )
    response = chat(
        system=COVER_SYSTEM,
        messages=[{"role": "user", "content": f"Write a cover letter:\n\n{context}"}],
        tools=[COVER_TOOL],
        tool_choice={"type": "tool", "name": "draft_cover_letter"},
    )
    return extract_tool_input(response, "draft_cover_letter")


# ── Job Alert HTML builder ─────────────────────────────────────────────────────
def build_job_alert_html(profile: dict, jobs: list[dict]) -> dict:
    """Build a polished HTML email for job alerts (no LLM call needed — template-based)."""
    name      = profile.get("full_name", "there")
    role      = profile.get("current_role", "Developer")
    all_jobs  = jobs[:8]  # max 8 per alert

    cards = ""
    for j in all_jobs:
        source_badge = (
            '<span style="background:#e8f5e9;color:#2e7d32;padding:2px 8px;border-radius:10px;font-size:11px;">🟢 Live listing</span>'
            if j.get("source") == "remotive_live"
            else '<span style="background:#e3f2fd;color:#1565c0;padding:2px 8px;border-radius:10px;font-size:11px;">🤖 AI curated</span>'
        )
        score_color = "#2e7d32" if j.get("match_score", 0) >= 70 else "#f57c00" if j.get("match_score", 0) >= 50 else "#c62828"
        cards += f"""
        <div style="border:1px solid #e0e0e0;border-radius:8px;padding:16px;margin-bottom:12px;background:#fff;">
            <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                    <div style="font-size:16px;font-weight:600;color:#1a1a2e;">{j.get('title','')}</div>
                    <div style="color:#555;margin-top:2px;">{j.get('company','')} · {j.get('location','')}</div>
                    <div style="color:#777;font-size:13px;margin-top:4px;">{j.get('salary_range','')}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:22px;font-weight:700;color:{score_color};">{j.get('match_score',0)}%</div>
                    <div style="font-size:11px;color:#999;">match</div>
                </div>
            </div>
            <div style="margin-top:8px;font-size:13px;color:#444;font-style:italic;">{j.get('why_matched','')}</div>
            <div style="margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
                {source_badge}
                <a href="{j.get('apply_url','#')}" style="background:#1a1a2e;color:#fff;padding:6px 14px;border-radius:6px;text-decoration:none;font-size:13px;">Apply →</a>
            </div>
        </div>"""

    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#f5f5f5;">
    <div style="background:#1a1a2e;color:#fff;padding:24px;border-radius:10px 10px 0 0;text-align:center;">
        <div style="font-size:24px;font-weight:700;">Career Copilot MY 🎯</div>
        <div style="margin-top:4px;opacity:0.8;">Your daily job matches</div>
    </div>
    <div style="background:#fff;padding:24px;border-radius:0 0 10px 10px;">
        <p>Hi <strong>{name}</strong>,</p>
        <p>Here are today's top job matches based on your <strong>{role}</strong> profile:</p>
        {cards}
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#999;font-size:12px;text-align:center;">
            You're receiving this because you subscribed to job alerts on Career Copilot MY.<br>
            <a href="#" style="color:#999;">Unsubscribe</a>
        </p>
    </div>
</body></html>"""

    subject = f"🎯 {len(all_jobs)} new jobs match your {role} profile — Career Copilot MY"
    return {"subject": subject, "html_body": html_body}


def _build_welcome_html(profile: dict, inbox_address: str) -> str:
    """Fallback welcome email when no job matches were found yet."""
    name = profile.get("full_name", "there")
    role = profile.get("current_role", "your field")
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"></head>
<body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px;background:#f5f5f5;">
    <div style="background:#1a1a2e;color:#fff;padding:24px;border-radius:10px 10px 0 0;text-align:center;">
        <div style="font-size:24px;font-weight:700;">Career Copilot MY 🎯</div>
        <div style="margin-top:4px;opacity:0.8;">Job Alert Subscription Confirmed</div>
    </div>
    <div style="background:#fff;padding:24px;border-radius:0 0 10px 10px;">
        <p>Hi <strong>{name}</strong>,</p>
        <p>You're now subscribed to job alerts for <strong>{role}</strong> roles.</p>
        <p>We'll email you every morning with fresh matching jobs from TheirStack and aidevboard.</p>
        <p style="color:#555;font-size:13px;">💡 <strong>Tip:</strong> Reply to any alert email to ask for different jobs —
        for example: <em>"Find me Django jobs in Penang"</em> or <em>"Show me remote-only roles"</em>.
        Our AI agent reads your replies and responds within minutes.</p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="color:#999;font-size:12px;text-align:center;">
            Reply to <a href="mailto:{inbox_address}">{inbox_address}</a> any time.<br>
            <a href="#" style="color:#999;">Unsubscribe</a>
        </p>
    </div>
</body></html>"""
