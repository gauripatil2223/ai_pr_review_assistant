"""Central configuration for the AI PR review assistant."""

from __future__ import annotations

import os


DEFAULT_BASE_BRANCH = "main"
BASE_BRANCH = os.getenv("BASE_BRANCH", DEFAULT_BASE_BRANCH)

# Keep ignored patterns simple and explicit.
IGNORED_PATH_PATTERNS = [
    "package-lock.json",
    "yarn.lock",
    "dist/*",
    "build/*",
    "*.min.js",
]

# Maximum characters per diff chunk sent to the LLM.
DIFF_CHUNK_SIZE = 8000

# Ollama config can be overridden with environment variables.
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
