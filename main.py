"""Entry point for the AI PR review assistant."""

from __future__ import annotations

import sys
from typing import List

from config import BASE_BRANCH, DIFF_CHUNK_SIZE
from formatter import format_report
from git_utils import GitDiffError, ensure_git_repo, fetch_diff
from github import github_context_available, post_pr_comment
from llm import analyze_diff
from reviewer import chunk_diff, merge_review_results


def main() -> int:
    try:
        ensure_git_repo()
    except GitDiffError as exc:
        print(f"[error] Not a git repository: {exc}")
        return 1

    try:
        diff = fetch_diff(BASE_BRANCH)
    except GitDiffError as exc:
        print(f"[error] Git diff failed: {exc}")
        return 1

    if not diff.strip():
        print("[info] No changes detected.")
        return 0

    chunks = chunk_diff(diff, DIFF_CHUNK_SIZE)
    print(f"[info] Processing {len(chunks)} chunk(s)")

    results: List[dict] = []
    failed = 0

    for i, chunk in enumerate(chunks, 1):
        try:
            print(f"[info] Analyzing chunk {i}/{len(chunks)}")
            results.append(analyze_diff(chunk))
        except Exception as exc:
            print(f"[error] Chunk {i} failed: {exc}")
            failed += 1

    if not results:
        print("[error] All chunks failed")
        return 1

    if failed:
        print(f"[warning] {failed} chunk(s) failed")

    merged = merge_review_results(results)
    report = format_report(merged)

    print("\n" + report)

    if github_context_available():
        try:
            post_pr_comment(report)
            print("[info] Comment posted to PR")
        except Exception as exc:
            print(f"[error] GitHub comment failed: {exc}")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())