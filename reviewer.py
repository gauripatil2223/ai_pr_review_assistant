"""Review orchestration helpers: chunking and merge logic."""

from __future__ import annotations

from typing import Dict, List

REVIEW_KEYS = ["bugs", "missing_tests", "bad_practices", "risks", "suggestions"]

MAX_CHUNKS = 10
MAX_ITEMS_PER_SECTION = 10


def chunk_diff(diff_text: str, chunk_size: int) -> List[str]:
    """Split diff by file first, then by size."""
    if not diff_text.strip():
        return []

    # Split by file boundaries
    file_chunks = [
        "diff --git " + chunk
        for chunk in diff_text.split("diff --git ")
        if chunk.strip()
    ]

    final_chunks = []
    for file_chunk in file_chunks:
        if len(file_chunk) <= chunk_size:
            final_chunks.append(file_chunk)
        else:
            # Further split large file chunks
            for i in range(0, len(file_chunk), chunk_size):
                final_chunks.append(file_chunk[i : i + chunk_size])

    return final_chunks[:MAX_CHUNKS]


def _normalize(text: str) -> str:
    return text.lower().strip()


def merge_review_results(results: List[Dict[str, list]]) -> Dict[str, list]:
    """Merge chunk review results with normalization and limits."""
    merged = {key: [] for key in REVIEW_KEYS}
    seen = {key: set() for key in REVIEW_KEYS}

    for result in results:
        for key in REVIEW_KEYS:
            for item in result.get(key, []):
                cleaned = str(item).strip()
                if not cleaned:
                    continue

                norm = _normalize(cleaned)

                if norm not in seen[key]:
                    seen[key].add(norm)
                    merged[key].append(cleaned)

    # Limit output size
    for key in REVIEW_KEYS:
        merged[key] = merged[key][:MAX_ITEMS_PER_SECTION]

    return merged