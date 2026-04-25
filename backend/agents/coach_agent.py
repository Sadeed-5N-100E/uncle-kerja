"""
Coach Agent — turns a score report into a concrete, ranked improvement plan.
Input : ScoreReport dict, ResumeProfile dict
Output: ActionPlan dict
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat, extract_tool_input

TOOL = {
    "name": "build_action_plan",
    "description": "Build a concrete, prioritised action plan to improve a candidate's job fit.",
    "input_schema": {
        "type": "object",
        "properties": {
            "priority_actions": {
                "type": "array",
                "description": "Top 5 actions ranked by impact/effort ratio",
                "items": {
                    "type": "object",
                    "properties": {
                        "rank":        {"type": "integer"},
                        "category":    {"type": "string", "enum": ["skill", "experience", "keyword", "format", "network"]},
                        "action":      {"type": "string", "description": "Specific, actionable step"},
                        "effort":      {"type": "string", "enum": ["1-2 days", "1-2 weeks", "1-3 months", "3-6 months"]},
                        "impact":      {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                        "resources":   {"type": "array", "items": {"type": "string"}, "description": "Free courses, tools, or links"},
                    },
                    "required": ["rank", "category", "action", "effort", "impact"],
                },
            },
            "resume_rewrites": {
                "type": "array",
                "description": "Specific resume sections to rewrite with before/after examples",
                "items": {
                    "type": "object",
                    "properties": {
                        "section":  {"type": "string"},
                        "issue":    {"type": "string"},
                        "improved": {"type": "string", "description": "Rewritten version using strong action verbs and quantification"},
                    },
                    "required": ["section", "issue", "improved"],
                },
            },
            "quick_wins": {
                "type": "array",
                "items": {"type": "string"},
                "description": "3 things the candidate can fix in their resume TODAY (< 30 mins)",
            },
            "timeline_weeks": {
                "type": "integer",
                "description": "Realistic weeks to become competitive for this role if all actions completed",
            },
            "motivational_close": {
                "type": "string",
                "description": "One honest, encouraging sentence about the path forward",
            },
        },
        "required": ["priority_actions", "resume_rewrites", "quick_wins", "timeline_weeks", "motivational_close"],
    },
}

SYSTEM = (
    "You are a senior career coach and ex-FAANG recruiter. "
    "You give brutally practical advice — no fluff, no participation trophies. "
    "Every action item must be specific (name the exact skill, course, or tool). "
    "Prioritise by impact-to-effort ratio: high impact + low effort = rank 1. "
    "Resources must be free or widely available (Coursera free audit, freeCodeCamp, official docs). "
    "Use the build_action_plan tool to return your structured plan."
)


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
    response = chat(
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Build an action plan:\n\n{context}"}],
        tools=[TOOL],
        tool_choice={"type": "tool", "name": "build_action_plan"},
    )
    return extract_tool_input(response, "build_action_plan")
