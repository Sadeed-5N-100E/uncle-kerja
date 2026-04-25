import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parents[2] / ".env")

# ── Active LLM: ILMU GLM-5.1 ─────────────────────────────────────────────────
ILMU_API_KEY    = os.getenv("ILMU_API_KEY", "sk-1191e2085cba6ce60e49fccafbb97240e3b36dfcc0014908")
ILMU_BASE_URL   = os.getenv("ILMU_BASE_URL", "https://api.ilmu.ai/anthropic")
MODEL           = os.getenv("ILMU_MODEL", "ilmu-glm-5.1")
MAX_TOKENS      = 2048
TEMPERATURE     = 0.3

# ── AgentMail ─────────────────────────────────────────────────────────────────
AGENTMAIL_API_KEY  = os.getenv("AGENTMAIL_API_KEY", "")
AGENTMAIL_INBOX_ID = os.getenv("AGENTMAIL_INBOX_ID", "usm.z.ai@agentmail.to")
AGENTMAIL_BASE_URL = "https://api.agentmail.to"
