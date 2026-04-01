# AI PR Review Assistant

`ai_pr_review_assistant` is a small production-ready Python tool that:

- fetches PR diff from git
- reviews code with Ollama
- builds a structured review report
- posts the report as a GitHub PR comment

## Project Structure

```text
ai_pr_review_assistant/
 ├── main.py
 ├── git_utils.py
 ├── llm.py
 ├── reviewer.py
 ├── formatter.py
 ├── github.py
 ├── config.py
 ├── requirements.txt
 └── README.md
```

## Requirements

- Python 3.10+
- git installed
- Ollama running locally (`http://localhost:11434` by default)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run Locally

1. Move into the project folder:

```bash
cd ai_pr_review_assistant
```

2. Export environment variables:

```bash
export BASE_BRANCH="main"  # optional, defaults to main
export OLLAMA_MODEL="llama3.1"  # optional
export OLLAMA_BASE_URL="http://localhost:11434"  # optional
```

3. Run:

```bash
python main.py
```

Optional GitHub posting variables:

```bash
export GITHUB_TOKEN="ghp_xxx"
export GITHUB_REPOSITORY="owner/repo"
export PR_NUMBER="123"
```

If these are set, the tool posts the report as a PR comment.

## Behavior Overview

- Fetches latest base branch: `git fetch origin <base_branch>`
- Generates diff: `git diff origin/<base_branch>...HEAD`
- Ignores:
  - `package-lock.json`
  - `yarn.lock`
  - `dist/`
  - `build/`
  - `*.min.js`
- Chunks large diff payloads at 8000 chars
- Runs one LLM analysis per chunk
- Merges and deduplicates findings
- Prints a final report and optionally comments on PR

## GitHub Actions Integration

Create `.github/workflows/pr-review.yml` with:

```yaml
name: AI PR Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v3

      - name: Fetch base branch
        run: git fetch origin ${{ github.base_ref }}

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install deps
        run: pip install -r requirements.txt

      - name: Run Tool
        run: python main.py
        env:
          BASE_BRANCH: ${{ github.base_ref }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          OLLAMA_MODEL: llama3.1
```

### GitHub Actions Notes

- The default Ubuntu runner does not include Ollama by default.
- Add install/start/pull-model steps for Ollama before running `python main.py`.
- `GITHUB_TOKEN` is provided by GitHub Actions automatically.
