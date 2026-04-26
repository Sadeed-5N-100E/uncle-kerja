"""
Parser Agent — extracts structured profile from raw resume text.
Input : raw_text (str)
Output: ResumeProfile dict

Uses Gemini JSON-mode (not function calling) to avoid MALFORMED_FUNCTION_CALL
on complex nested schemas.
"""
from __future__ import annotations
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parents[1]))

from core.llm_client import chat_json

SYSTEM = """You are a precise resume parser. Extract structured information from the resume text provided.

Return a JSON object with exactly these fields:
{
  "full_name": "string",
  "email": "string",
  "phone": "string",
  "location": "string (city/country)",
  "summary": "string (2-3 sentence professional summary)",
  "years_experience": integer,
  "current_role": "string (most recent job title)",
  "skills": ["skill1", "skill2", ...],
  "education": ["Degree @ Institution, Year", ...],
  "experience": ["Job Title at Company (N yrs): key achievements", ...],
  "certifications": ["cert1", "cert2", ...]
}

Rules:
- years_experience must be an integer (round to nearest whole number)
- skills must include ALL technical tools, languages, frameworks, and soft skills mentioned
- experience entries must each be a single descriptive string
- If a field has no data, use an empty string or empty array
- Return ONLY the JSON object, no explanation
"""


def run(raw_text: str) -> dict:
    result = chat_json(
        system=SYSTEM,
        messages=[{"role": "user", "content": f"Parse this resume:\n\n{raw_text}"}],
    )
    # Ensure required fields exist with defaults
    result.setdefault("full_name", "Unknown")
    result.setdefault("years_experience", 0)
    result.setdefault("skills", [])
    result.setdefault("experience", [])
    result.setdefault("education", [])
    result.setdefault("certifications", [])
    return result
