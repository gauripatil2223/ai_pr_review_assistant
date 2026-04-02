"""Central configuration for the AI PR review assistant."""

from __future__ import annotations

import os


# -----------------------------
# BASE CONFIG
# -----------------------------
DEFAULT_BASE_BRANCH = "main"
BASE_BRANCH = os.getenv("BASE_BRANCH", DEFAULT_BASE_BRANCH)

DIFF_CHUNK_SIZE = int(os.getenv("DIFF_CHUNK_SIZE", "8000"))


# -----------------------------
# IGNORED FILES
# -----------------------------
IGNORED_PATH_PATTERNS = [
    "package-lock.json",
    "yarn.lock",
    "dist/*",
    "build/*",
    "*.min.js",
]


# -----------------------------
# LLM PROVIDER CONFIG
# -----------------------------
SUPPORTED_PROVIDERS = {"ollama", "together"}

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
LLM_FALLBACK_PROVIDER = os.getenv("LLM_FALLBACK_PROVIDER")  # optional


# -----------------------------
# OLLAMA CONFIG (LOCAL)
# -----------------------------
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2:7b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")


# -----------------------------
# TOGETHER AI CONFIG (CLOUD)
# -----------------------------
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "Qwen/Qwen2-7B-Instruct")


# -----------------------------
# VALIDATION
# -----------------------------
def validate_config() -> None:
    """Validate critical configuration at startup."""

    # Validate provider
    if LLM_PROVIDER not in SUPPORTED_PROVIDERS:
        raise ValueError(
            f"Invalid LLM_PROVIDER '{LLM_PROVIDER}'. Supported: {SUPPORTED_PROVIDERS}"
        )

    # Validate fallback (if provided)
    if LLM_FALLBACK_PROVIDER:
        if LLM_FALLBACK_PROVIDER not in SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Invalid LLM_FALLBACK_PROVIDER '{LLM_FALLBACK_PROVIDER}'"
            )

    # Provider-specific checks
    if LLM_PROVIDER == "together" and not TOGETHER_API_KEY:
        raise ValueError("TOGETHER_API_KEY is required when using 'together' provider")

    if LLM_FALLBACK_PROVIDER == "together" and not TOGETHER_API_KEY:
        raise ValueError("TOGETHER_API_KEY required for fallback provider 'together'")