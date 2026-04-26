"""
LLM client — Google Gemini 2.5 Flash via native REST API (active).

Agents call chat() / extract_text() / extract_tool_input() — interface unchanged.
The adapter converts Anthropic-style tool defs/tool_choice to Gemini format
and wraps the Gemini response back into Anthropic-compatible .content blocks.

To switch to ILMU GLM-5.1 when server is restored:
  1. Uncomment the ILMU block in config.py
  2. Set ILMU_API_KEY in .env
  3. Change chat() to call _chat_ilmu() instead of _chat_gemini()
"""
from __future__ import annotations
import logging
from types import SimpleNamespace
from typing import Any

import httpx
from .config import GEMINI_API_KEY, MODEL, MAX_TOKENS, TEMPERATURE

log = logging.getLogger(__name__)

GEMINI_REST_BASE = "https://generativelanguage.googleapis.com/v1beta/models"


# ── Format converters (Anthropic ↔ Gemini) ────────────────────────────────────

def _to_gemini_tools(tools: list[dict]) -> list[dict]:
    """Anthropic tool defs (input_schema) → Gemini function_declarations."""
    declarations = []
    for t in tools:
        schema = t.get("input_schema", t.get("parameters", {"type": "object", "properties": {}}))
        declarations.append({
            "name":        t["name"],
            "description": t.get("description", ""),
            "parameters":  schema,
        })
    return [{"function_declarations": declarations}]


def _to_gemini_tool_config(tc: dict | None, tools: list[dict] | None) -> dict | None:
    """Anthropic tool_choice → Gemini tool_config."""
    if not tc or not tools:
        return None
    if tc.get("type") == "tool":
        return {"function_calling_config": {
            "mode": "ANY",
            "allowed_function_names": [tc["name"]],
        }}
    return {"function_calling_config": {"mode": "AUTO"}}


def _to_gemini_messages(messages: list[dict]) -> list[dict]:
    result = []
    for m in messages:
        role    = "model" if m["role"] == "assistant" else "user"
        content = m["content"] or ""
        result.append({"role": role, "parts": [{"text": content}]})
    return result


def _to_anthropic_message(gemini_resp: dict) -> Any:
    """Wrap Gemini response so agents read .content[i].type/.input/.text."""
    blocks = []
    candidates = gemini_resp.get("candidates", [])
    if not candidates:
        return SimpleNamespace(content=blocks, stop_reason="error")

    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "text" in part:
            blocks.append(SimpleNamespace(type="text", text=part["text"]))
        if "functionCall" in part:
            fc = part["functionCall"]
            blocks.append(SimpleNamespace(
                type="tool_use",
                name=fc.get("name", ""),
                input=fc.get("args", {}),
            ))

    finish = candidates[0].get("finishReason", "")
    return SimpleNamespace(content=blocks, stop_reason=finish)


# ── Public API ────────────────────────────────────────────────────────────────

def chat(
    messages: list[dict],
    system: str = "",
    tools: list[dict] | None = None,
    tool_choice: dict | None = None,
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
) -> Any:
    """
    Call Gemini 2.5 Flash via native REST API.
    Returns an Anthropic-compatible message object so no agent files need to change.
    """
    url     = f"{GEMINI_REST_BASE}/{MODEL}:generateContent"
    payload: dict[str, Any] = {
        "contents":         _to_gemini_messages(messages),
        "generationConfig": {
            "maxOutputTokens": max_tokens,
            "temperature":     temperature,
        },
        # Reduce false-positive safety blocks on resume/career content (names,
        # addresses, phone numbers). Only block genuinely harmful content.
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ],
    }
    if system:
        payload["system_instruction"] = {"parts": [{"text": system}]}
    if tools:
        payload["tools"]      = _to_gemini_tools(tools)
        tool_cfg = _to_gemini_tool_config(tool_choice, tools)
        if tool_cfg:
            payload["tool_config"] = tool_cfg
        # Gemini requires temperature=0 for reliable forced function calling (ANY mode)
        if tool_choice and tool_choice.get("type") == "tool":
            payload["generationConfig"]["temperature"] = 0

    resp = httpx.post(
        url,
        params={"key": GEMINI_API_KEY},
        json=payload,
        timeout=90,
    )
    if resp.status_code != 200:
        err = resp.json().get("error", {})
        raise RuntimeError(
            f"Gemini API error {resp.status_code}: {err.get('message', resp.text[:200])}"
        )

    result = _to_anthropic_message(resp.json())

    # If we expected a tool call but got empty content for any reason (SAFETY,
    # RECITATION, PROHIBITED_CONTENT, SPII, OTHER, etc.), raise so the
    # orchestrator logs the actual stop_reason instead of a confusing tool error.
    if not result.content:
        raise RuntimeError(
            f"Gemini returned empty response. stop_reason={result.stop_reason!r}"
        )

    return result


def chat_json(
    messages: list[dict],
    system: str = "",
    max_tokens: int = MAX_TOKENS,
    temperature: float = TEMPERATURE,
) -> dict:
    """
    Call Gemini in JSON-mode (responseMimeType=application/json).
    Returns a parsed dict directly — no function-calling schema needed.
    Use this for agents where function calling causes MALFORMED_FUNCTION_CALL.
    """
    import json as _json
    url     = f"{GEMINI_REST_BASE}/{MODEL}:generateContent"
    payload: dict[str, Any] = {
        "contents":         _to_gemini_messages(messages),
        "generationConfig": {
            "maxOutputTokens":  max_tokens,
            "temperature":      temperature,
            "responseMimeType": "application/json",
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT",        "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH",       "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_ONLY_HIGH"},
        ],
    }
    if system:
        payload["system_instruction"] = {"parts": [{"text": system}]}

    resp = httpx.post(
        url,
        params={"key": GEMINI_API_KEY},
        json=payload,
        timeout=90,
    )
    if resp.status_code != 200:
        err = resp.json().get("error", {})
        raise RuntimeError(
            f"Gemini JSON-mode error {resp.status_code}: {err.get('message', resp.text[:200])}"
        )

    result = _to_anthropic_message(resp.json())
    if not result.content:
        raise RuntimeError(
            f"Gemini JSON-mode returned empty response. stop_reason={result.stop_reason!r}"
        )

    raw = extract_text(result)
    try:
        return _json.loads(raw)
    except _json.JSONDecodeError as e:
        raise RuntimeError(f"Gemini JSON-mode returned invalid JSON: {e}. Raw: {raw[:200]!r}")


def extract_text(message: Any) -> str:
    for block in message.content:
        if block.type == "text":
            return block.text
    return ""


def extract_tool_input(message: Any, tool_name: str) -> dict:
    for block in message.content:
        if block.type == "tool_use" and block.name == tool_name:
            return block.input
    content_types = [getattr(b, "type", "?") for b in message.content]
    text_preview  = extract_text(message)[:120]
    raise RuntimeError(
        f"Tool '{tool_name}' not called. Got blocks={content_types}. "
        f"Text preview: {text_preview!r}"
    )
