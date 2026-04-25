"""
Roaster Agent — generates a brutally honest, funny critique of the resume
given the score report.
Input : resume_profile (dict), score_report (dict), job_title (str)
Output: RoastReport dict
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat, extract_tool_input

TOOL = {
    "name": "roast_resume",
    "description": "Generate a structured, brutally funny roast of a resume.",
    "input_schema": {
        "type": "object",
        "properties": {
            "opening_roast": {
                "type": "string",
                "description": "A savage one-liner opening that lands like a punchline",
            },
            "skills_roast": {
                "type": "string",
                "description": "Brutal commentary on their skill gaps for this specific role",
            },
            "experience_roast": {
                "type": "string",
                "description": "Honest take on their experience level vs what's needed",
            },
            "formatting_roast": {
                "type": "string",
                "description": "Commentary on resume presentation, keywords, structure",
            },
            "silver_lining": {
                "type": "string",
                "description": "One genuine strength, delivered with backhanded warmth",
            },
            "closing_line": {
                "type": "string",
                "description": "A memorable closing line — brutal but not cruel",
            },
            "emoji_rating": {
                "type": "string",
                "description": "Rate the resume with 1-5 fire emojis (e.g. 🔥🔥)",
            },
        },
        "required": [
            "opening_roast", "skills_roast", "experience_roast",
            "formatting_roast", "silver_lining", "closing_line", "emoji_rating",
        ],
    },
}

SYSTEM = (
    "You are a career roast comedian — part Simon Cowell, part Gordon Ramsay, part LinkedIn influencer gone rogue. "
    "Your roasts are specific, witty, and based on real gaps. You NEVER punch down cruelly — "
    "you roast the resume choices, not the person. Your tone: sharp, funny, honest. "
    "Reference specific skills, companies, or gaps from the actual resume. No generic filler. "
    "Use the roast_resume tool to deliver your structured roast."
)


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
    response = chat(
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": f"Roast this resume:\n\n{context}",
            }
        ],
        tools=[TOOL],
        tool_choice={"type": "tool", "name": "roast_resume"},
        temperature=0.8,
    )
    return extract_tool_input(response, "roast_resume")
