"""
Thin wrapper around the ILMU Anthropic-compatible endpoint.

Includes automatic retry with exponential backoff for transient 5xx errors
(504 Gateway Timeout is common when the ILMU API is under load at hackathons).
"""
from __future__ import annotations
import time, logging
from typing import Any
import anthropic
from .config import ILMU_API_KEY, ILMU_BASE_URL, MODEL, MAX_TOKENS, TEMPERATURE

log = logging.getLogger(__name__)

_client: anthropic.Anthropic | None = None

# Retry config: 3 attempts, delays 5s → 15s → 30s
_RETRY_DELAYS = [5, 15, 30]
# 5xx HTTP codes that are safe to retry
_RETRYABLE_STATUS = {500, 502, 503, 504, 529}


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

    last_exc: Exception | None = None

    for attempt, delay in enumerate([0] + _RETRY_DELAYS, start=1):
        if delay:
            log.warning(f"ILMU API retry {attempt}/{len(_RETRY_DELAYS)+1} after {delay}s (previous: {last_exc})")
            time.sleep(delay)
        try:
            return get_client().messages.create(**kwargs)
        except anthropic.InternalServerError as e:
            # 504 / 503 / 500 — server-side, retryable
            status = getattr(e, "status_code", 0) or 0
            if status in _RETRYABLE_STATUS or "504" in str(e) or "502" in str(e) or "503" in str(e):
                last_exc = e
                log.warning(f"ILMU API {status} on attempt {attempt}: {str(e)[:120]}")
                continue
            raise  # non-retryable server error
        except anthropic.APIConnectionError as e:
            # Network-level timeout — retryable
            last_exc = e
            log.warning(f"ILMU connection error on attempt {attempt}: {e}")
            continue
        except anthropic.RateLimitError as e:
            # 429 — back off longer
            last_exc = e
            backoff = min(delay * 2, 60)
            log.warning(f"ILMU rate limit on attempt {attempt}, sleeping {backoff}s")
            time.sleep(backoff)
            continue

    # All retries exhausted
    raise RuntimeError(
        f"ILMU API failed after {len(_RETRY_DELAYS)+1} attempts. "
        f"Last error: {last_exc}. "
        "This is a temporary server overload — please try again in a minute."
    ) from last_exc


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
