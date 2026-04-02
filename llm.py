"""LLM integration supporting multiple providers (Ollama, Together AI)."""

from __future__ import annotations

import json
import os
from typing import Any, Dict

import requests

from config import OLLAMA_BASE_URL, OLLAMA_MODEL


LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")


# -----------------------------
# COMMON HELPERS
# -----------------------------
def _normalize_result(data: Dict[str, Any]) -> Dict[str, list]:
    keys = ["bugs", "missing_tests", "bad_practices", "risks", "suggestions"]
    normalized: Dict[str, list] = {}

    for key in keys:
        value = data.get(key, [])
        if isinstance(value, list):
            normalized[key] = [str(v).strip() for v in value if str(v).strip()]
        elif value:
            normalized[key] = [str(value).strip()]
        else:
            normalized[key] = []

    return normalized


def _build_prompt(diff_chunk: str) -> str:
    return f"""
You are a senior software engineer performing a rigorous PR review.

Follow this process:
1. Understand the change
2. Identify edge cases and risks
3. Suggest test coverage

Rules:
- Assume inputs are unsafe
- Always suggest tests if logic exists
- Avoid generic advice

Return STRICT JSON:

{{
  "bugs": [],
  "missing_tests": [],
  "bad_practices": [],
  "risks": [],
  "suggestions": []
}}

Git Diff:
{diff_chunk}
"""


# -----------------------------
# OLLAMA IMPLEMENTATION
# -----------------------------
def analyze_ollama(diff_chunk: str) -> Dict[str, list]:
    prompt = _build_prompt(diff_chunk)

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }

    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json=payload,
        timeout=120,
    )

    if response.status_code >= 300:
        raise RuntimeError(f"Ollama error: {response.text}")

    content = response.json().get("response", "")

    if not content.strip():
        return _normalize_result({})

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        return _normalize_result({})

    return _normalize_result(parsed)


# -----------------------------
# TOGETHER AI IMPLEMENTATION
# -----------------------------
def analyze_together(diff_chunk: str) -> Dict[str, list]:
    api_key = os.getenv("TOGETHER_API_KEY")
    if not api_key:
        raise RuntimeError("Missing TOGETHER_API_KEY")

    prompt = _build_prompt(diff_chunk)

    response = requests.post(
        "https://api.together.xyz/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": "Qwen/Qwen2-7B-Instruct",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0,
        },
        timeout=60,
    )

    if response.status_code >= 300:
        raise RuntimeError(f"Together AI error: {response.text}")

    content = response.json()["choices"][0]["message"]["content"]

    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        parsed = json.loads(content[start:end])
    except Exception:
        return _normalize_result({})

    return _normalize_result(parsed)


# -----------------------------
# MAIN ENTRY (ROUTER)
# -----------------------------
def analyze_diff(diff_chunk: str) -> Dict[str, list]:
    """Route to appropriate provider."""
    if LLM_PROVIDER == "ollama":
        return analyze_ollama(diff_chunk)

    elif LLM_PROVIDER == "together":
        return analyze_together(diff_chunk)

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {LLM_PROVIDER}")