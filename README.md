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

### Using Claude Code (recommended)

Run `/add-feed` in Claude Code — it will prompt you for the category, name, and URL, then update `config/feeds.yaml` automatically. The [Feeds](#feeds) section of this README is kept in sync via a post-edit hook.

### Manually editing feeds.yaml

Edit `config/feeds.yaml` directly. Two formats are supported:

**Simple feed** (include all items):
```yaml
feeds:
  "Category Name":
    "Source Display Name": "https://feed-url"
```

**Filtered feed** (only items tagged with a matching RSS `<category>` CDATA value):
```yaml
feeds:
  "Category Name":
    "Source Display Name":
      url: "https://feed-url"
      category_filter: "Week in Review"
```

The `category_filter` value is matched case-insensitively against the entry's `<category>` tags. This is useful for high-volume feeds where you only want a specific series or tag.

After editing manually, sync the README feeds list by running:

```bash
uv run python .claude/hooks/sync_feeds_readme.py
```

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

## Feeds

<!-- feeds-start -->

### TLDR
- [AI](https://bullrich.dev/tldr-rss/ai.rss)
- [Tech](https://bullrich.dev/tldr-rss/tech.rss)
- [DevOps](https://bullrich.dev/tldr-rss/devops.rss)

### News Sites
- [The Verge AI](https://www.theverge.com/rss/ai-artificial-intelligence/index.xml)
- [TechCrunch AI](https://techcrunch.com/category/artificial-intelligence/feed/)

### Cloud
- [AWS News](https://aws.amazon.com/blogs/aws/feed/)

### Developer Platforms
- [Ollama Blog](https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_ollama.xml)
- [Claude Blog](https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_claude.xml)
- [Claude Code Changelog](https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_changelog_claude_code.xml)

### AI
- [Ahead of AI](https://magazine.sebastianraschka.com/feed)
- [Last Week in AI](https://lastweekin.ai/feed)

### ChangeLogs
- [Obsidian](https://obsidian.md/changelog.xml)
- [Kiro](https://kiro.dev/changelog/feed.rss)

### Investing
- [TechCrunch Venture](https://techcrunch.com/category/venture/feed/)

<!-- feeds-end -->
