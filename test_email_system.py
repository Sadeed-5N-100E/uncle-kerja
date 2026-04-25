"""
Test the full AgentMail integration:
  1. Send a real job alert email to tomleeatwork@gmail.com
  2. Read the inbox to confirm sent items
  3. Check pending replies (inbound messages we haven't replied to yet)

Run from: career-copilot-my/
  python test_email_system.py
"""
import sys, json, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "backend")

from core import mailer
from agents.email_agent import build_job_alert_html

PROFILE = {
    "full_name": "Ali Hassan",
    "current_role": "Junior Software Developer",
    "skills": ["Python", "Django", "SQL", "PostgreSQL", "Git"],
}
JOBS = [
    {"title": "Junior Backend Developer",  "company": "Shopee",          "location": "Kuala Lumpur", "salary_range": "RM4,000-RM6,000/month",  "match_score": 82, "why_matched": "Strong Python/Django match.",           "apply_url": "https://careers.shopee.com.my", "source": "ai_curated"},
    {"title": "Software Developer",        "company": "Revenue Monster",  "location": "Petaling Jaya","salary_range": "RM3,500-RM5,500/month",  "match_score": 85, "why_matched": "Near-perfect Django + PostgreSQL fit.", "apply_url": "https://revenuemonster.my/careers", "source": "ai_curated"},
    {"title": "Backend Engineer",          "company": "TNG Digital",      "location": "Kuala Lumpur", "salary_range": "RM3,800-RM5,500/month",  "match_score": 75, "why_matched": "Python REST APIs core to e-wallet.",    "apply_url": "https://tngdigital.com.my/careers", "source": "ai_curated"},
    {"title": "Python Developer (Remote)", "company": "Sanctuary Computer","location": "Remote (Asia)","salary_range": "Not specified",          "match_score": 55, "why_matched": "2+ yrs Python + REST APIs match.",      "apply_url": "https://sanctuary.computer",        "source": "remotive_live"},
]

print("=" * 60)
print("TEST 1: AgentMail configured?")
print("=" * 60)
print(f"  configured : {mailer.is_configured()}")
print(f"  inbox      : {mailer.inbox_address()}")

print()
print("=" * 60)
print("TEST 2: Send job alert email")
print("=" * 60)
alert = build_job_alert_html(PROFILE, JOBS)
print(f"  Subject: {alert['subject']}")
result = mailer.send(
    to="tomleeatwork@gmail.com",
    subject=alert["subject"],
    html_body=alert["html_body"],
)
if result:
    print(f"  SENT  message_id={result.get('message_id','?')[:40]}...")
    print(f"        thread_id ={result.get('thread_id','?')}")
else:
    print("  FAIL")

print()
print("=" * 60)
print("TEST 3: Read inbox messages (last 5)")
print("=" * 60)
msgs = mailer.list_unread_messages(limit=5)
print(f"  {len(msgs)} message(s) in inbox")
for m in msgs:
    print(f"  [{m.get('created_at','')[:19]}] from={m.get('from','')} subject={m.get('subject','')!r}")
    labels = m.get("labels") or []
    if labels:
        print(f"    labels={labels}")

print()
print("=" * 60)
print("TEST 4: Pending replies (inbound not yet processed)")
print("=" * 60)
pending = mailer.list_pending_replies()
print(f"  {len(pending)} pending reply(ies)")
for m in pending:
    print(f"  from={m.get('from','')} subject={m.get('subject','')!r}")

print()
print("DONE")
