# Contributing to yt-Z-Downloader

Thanks for taking the time to contribute.

## Development setup

```bash
git clone https://github.com/Isuruzenith/yt-Z-downloader.git
cd yt-Z-downloader

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt

cp .env.example .env
python -m uvicorn api.main:app --reload --port 8080
```

## Running tests

```bash
pytest tests/ -q
```

All tests must pass before opening a PR.

## Code style

- Formatter / linter: [ruff](https://docs.astral.sh/ruff/)
- Run `ruff check api/` before committing
- No type: ignore comments unless absolutely necessary
- Keep functions small and focused

## Branch strategy

| Branch | Purpose |
|---|---|
| `main` | Stable releases only |
| `developer` | Active development, base for PRs |

Open PRs against **`developer`**, not `main`.

## Commit messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add playlist download support
fix: handle missing cookies.json gracefully
docs: update README quick start
chore: bump yt-dlp to 2026.3.0
```

## What makes a good PR

- One focused change per PR
- Includes tests for new behaviour
- `pytest tests/ -q` and `ruff check api/` both pass
- PR description explains the why, not just the what

## Reporting bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).
Include logs, yt-Z version (`/health`), and steps to reproduce.

## Security issues

Do not open a public issue for security vulnerabilities.
See [SECURITY.md](SECURITY.md) (coming soon) or email the maintainer directly.
