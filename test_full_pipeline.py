"""
Full 6-agent pipeline test: parser → scorer+jobs (parallel) → roaster+coach (parallel)
Run from: career-copilot-my/
  python test_full_pipeline.py
"""
import sys, json, time
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "backend")

from agents.orchestrator import run_pipeline

RESUME = """
Ali Hassan
ali.hassan@gmail.com | +60-12-345-6789 | Kuala Lumpur, Malaysia

SUMMARY
Software developer with 2 years of experience in Python/Django web apps.

SKILLS
Python, Django, SQL, PostgreSQL, HTML, CSS, JavaScript, Git, REST APIs, Linux

EXPERIENCE
Junior Software Developer | TechSprint Sdn Bhd | Jan 2023 - Present (1.5 years)
- Built 3 internal CRUD apps with Django
- Wrote SQL reports for the business team
- Maintained a Django REST API

Software Developer Intern | MyDigital Startup | Jun-Dec 2022 (6 months)
- Built Django e-commerce backend
- Learned Git workflows

EDUCATION
BSc Computer Science | Universiti Malaya | 2022 | CGPA 3.4
"""

JOB_DESCRIPTION = """
Mid-level Python Developer — Shopee Malaysia (Kuala Lumpur)

We are looking for a Python Developer to join our platform team.

Requirements:
- 2-4 years Python experience
- Django or FastAPI (either is fine)
- PostgreSQL or MySQL
- Basic Docker knowledge
- RESTful API design
- Team player, good communicator

Nice to have:
- Redis basics
- CI/CD experience
- AWS basics
"""

def progress(step, pct):
    print(f"  [{pct:3d}%] {step}")

def banner(title):
    print()
    print("=" * 65)
    print(f"  {title}")
    print("=" * 65)

start = time.time()
banner("FULL PIPELINE — START")
session = run_pipeline(
    resume_text=RESUME,
    job_description=JOB_DESCRIPTION,
    alert_email=None,      # no email during test
    progress_cb=progress,
)
total = time.time() - start

banner("RESULTS")
print(f"  Status        : {session['status']}")
print(f"  Session ID    : {session['session_id']}")
print(f"  Timings       : {session['timings']}")
print(f"  Total wall    : {total:.1f}s")
print(f"  Errors        : {session['errors'] or 'none'}")

banner("PROFILE")
p = session.get("profile", {})
print(f"  Name          : {p.get('full_name')}")
print(f"  Years exp     : {p.get('years_experience')}")
print(f"  Skills        : {', '.join(p.get('skills', []))}")

banner("SCORE REPORT")
s = session.get("score", {})
print(f"  Overall       : {s.get('overall_score')}/100")
print(f"  Verdict       : {s.get('verdict')}")
print(f"  Matched skills: {s.get('matched_skills')}")
print(f"  Missing skills: {s.get('missing_skills')}")
print(f"  Summary       : {s.get('one_line_summary')}")

banner("ROAST")
r = session.get("roast", {})
print(f"  {r.get('emoji_rating')}")
print(f"  Opening  : {r.get('opening_roast')}")
print(f"  Closing  : {r.get('closing_line')}")

banner("ACTION PLAN")
ap = session.get("action_plan", {})
print(f"  Quick wins    : {ap.get('quick_wins')}")
print(f"  Timeline      : {ap.get('timeline_weeks')} weeks")
print(f"  Top actions:")
for a in (ap.get("priority_actions") or [])[:3]:
    print(f"    [{a.get('rank')}] {a.get('action')} ({a.get('effort')}, {a.get('impact')} impact)")

banner("JOB MATCHES")
jobs = session.get("jobs", {})
print(f"  Local (AI curated) : {len(jobs.get('local_jobs', []))} jobs")
for j in jobs.get("local_jobs", [])[:3]:
    print(f"    [{j.get('match_score')}%] {j.get('title')} @ {j.get('company')} | {j.get('salary_range')}")
    print(f"         {j.get('why_matched')}")
print(f"  Remote (live)      : {len(jobs.get('remote_jobs', []))} jobs")
for j in jobs.get("remote_jobs", []):
    print(f"    {j.get('title')} @ {j.get('company')} | {j.get('location')}")

banner("DONE")
print(f"  Wall clock: {total:.1f}s (parallel steps visible in timings above)")
