"""
Parser Agent — extracts structured profile from raw resume text.
Input : raw_text (str)
Output: ResumeProfile dict
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat, extract_tool_input

TOOL = {
    "name": "extract_resume",
    "description": "Extract structured information from a resume.",
    "input_schema": {
        "type": "object",
        "properties": {
            "full_name":       {"type": "string"},
            "email":           {"type": "string"},
            "phone":           {"type": "string"},
            "location":        {"type": "string", "description": "City / country"},
            "summary":         {"type": "string", "description": "2-3 sentence professional summary"},
            "years_experience":{"type": "number", "description": "Total years of work experience"},
            "current_role":    {"type": "string"},
            "skills":          {"type": "array", "items": {"type": "string"}, "description": "All technical + soft skills"},
            "education": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "degree":      {"type": "string"},
                        "institution": {"type": "string"},
                        "year":        {"type": "integer"},
                    },
                },
            },
            "experience": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title":        {"type": "string"},
                        "company":      {"type": "string"},
                        "duration_yrs": {"type": "number"},
                        "highlights":   {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
            "certifications": {"type": "array", "items": {"type": "string"}},
            "languages":      {"type": "array", "items": {"type": "string"}},
        },
        "required": ["full_name", "years_experience", "skills", "experience"],
    },
}

SYSTEM = (
    "You are a precise resume parser. Extract every piece of structured information "
    "from the provided resume text. Be thorough — capture all skills, roles, and education. "
    "Use the extract_resume tool to return your findings."
)


def run(raw_text: str) -> dict:
    response = chat(
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Parse this resume:\n\n{raw_text}"}],
        tools=[TOOL],
        tool_choice={"type": "tool", "name": "extract_resume"},
    )
    return extract_tool_input(response, "extract_resume")
