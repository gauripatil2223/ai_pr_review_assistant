"""Formatting utilities for human-readable PR reports."""

from __future__ import annotations

from typing import Dict, List


def _format_section(title: str, items: List[str]) -> str:
    if not items:
        return f"{title}\n- None"
    lines = [title] + [f"- {item}" for item in items]
    return "\n".join(lines)


def format_report(review_data: Dict[str, list]) -> str:
    """Create the final markdown-ish report body."""
    sections = [
        "=== AI PR REVIEW REPORT ===",
        "",
        _format_section("🚨 Bugs:", review_data.get("bugs", [])),
        "",
        _format_section("🧪 Missing Tests:", review_data.get("missing_tests", [])),
        "",
        _format_section("⚠️ Risks:", review_data.get("risks", [])),
        "",
        _format_section("🧹 Code Smells:", review_data.get("bad_practices", [])),
        "",
        _format_section("💡 Suggestions:", review_data.get("suggestions", [])),
    ]
    return "\n".join(sections).strip() + "\n"
