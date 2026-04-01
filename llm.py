"""Ollama integration for diff analysis."""

from __future__ import annotations

import json
import re
from typing import Any, Dict

import requests

from config import OLLAMA_BASE_URL, OLLAMA_MODEL


def _extract_json(text: str) -> Dict[str, Any]:
    """Extract JSON safely from model output."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return {}
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return {}


def _normalize_result(data: Dict[str, Any]) -> Dict[str, list]:
    keys = ["bugs", "missing_tests", "bad_practices", "risks", "suggestions"]
    normalized = {}

    for key in keys:
        value = data.get(key, [])
        if isinstance(value, list):
            normalized[key] = [str(v).strip() for v in value if str(v).strip()]
        elif value:
            normalized[key] = [str(value).strip()]
        else:
            normalized[key] = []

    return normalized


def analyze_diff(diff_chunk: str) -> Dict[str, list]:
    prompt = f"""
You are a senior software engineer performing a strict PR review.

Analyze the following git diff and provide structured output:

1. Bugs / Logical Issues
2. Missing Test Cases
3. Bad Practices / Code Smells
4. Risk Analysis
5. Suggestions

Be specific. Avoid generic advice.

Git Diff:
{diff_chunk}

Return ONLY valid JSON.
"""

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0},
    }

    for _ in range(2):  # retry
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=120,
            )

            content = response.json().get("response", "")
            parsed = _extract_json(content)

            if parsed:
                return _normalize_result(parsed)

        except Exception:
            continue

    return {k: [] for k in ["bugs", "missing_tests", "bad_practices", "risks", "suggestions"]}