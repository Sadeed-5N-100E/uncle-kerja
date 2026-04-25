"""
Scorer Agent — scores a parsed resume against a job description.
Input : resume_profile (dict), job_description (str)
Output: ScoreReport dict
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat, extract_tool_input

TOOL = {
    "name": "score_resume",
    "description": (
        "Score a resume against a job description across multiple dimensions. "
        "Return a structured score report."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "overall_score": {
                "type": "integer",
                "description": "Weighted overall fit score 0-100",
            },
            "skills_score": {
                "type": "integer",
                "description": "Technical + soft skills match 0-100",
            },
            "experience_score": {
                "type": "integer",
                "description": "Years and relevance of experience match 0-100",
            },
            "education_score": {
                "type": "integer",
                "description": "Education requirements match 0-100",
            },
            "keyword_score": {
                "type": "integer",
                "description": "ATS keyword coverage score 0-100",
            },
            "matched_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Skills the candidate has that the job requires",
            },
            "missing_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Skills the job requires that the candidate lacks",
            },
            "bonus_skills": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Skills the candidate has beyond what the job requires",
            },
            "missing_keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "ATS keywords from the JD absent from the resume",
            },
            "experience_gap": {
                "type": "string",
                "description": "Specific experience mismatch, e.g. 'JD requires 5yr, candidate has 2yr'",
            },
            "verdict": {
                "type": "string",
                "enum": ["Strong Fit", "Good Fit", "Partial Fit", "Weak Fit", "Not a Fit"],
            },
            "one_line_summary": {
                "type": "string",
                "description": "One honest sentence about this application's chance",
            },
        },
        "required": [
            "overall_score", "skills_score", "experience_score", "education_score",
            "keyword_score", "matched_skills", "missing_skills", "missing_keywords",
            "verdict", "one_line_summary",
        ],
    },
}

SYSTEM = (
    "You are a senior technical recruiter with 15 years of experience at top-tier tech companies. "
    "You evaluate resumes with surgical precision. No sugar-coating — give honest, calibrated scores. "
    "Weight the overall score as: skills 40%, experience 35%, education 15%, keywords 10%. "
    "Use the score_resume tool to return your structured assessment."
)


def run(resume_profile: dict, job_description: str) -> dict:
    profile_text = _format_profile(resume_profile)
    response = chat(
        system=SYSTEM,
        messages=[
            {
                "role": "user",
                "content": (
                    f"JOB DESCRIPTION:\n{job_description}\n\n"
                    f"CANDIDATE PROFILE:\n{profile_text}\n\n"
                    "Score this candidate for the role."
                ),
            }
        ],
        tools=[TOOL],
        tool_choice={"type": "tool", "name": "score_resume"},
    )
    return extract_tool_input(response, "score_resume")


def _format_profile(p: dict) -> str:
    lines = [
        f"Name: {p.get('full_name', 'Unknown')}",
        f"Years Experience: {p.get('years_experience', 0)}",
        f"Current Role: {p.get('current_role', 'Unknown')}",
        f"Skills: {', '.join(p.get('skills', []))}",
        f"Education: {'; '.join(e.get('degree', '') + ' @ ' + e.get('institution', '') for e in p.get('education', []))}",
    ]
    for exp in p.get("experience", []):
        lines.append(
            f"- {exp.get('title')} at {exp.get('company')} ({exp.get('duration_yrs')} yrs): "
            + "; ".join(exp.get("highlights", [])[:3])
        )
    return "\n".join(lines)
