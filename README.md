# News Aggregator

Automated daily news reports powered by RSS feeds + Claude Code.

## How It Works

```
┌─────────────────────────────────────────────────────┐
│    GitHub Actions  (daily cron 12:00 UTC / 7 AM EST)│
└───────────────────────────┬─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│           Step 1: Python RSS Aggregator             │
│                                                     │
│  config/feeds.yaml                                  │
│       │                                             │
│       ▼                                             │
│  Fetch RSS/Atom feeds                               │
│       │                                             │
│       ▼                                             │
│  Filter to last 24h · Deduplicate via seen.json     │
│       │                                             │
│       ▼                                             │
│  reports/raw-YYYY-MM-DD.json                        │
└───────────────────────────┬─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│                  Step 2: Claude Code                │
│                                                     │
│  Read raw JSON                                      │
│       │                                             │
│       ▼                                             │
│  WebSearch for breaking news RSS may have missed    │
│       │                                             │
│       ▼                                             │
│  Synthesize into markdown + HTML report             │
│       │                                             │
│       ▼                                             │
│  reports/YYYY-MM-DD.md · reports/YYYY-MM-DD.html    │
└───────────────────────────┬─────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────┐
│             Step 3: git-auto-commit-action          │
│                                                     │
│  Commit report + seen.json to main                  │
└─────────────────────────────────────────────────────┘
```

## Configuring Feeds

All RSS feeds are defined in **`config/feeds.yaml`** — no code changes needed.

```yaml
feeds:
  "Category Name":
    "Source Display Name": "https://feed-url"
```

Add, remove, or rename feeds by editing that file.

## Setup

### Prerequisites
- GitHub repo with Actions enabled
- Anthropic API key
- Python 3.13+ and [uv](https://docs.astral.sh/uv/)

### Adding the Anthropic API Key

1. Get your API key at https://console.anthropic.com/settings/keys
2. In your GitHub repo, go to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `ANTHROPIC_API_KEY`, Value: paste your key
5. Click **Add secret**

### Local Development

#### Step 1 — Fetch RSS feeds

```bash
# Install dependencies
uv pip install -r scripts/requirements.txt

# Run the aggregator (writes reports/raw-YYYY-MM-DD.json)
uv run python scripts/aggregate_news.py

# Inspect the output
cat reports/raw-$(date +%Y-%m-%d).json | python -m json.tool | head -50
```

#### Step 2 — Generate the report with Claude Code

Make sure `ANTHROPIC_API_KEY` is set in your environment, then run Claude Code directly against the raw JSON:

```bash
export ANTHROPIC_API_KEY=sk-ant-...

claude --model claude-sonnet-4-6 \
  --max-turns 30 \
  --allowedTools "Read,Write,Glob,Grep,WebFetch,WebSearch,Bash(date *),Bash(ls *)" \
  --print \
  "Read the raw feed data from reports/raw-$(date +%Y-%m-%d).json. \
   Follow the instructions in CLAUDE.md to generate a polished daily news report. \
   Save a markdown report to reports/$(date +%Y-%m-%d).md and an HTML digest to \
   reports/$(date +%Y-%m-%d).html. Use templates/digest-template.html as the HTML template."
```

#### Step 3 — View the output

```bash
# Open the HTML digest in your browser
open reports/$(date +%Y-%m-%d).html

# Or read the markdown report
cat reports/$(date +%Y-%m-%d).md
```

> **Note:** The aggregator tracks seen URLs in `reports/seen.json` to avoid duplicates across runs. Delete or reset this file if you want to reprocess all items.

### Manual Trigger (GitHub Actions)

Go to **Actions** > **Daily News Report** > **Run workflow**.

## Report Format

Each daily report includes:

1. **Top Story** — single most significant item with 2-3 sentence summary
2. **Dynamic categories** (4-7 sections based on the day's content)
   - High-relevance: major launches, breaking news
   - Medium-relevance: notable updates, ecosystem moves
   - Low-relevance: minor items, niche updates

## Cost

| Component | Cost |
|-----------|------|
| RSS feeds | Free |
| Claude Code API (~10 turns/day, sonnet) | ~$0.10-0.25/day |
| GitHub Actions (<2 min/run) | Free tier |
| **Total** | **~$3-8/month** |
