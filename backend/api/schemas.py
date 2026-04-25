from pydantic import BaseModel, EmailStr
from typing import Optional


class AnalyzeRequest(BaseModel):
    job_description: str
    alert_email: Optional[str] = None
    # resume text is sent as a multipart file OR as plain text
    resume_text: Optional[str] = None  # fallback if no PDF uploaded


class AlertSubscribeRequest(BaseModel):
    session_id: str
    email: str


class CoverLetterRequest(BaseModel):
    session_id: str
    job_index: int = 0
