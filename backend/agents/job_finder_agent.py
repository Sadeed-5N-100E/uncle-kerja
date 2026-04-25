"""
Job Finder Agent — three-layer job search, zero LLM calls.

Layer 1  SerpAPI Google Jobs (primary, free quota, real-time Google results)
  Query: "{role} {top_skills}" location=Malaysia
  Returns real job URLs from Google Jobs aggregator.

Layer 2  aidevboard (free, 100 req/hr — AI/tech remote roles)
  Good fallback for tech-specific positions.

Layer 3  TheirStack (backup, 1 credit/result — use sparingly, max 3/call)
  Only used when layers 1+2 return < 3 results combined.
"""
from __future__ import annotations
import os, sys, logging
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

import httpx
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parents[2] / ".env")
log = logging.getLogger(__name__)

SERPAPI_KEY     = os.getenv("SERPAPI_KEY", "")
THEIRSTACK_KEY  = os.getenv("THEIRSTACK_API_KEY", "")
SERPAPI_BASE    = "https://serpapi.com/search"
THEIRSTACK_BASE = "https://api.theirstack.com/v1"
AIDEVBOARD_BASE = "https://aidevboard.com/api/v1"

_SLUG_MAP = {
    "rest apis": "rest", "rest api": "rest", "postgresql": "postgresql",
    "node.js": "node-js", "vue.js": "vue-js", "react.js": "react",
    "c#": "csharp", "c++": "cplusplus", ".net": "dotnet",
    "machine learning": "machine-learning", "deep learning": "deep-learning",
    "ci/cd": "github-actions", "linux basics": "linux",
}

def _to_slugs(skills: list[str]) -> list[str]:
    slugs = []
    for s in skills:
        key  = s.lower().strip()
        slug = _SLUG_MAP.get(key, key.replace(" ", "-").replace("/", "-").replace(".", ""))
        slugs.append(slug)
    return list(dict.fromkeys(slugs))

def _skill_overlap(candidate: list[str], job_techs: list[str]) -> tuple[int, list[str]]:
    c_lower = {s.lower().replace(" ", "") for s in candidate}
    matched = [t for t in job_techs
               if t.lower().replace("-","") in c_lower or
               any(c in t.lower() or t.lower() in c for c in c_lower)]
    return len(matched), matched

def _score(overlap: int, total: int) -> int:
    base = min(int(overlap / max(total, 1) * 100), 95)
    return max(base, 30)

def _salary_from_usd(lo, hi) -> str:
    if not lo: return "Not specified"
    myr_lo = int((lo / 12) * 4.7 / 100) * 100
    myr_hi = int((hi / 12) * 4.7 / 100) * 100 if hi else myr_lo * 2
    return f"RM{myr_lo:,}–RM{myr_hi:,}/month"


# ── Layer 1: SerpAPI Google Jobs ──────────────────────────────────────────────

def _fetch_serpapi(skills: list[str], role: str, years: float) -> list[dict]:
    if not SERPAPI_KEY:
        log.warning("SERPAPI_KEY not set, skipping Google Jobs")
        return []

    # Build a natural-language query
    top_skills = ", ".join(skills[:3]) if skills else role
    seniority  = "senior" if years >= 5 else "junior" if years < 2 else ""
    query      = f"{seniority} {role} {top_skills}".strip()

    try:
        resp = httpx.get(
            SERPAPI_BASE,
            params={
                "engine":    "google_jobs",
                "q":         query,
                "location":  "Malaysia",
                "gl":        "my",
                "hl":        "en",
                "num":       10,
                "api_key":   SERPAPI_KEY,
            },
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log.error(f"SerpAPI error: {e}")
        return []

    results = []
    for j in data.get("jobs_results", []):
        # Extract apply URL
        apply_options = j.get("apply_options") or []
        apply_url     = apply_options[0].get("link", "") if apply_options else ""

        # Extract extensions
        ext     = j.get("detected_extensions") or {}
        posted  = ext.get("posted_at", "")
        salary  = j.get("salary") or ext.get("salary") or "Not specified"

        # Guess skill overlap from description
        desc      = (j.get("description") or "").lower()
        overlap   = sum(1 for s in skills if s.lower() in desc)

        results.append({
            "title":         j.get("title", ""),
            "company":       j.get("company_name", ""),
            "location":      j.get("location", "Malaysia"),
            "salary_range":  salary,
            "match_score":   min(40 + overlap * 8, 92),
            "matched_skills": [s for s in skills if s.lower() in desc][:4],
            "why_matched":   f"Found via Google Jobs · {overlap} skill matches in description",
            "requirements":  [],
            "apply_url":     apply_url,
            "source":        "serpapi",
            "posted":        posted,
        })

    results.sort(key=lambda x: -x["match_score"])
    return results[:5]


# ── Layer 2: aidevboard (AI/tech remote) ─────────────────────────────────────

def _fetch_aidevboard(skills: list[str], limit: int = 20) -> list[dict]:
    tags = ",".join(_to_slugs(skills[:6]))
    try:
        resp = httpx.get(
            f"{AIDEVBOARD_BASE}/jobs",
            params={"tags": tags, "limit": limit},
            headers={"User-Agent": "CareerCopilotMY/1.0"},
            timeout=10,
        )
        resp.raise_for_status()
        jobs = resp.json().get("jobs", [])
    except Exception as e:
        log.error(f"aidevboard error: {e}")
        return []

    results = []
    for j in jobs:
        job_tags = j.get("tags") or []
        overlap, matched = _skill_overlap(skills, job_tags)
        if overlap < 1:
            continue
        sal_min = j.get("salary_min")
        sal_max = j.get("salary_max")
        sal_str = f"${sal_min:,}–${sal_max:,}/yr" if sal_min else "Not specified"
        results.append({
            "title":         j.get("title", ""),
            "company":       j.get("company_name", ""),
            "location":      j.get("location") or "Remote",
            "salary_range":  sal_str,
            "match_score":   _score(overlap, len(job_tags) or 4),
            "matched_skills": matched[:4],
            "why_matched":   f"AI/tech role — {overlap} matching skills",
            "requirements":  job_tags[:5],
            "apply_url":     j.get("url", ""),
            "source":        "aidevboard",
            "posted":        (j.get("published_at") or "")[:10],
        })

    results.sort(key=lambda x: -x["match_score"])
    return results[:3]


# ── Layer 3: TheirStack (sparingly) ──────────────────────────────────────────

def _fetch_theirstack(skills: list[str], years: float, limit: int = 3) -> list[dict]:
    if not THEIRSTACK_KEY:
        return []
    slugs      = _to_slugs(skills[:6])
    seniority  = "senior" if years >= 5 else "mid" if years >= 2 else "junior"
    title_map  = {
        "junior": ["junior", "associate", "graduate"],
        "mid":    ["software engineer", "developer", "backend"],
        "senior": ["senior", "lead", "principal"],
    }
    body: dict = {
        "job_title_or":           title_map.get(seniority, ["developer"]),
        "job_country_code_or":    ["MY"],
        "posted_at_max_age_days": 60,
        "limit":                  limit,
        "page":                   0,
    }
    if slugs:
        body["job_technology_slug_or"] = slugs[:5]

    def _do(b):
        r = httpx.post(
            f"{THEIRSTACK_BASE}/jobs/search",
            headers={"Authorization": f"Bearer {THEIRSTACK_KEY}", "Content-Type": "application/json"},
            json=b, timeout=15,
        )
        r.raise_for_status()
        return r.json()

    try:
        data = _do(body)
        if not data.get("data") and "job_technology_slug_or" in body:
            fb = {k: v for k, v in body.items() if k != "job_technology_slug_or"}
            data = _do(fb)
    except Exception as e:
        log.error(f"TheirStack error: {e}")
        return []

    results = []
    for j in data.get("data", []):
        techs    = j.get("technology_slugs") or []
        overlap, matched = _skill_overlap(skills, techs)
        company  = (j.get("company_object") or {}).get("name", j.get("company_domain", "Unknown"))
        sal      = j.get("salary_string") or _salary_from_usd(
            j.get("min_annual_salary_usd"), j.get("max_annual_salary_usd"))
        results.append({
            "title":         j.get("job_title", ""),
            "company":       company,
            "location":      j.get("location") or "Malaysia",
            "salary_range":  sal,
            "match_score":   _score(overlap, len(techs) or 5),
            "matched_skills": matched[:4],
            "why_matched":   f"Malaysian listing — {overlap} tech matches",
            "requirements":  list(set(techs[:5])),
            "apply_url":     j.get("url", ""),
            "source":        "theirstack",
            "posted":        j.get("date_posted", ""),
        })
    return results


# ── Public entry point ────────────────────────────────────────────────────────

def run(resume_profile: dict, score_report: dict) -> dict:
    skills = resume_profile.get("skills", [])
    role   = resume_profile.get("current_role") or "Software Developer"
    years  = resume_profile.get("years_experience", 0)

    extra  = score_report.get("matched_skills", [])
    all_sk = list(dict.fromkeys(skills + extra))

    # Layer 1: SerpAPI (primary)
    local_jobs = _fetch_serpapi(all_sk, role, years)

    # Layer 2: aidevboard (always run for remote/AI jobs)
    remote_jobs = _fetch_aidevboard(all_sk)

    # Layer 3: TheirStack only if SerpAPI returned < 3 local results
    if len(local_jobs) < 3:
        log.info(f"SerpAPI returned {len(local_jobs)} results, supplementing with TheirStack (max 3 credits)")
        ts = _fetch_theirstack(all_sk, years, limit=3)
        # Merge, de-duplicate by title+company
        seen = {(j["title"].lower(), j["company"].lower()) for j in local_jobs}
        for j in ts:
            key = (j["title"].lower(), j["company"].lower())
            if key not in seen:
                local_jobs.append(j)
                seen.add(key)

    local_jobs.sort(key=lambda x: -x["match_score"])
    return {"local_jobs": local_jobs[:5], "remote_jobs": remote_jobs}
