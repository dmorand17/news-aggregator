# News Aggregator — Claude Code Instructions

Weekly news digest: RSS feeds → LLM (via OpenRouter) → Hugo post → GitHub Pages.

- `config/feeds.yaml` — feed list (single source of truth; also rendered on /sources/)
- `src/news_aggregator/aggregate.py` — fetches feeds, keeps the last 7 days, de-dupes, appends to `reports/pending.json` (run daily)
- `src/news_aggregator/digest.py` — sends `pending.json` + `prompts/digest.md` to OpenRouter, writes `content/posts/YYYY-MM-DD.md`, appends cost to `data/costs.json`, clears the buffer
- `prompts/digest.md` — the editorial instructions / report format for the digest
- `.github/workflows/daily-fetch.yml` — daily fetch into the buffer (some feeds only keep hours of history)
- `.github/workflows/weekly-news.yml` — Friday cron: final fetch, digest, Hugo build, deploy

If asked to write a digest by hand, follow `prompts/digest.md`.

Run tests with `uv run --with pytest pytest -q tests`.
