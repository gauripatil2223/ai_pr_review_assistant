"""GitHub API integration for posting/updating PR comments."""

from __future__ import annotations

import os
from typing import Optional

import requests


# Unique marker to पहचान our comment
MARKER = "<!-- AI_PR_REVIEW -->"


def github_context_available() -> bool:
    """Return True if required GitHub env vars exist."""
    return all(
        [
            os.getenv("GITHUB_TOKEN"),
            os.getenv("GITHUB_REPOSITORY"),
            os.getenv("PR_NUMBER"),
        ]
    )


def _get_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }


def _get_existing_comment(
    repo: str, pr_number: str, headers: dict
) -> Optional[dict]:
    """Fetch existing PR comments and find our tool's comment."""
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code >= 300:
        raise RuntimeError(
            f"Failed to fetch comments ({response.status_code}): {response.text}"
        )

    comments = response.json()

    for comment in comments:
        if MARKER in comment.get("body", ""):
            return comment

    return None


def post_or_update_pr_comment(body: str) -> None:
    """Create or update PR comment to avoid spam."""
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not (token and repo and pr_number):
        raise RuntimeError("Missing GITHUB_TOKEN, GITHUB_REPOSITORY, or PR_NUMBER.")

    headers = _get_headers(token)

    # Add marker so we can पहचान our own comment later
    final_body = f"{MARKER}\n{body}"

    existing_comment = _get_existing_comment(repo, pr_number, headers)

    if existing_comment:
        # 🔄 UPDATE EXISTING COMMENT
        update_url = existing_comment["url"]

        response = requests.patch(
            update_url,
            headers=headers,
            json={"body": final_body},
            timeout=30,
        )

        if response.status_code >= 300:
            raise RuntimeError(
                f"Failed to update comment ({response.status_code}): {response.text}"
            )

        print("[info] Updated existing PR comment")

    else:
        # ➕ CREATE NEW COMMENT
        create_url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"

        response = requests.post(
            create_url,
            headers=headers,
            json={"body": final_body},
            timeout=30,
        )

        if response.status_code >= 300:
            raise RuntimeError(
                f"Failed to create comment ({response.status_code}): {response.text}"
            )

        print("[info] Created new PR comment")