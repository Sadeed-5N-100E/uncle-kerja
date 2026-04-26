import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env", override=True)

# ── Active LLM: Google Gemini 2.5 Flash ──────────────────────────────────────
GEMINI_API_KEY  = os.getenv("GEMINI_API_KEY", "")
MODEL           = "gemini-2.5-flash"
MAX_TOKENS      = 2048
TEMPERATURE     = 0.3

# ── ILMU GLM-5.1 (restore when server is back) ───────────────────────────────
ILMU_API_KEY  = os.getenv("ILMU_API_KEY", "")
ILMU_BASE_URL = os.getenv("ILMU_BASE_URL", "https://api.ilmu.ai/anthropic")

# ── AgentMail ─────────────────────────────────────────────────────────────────
AGENTMAIL_API_KEY  = os.getenv("AGENTMAIL_API_KEY", "")
AGENTMAIL_INBOX_ID = os.getenv("AGENTMAIL_INBOX_ID", "usm.z.ai@agentmail.to")
AGENTMAIL_BASE_URL = "https://api.agentmail.to"
