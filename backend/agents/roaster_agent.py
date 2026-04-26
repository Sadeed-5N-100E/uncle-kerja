"""
Roaster Agent — generates a candid, witty critique of the resume.
Input : resume_profile (dict), score_report (dict), job_title (str)
Output: RoastReport dict

Uses Gemini JSON-mode to avoid function-calling schema issues.
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat_json

SYSTEM = """You are a frank and witty career advisor who delivers sharp, honest resume feedback.
Your feedback is specific and based on real skill gaps — never generic.
You focus on resume decisions, not the person. Tone: candid, dry, occasionally funny.
You always find one genuine strength alongside the honest critique.

Return a JSON object with exactly these fields:
{
  "opening_roast": "string — sharp one-liner summarising the resume's main issue",
  "skills_roast": "string — direct commentary on skill gaps for this specific role",
  "experience_roast": "string — honest assessment of experience vs what is needed",
  "formatting_roast": "string — commentary on resume presentation, keywords, structure",
  "silver_lining": "string — one genuine strength or positive aspect",
  "closing_line": "string — candid but encouraging closing remark",
  "emoji_rating": "string — 1 to 5 fire emojis e.g. 🔥🔥🔥"
}

Return ONLY the JSON object, no explanation.
"""


def run(resume_profile: dict, score_report: dict, job_title: str) -> dict:
    context = (
        f"Job applied for: {job_title}\n"
        f"Overall fit score: {score_report.get('overall_score')}/100\n"
        f"Verdict: {score_report.get('verdict')}\n"
        f"Missing skills: {', '.join(score_report.get('missing_skills', []))}\n"
        f"Matched skills: {', '.join(score_report.get('matched_skills', []))}\n"
        f"Experience gap: {score_report.get('experience_gap', 'None noted')}\n"
        f"Candidate: {resume_profile.get('full_name')}, "
        f"{resume_profile.get('years_experience')} years exp, "
        f"current role: {resume_profile.get('current_role')}"
    )
    result = chat_json(
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Give feedback on this resume:\n\n{context}"}],
    )
    result.setdefault("opening_roast", "")
    result.setdefault("emoji_rating", "🔥")
    return result
