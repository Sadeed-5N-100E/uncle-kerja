"""
Coach Agent — turns a score report into a concrete improvement plan.
Input : ScoreReport dict, ResumeProfile dict
Output: ActionPlan dict

Uses Gemini JSON-mode to avoid function-calling schema issues with nested arrays.
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat_json

SYSTEM = """You are a senior career coach. Give direct, practical advice with no filler.
Every action item must be specific — name the exact skill, course, or tool.
Prioritise by impact-to-effort ratio: high impact + low effort = rank 1.
Resources must be free or widely available (Coursera free audit, freeCodeCamp, official docs).

Return a JSON object with exactly these fields:
{
  "priority_actions": [
    {
      "rank": 1,
      "category": "skill|experience|keyword|format|network",
      "action": "specific actionable step",
      "effort": "days|weeks|months",
      "impact": "low|medium|high|critical",
      "resources": ["free course or tool name"]
    }
  ],
  "resume_rewrites": [
    {
      "section": "section name",
      "issue": "what is wrong",
      "improved": "rewritten version with action verbs and quantification"
    }
  ],
  "quick_wins": ["thing to fix today in under 30 minutes"],
  "timeline_weeks": 8,
  "motivational_close": "one honest encouraging sentence"
}

Include 3-5 priority_actions, 1-3 resume_rewrites, 3 quick_wins.
Return ONLY the JSON object, no explanation.
"""


def run(score_report: dict, resume_profile: dict) -> dict:
    context = (
        f"Candidate: {resume_profile.get('full_name')}, "
        f"{resume_profile.get('years_experience')} yrs exp, "
        f"current role: {resume_profile.get('current_role')}\n"
        f"Skills: {', '.join(resume_profile.get('skills', []))}\n\n"
        f"Score: {score_report.get('overall_score')}/100 — {score_report.get('verdict')}\n"
        f"Missing skills: {', '.join(score_report.get('missing_skills', []))}\n"
        f"Missing keywords: {', '.join(score_report.get('missing_keywords', []))}\n"
        f"Experience gap: {score_report.get('experience_gap', 'None')}\n"
        f"Summary: {score_report.get('one_line_summary')}"
    )
    result = chat_json(
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Build an improvement plan:\n\n{context}"}],
    )
    result.setdefault("priority_actions", [])
    result.setdefault("resume_rewrites", [])
    result.setdefault("quick_wins", [])
    result.setdefault("timeline_weeks", 8)
    result.setdefault("motivational_close", "")
    return result
