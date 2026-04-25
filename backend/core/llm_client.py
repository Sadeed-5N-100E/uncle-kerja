"""
LLM client — ILMU GLM-5.1 via Anthropic-compatible endpoint.
One retry on 504/503/502 with a 10-second wait. Fails fast after that.
"""
from __future__ import annotations
import time, logging
from typing import Any
import anthropic
from .config import ILMU_API_KEY, ILMU_BASE_URL, MODEL, MAX_TOKENS, TEMPERATURE

log = logging.getLogger(__name__)
_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=ILMU_API_KEY, base_url=ILMU_BASE_URL)
    return _client


def chat(
    messages: list[dict],
    system: str = "",
    tools: list[dict] | None = None,
    tool_choice: dict | None = None,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
) -> anthropic.types.Message:
    kwargs: dict[str, Any] = dict(
        model=MODEL,
        max_tokens=max_tokens,
        messages=messages,
        temperature=temperature,
    )
    if system:      kwargs["system"]      = system
    if tools:       kwargs["tools"]       = tools
    if tool_choice: kwargs["tool_choice"] = tool_choice

    for attempt in range(2):   # 1 try + 1 retry
        try:
            return get_client().messages.create(**kwargs)
        except anthropic.InternalServerError as e:
            status = getattr(e, "status_code", 0) or 0
            if attempt == 0 and status in (500, 502, 503, 504):
                log.warning(f"ILMU {status} — waiting 10s then one retry")
                time.sleep(10)
                continue
            raise
        except anthropic.APIConnectionError as e:
            if attempt == 0:
                log.warning(f"ILMU connection error — waiting 10s then one retry: {e}")
                time.sleep(10)
                continue
            raise

    raise RuntimeError("ILMU API unreachable after 2 attempts — server may be overloaded.")


def extract_text(message: anthropic.types.Message) -> str:
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


def extract_tool_input(message: anthropic.types.Message, tool_name: str) -> dict:
    for block in message.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input
    content_types = [getattr(b, "type", "?") for b in message.content]
    text_preview  = extract_text(message)[:120]
    raise RuntimeError(
        f"Tool '{tool_name}' not called. Got blocks={content_types}. "
        f"Text preview: {text_preview!r}"
    )
