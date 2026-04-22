# News Aggregator

Automated daily news reports powered by RSS feeds + Claude Code.

## How It Works

```
  GitHub Actions (daily cron 7 AM EST)
  │
  ├─[1: Python RSS Aggregator]──────────────────────────────────────────┐
  │  feeds.yaml → fetch feeds → filter 24h → dedupe → raw-YYYY-MM-DD.json
  │
  ├─[2: Claude Code]────────────────────────────────────────────────────┐
  │  raw JSON + WebSearch → synthesize → YYYY-MM-DD.{md,html}
  │
  └─[3: git-auto-commit]────────────────────────────────────────────────┐
     commit report + seen.json → main
```

## Configuring Feeds

All RSS feeds are defined in **`config/feeds.yaml`** — no code changes needed.

**Simple feed** (include all items):
```yaml
feeds:
  "Category Name":
    "Source Display Name": "https://feed-url"
```

**Filtered feed** (only include items whose title contains the filter string):
```yaml
feeds:
  "Category Name":
    "Source Display Name":
      url: "https://feed-url"
      filter: "keyword to match"
```

The `filter` value is matched case-insensitively against each entry's title. Items that don't match are skipped. This is useful for high-volume feeds where you only want a specific series or tag (e.g., filtering an AWS blog feed to just "AWS Weekly Roundup").

Add, remove, or rename feeds by editing that file.

## Setup

### Prerequisites
- GitHub repo with Actions enabled
- Claude Code OAuth token
- Python 3.13+ and [uv](https://docs.astral.sh/uv/)

### Adding the Claude Code OAuth Token

1. Get your OAuth token from [claude.ai/settings](https://claude.ai/settings) under **Claude Code**
2. In your GitHub repo, go to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret**
4. Name: `CLAUDE_CODE_OAUTH_TOKEN`, Value: paste your token
5. Click **Add secret**

### Local Development

#### Step 1 — Fetch RSS feeds

```bash
# Run the aggregator (writes reports/raw-YYYY-MM-DD.json)
uv run python aggregate_news.py

# Inspect the output
cat reports/raw-$(date +%Y-%m-%d).json | python -m json.tool | head -50
```

#### Step 2 — Generate the report with Claude Code

Make sure `CLAUDE_CODE_OAUTH_TOKEN` is set in your environment, then run Claude Code directly against the raw JSON:

```bash
export CLAUDE_CODE_OAUTH_TOKEN=...

claude --model claude-sonnet-4-6 \
  --max-turns 30 \
  --allowedTools "Read,Write,Glob,Grep,WebFetch,WebSearch,Bash(date *),Bash(ls *)" \
  --print \
  "Read the raw feed data from reports/raw-$(date +%Y-%m-%d).json. \
   Follow the instructions in CLAUDE.md to generate a polished daily news report. \
   Save a markdown report to reports/$(date +%Y-%m-%d).md and an HTML digest to \
   reports/$(date +%Y-%m-%d).html. Use templates/digest-template.html as the HTML template. \
   Use WebSearch to find any breaking news that RSS feeds may have missed."
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
