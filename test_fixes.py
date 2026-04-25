"""Quick test: only coach_agent + job_finder_agent (the two that failed)."""
import sys, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "backend")

PROFILE = {
    "full_name": "Ali Hassan", "years_experience": 2, "current_role": "Junior Software Developer",
    "location": "Kuala Lumpur, Malaysia",
    "skills": ["Python", "Django", "SQL", "PostgreSQL", "HTML", "CSS", "JavaScript", "Git", "REST APIs", "Linux"],
    "education": [{"degree": "BSc Computer Science", "institution": "Universiti Malaya", "year": 2022}],
    "experience": [{"title": "Junior Software Developer", "company": "TechSprint Sdn Bhd", "duration_yrs": 1.5, "highlights": ["Built Django CRUD apps", "SQL reporting"]}],
}
SCORE = {
    "overall_score": 64, "verdict": "Partial Fit",
    "matched_skills": ["Python", "Django", "PostgreSQL", "REST APIs", "SQL"],
    "missing_skills": ["Docker", "Redis", "CI/CD", "AWS"],
    "missing_keywords": ["Docker", "Redis", "CI/CD", "AWS"],
    "experience_gap": "2yr vs 2-4yr required",
    "one_line_summary": "Good Python/Django core but missing Docker and cloud basics.",
}

print("=" * 55)
print("TEST: coach_agent")
print("=" * 55)
import time
from agents import coach_agent
t0 = time.time()
try:
    plan = coach_agent.run(SCORE, PROFILE)
    print(f"  OK in {time.time()-t0:.1f}s")
    print(f"  quick_wins    : {plan.get('quick_wins')}")
    print(f"  timeline_weeks: {plan.get('timeline_weeks')}")
    print(f"  top action    : {(plan.get('priority_actions') or [{}])[0].get('action')}")
except Exception as e:
    print(f"  FAIL: {e}")

print()
print("=" * 55)
print("TEST: job_finder_agent")
print("=" * 55)
from agents import job_finder_agent
t0 = time.time()
try:
    jobs = job_finder_agent.run(PROFILE, SCORE)
    print(f"  OK in {time.time()-t0:.1f}s")
    print(f"  local_jobs : {len(jobs.get('local_jobs', []))}")
    for j in jobs.get("local_jobs", [])[:2]:
        print(f"    [{j.get('match_score')}%] {j.get('title')} @ {j.get('company')} | {j.get('salary_range')}")
    print(f"  remote_jobs: {len(jobs.get('remote_jobs', []))}")
    for j in jobs.get("remote_jobs", []):
        print(f"    {j.get('title')} @ {j.get('company')}")
except Exception as e:
    print(f"  FAIL: {e}")

print()
print("DONE")
