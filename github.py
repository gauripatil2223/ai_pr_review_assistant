"""GitHub API integration for posting PR comments."""

from __future__ import annotations

import os

import requests


def github_context_available() -> bool:
    """Return True if required GitHub env vars exist."""
    return all(
        [
            os.getenv("GITHUB_TOKEN"),
            os.getenv("GITHUB_REPOSITORY"),
            os.getenv("PR_NUMBER"),
        ]
    )


def post_pr_comment(body: str) -> None:
    """Post the report as a comment on the current pull request."""
    token = os.getenv("GITHUB_TOKEN")
    repository = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")

    if not (token and repository and pr_number):
        raise RuntimeError("Missing GITHUB_TOKEN, GITHUB_REPOSITORY, or PR_NUMBER.")

    url = f"https://api.github.com/repos/{repository}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
    }
    response = requests.post(url, headers=headers, json={"body": body}, timeout=30)

    if response.status_code >= 300:
        raise RuntimeError(
            f"GitHub API request failed ({response.status_code}): {response.text}"
        )
