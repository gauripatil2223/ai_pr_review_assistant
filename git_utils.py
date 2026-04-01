"""Utilities for fetching and filtering git diffs."""

from __future__ import annotations

import fnmatch
import subprocess
from typing import List

from config import IGNORED_PATH_PATTERNS


class GitDiffError(Exception):
    """Raised when git operations fail."""


def _run_git_command(args: List[str]) -> str:
    """Run a git command and return stdout or raise GitDiffError."""
    try:
        result = subprocess.run(
            args,
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise GitDiffError("Git is not installed or not available in PATH.") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        raise GitDiffError(stderr or f"Git command failed: {' '.join(args)}") from exc
    return result.stdout


def ensure_git_repo() -> None:
    """Validate that the current working directory is a git repository."""
    _run_git_command(["git", "rev-parse", "--is-inside-work-tree"])


def _is_ignored_file(path: str) -> bool:
    """Return True if a file path matches ignored patterns."""
    normalized = path.strip()
    if not normalized:
        return False
    for pattern in IGNORED_PATH_PATTERNS:
        if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(
            normalized, f"*/{pattern}"
        ):
            return True
    return False


def _extract_file_path_from_header(header_line: str) -> str:
    """
    Extract file path from a git diff header line:
      diff --git a/path b/path
    """
    parts = header_line.split()
    if len(parts) < 4:
        return ""
    b_path = parts[3]  # typically "b/<path>"
    return b_path[2:] if b_path.startswith("b/") else b_path


def _filter_ignored_files_from_diff(raw_diff: str) -> str:
    """Remove file diff blocks matching ignored patterns."""
    if not raw_diff.strip():
        return ""

    blocks = raw_diff.split("diff --git ")
    kept_blocks = []

    for block in blocks:
        if not block.strip():
            continue
        first_line = block.splitlines()[0]
        file_path = _extract_file_path_from_header(f"diff --git {first_line}")
        if _is_ignored_file(file_path):
            continue
        kept_blocks.append(f"diff --git {block}")

    return "".join(kept_blocks).strip()


def fetch_diff(base_branch: str) -> str:
    """Fetch latest base branch ref and return filtered git diff vs HEAD."""
    _run_git_command(["git", "fetch", "origin", base_branch])
    raw_diff = _run_git_command(["git", "diff", f"origin/{base_branch}...HEAD"])
    return _filter_ignored_files_from_diff(raw_diff)
