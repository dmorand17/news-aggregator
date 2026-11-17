# News Aggregator

Automated weekly news digests powered by RSS feeds + an LLM via [OpenRouter](https://openrouter.ai), published with Hugo to GitHub Pages.

📰 **Live site:** https://dmorand17.github.io/news-aggregator/

## How It Works

```
  daily-fetch.yml (every day, 12:00 UTC)
  │  feeds.yaml → fetch feeds → filter 7d → dedupe → append to reports/pending.json
  │  commit pending.json + seen.json → main
  │
  weekly-news.yml (Fridays 1 PM EST)
  │
  ├─[1: Python RSS Aggregator]──────────────────────────────────────────┐
  │  one last fetch to top up reports/pending.json
  │
  ├─[2: OpenRouter LLM]─────────────────────────────────────────────────┐
  │  pending.json + prompts/digest.md + web search → content/posts/YYYY-MM-DD.md
  │  then clear pending.json
  │
  ├─[3: git-auto-commit]────────────────────────────────────────────────┐
  │  commit post + seen.json + pending.json + costs.json → main
  │
  └─[4: Hugo build → deploy-pages]──────────────────────────────────────┐
     build static site → publish to GitHub Pages
```

## Theme

The site uses [**PaperMod**](https://github.com/adityatelange/hugo-PaperMod), a fast, clean Hugo theme, vendored as a git submodule at `themes/PaperMod` and selected via `theme = "PaperMod"` in `hugo.toml`. Clone with `--recurse-submodules` (or run `git submodule update --init`) so the theme is present locally.

Site-level customizations live outside the submodule so theme updates don't clobber them:
- `layouts/` — custom shortcodes (e.g. `costs`, `feeds`) and render hooks that override or extend the theme.
- `hugo.toml` — theme params, menu, and site config.

To update the theme:

```bash
git submodule update --remote themes/PaperMod
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
- GitHub repo with Actions enabled, Pages source set to **GitHub Actions**
- [OpenRouter](https://openrouter.ai) API key
- Python 3.13+ and [uv](https://docs.astral.sh/uv/)
- [Hugo extended](https://gohugo.io/installation/) (for local site preview)

> **Repo setup:** clone with `--recurse-submodules` (the PaperMod theme lives in
> `themes/PaperMod`). If you already cloned, run `git submodule update --init`.

### Adding the OpenRouter API key

1. Create a key at [openrouter.ai/settings/keys](https://openrouter.ai/settings/keys)
2. In your GitHub repo, go to **Settings** > **Secrets and variables** > **Actions**
3. Add a repository secret named `OPENROUTER_API_KEY` with the key as its value
4. *(Optional)* Under **Variables**, add `OPENROUTER_MODEL` to override the default
   model (`deepseek/deepseek-v4.1-flash-1017`, set in `src/news_aggregator/digest.py`)

The model must support tool calling — the digest uses OpenRouter's
`openrouter:web_search` server tool to catch news the feeds missed.

### Local Development

#### Step 1 — Fetch RSS feeds

```bash
# Run the aggregator (appends new entries to reports/pending.json)
uv run news-aggregator

# Inspect the buffer
python -m json.tool reports/pending.json | head -50
```

#### Step 2 — Generate the digest

```bash
export OPENROUTER_API_KEY=...
# export OPENROUTER_MODEL=google/gemini-3.8-flash  # optional override
uv run news-digest   # writes content/posts/YYYY-MM-DD.md and appends to data/costs.json
```

The editorial instructions (format, relevance tiers, categories) live in
[`prompts/digest.md`](prompts/digest.md).

#### Step 3 — Preview the site

```bash
# Serve the Hugo site locally with live reload
hugo server

# Then open http://localhost:1313/news-aggregator/
```

> **Note:** The aggregator tracks seen URLs in `reports/seen.json` to avoid duplicates across runs. Delete or reset this file if you want to reprocess all items.

### Manual Trigger (GitHub Actions)

Go to **Actions** > **Weekly News Digest** > **Run workflow**.

## Report Format

Each weekly digest is a Hugo post (`content/posts/YYYY-MM-DD.md`) with front matter
(title, date, summary) and a body containing:

1. **Top Story** — single most significant item with 2-3 sentence summary
2. **Dynamic categories** (4-6 sections based on the week's content)
   - High-relevance: major launches, breaking news
   - Medium-relevance: notable updates, ecosystem moves
   - Low-relevance: minor items, niche updates

Posts older than 90 days are pruned automatically.

## Cost

| Component | Cost |
|-----------|------|
| RSS feeds | Free |
| OpenRouter (1 run/week, DeepSeek V4.1 Flash + web search) | ~$0.05-0.20/run |
| GitHub Actions + Pages (<3 min/run) | Free tier |
| **Total** | **< $1/month** |

Actual per-run cost is recorded in `data/costs.json` and shown on the site's Costs page.

## Feeds

<!-- feeds-start -->

| Category | Source | Filter |
| --- | --- | --- |
| TLDR | [AI](https://bullrich.dev/tldr-rss/ai.rss) |  |
| TLDR | [DevOps](https://bullrich.dev/tldr-rss/devops.rss) |  |
| News Sites | [The Verge AI](https://www.theverge.com/rss/ai-artificial-intelligence/index.xml) |  |
| News Sites | [TechCrunch AI](https://techcrunch.com/category/artificial-intelligence/feed/) |  |
| Cloud | [AWS News](https://aws.amazon.com/blogs/aws/feed/) | `Week in Review` |
| Developer Platforms | [Ollama Blog](https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_ollama.xml) |  |
| Developer Platforms | [Claude Blog](https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_claude.xml) | `Product updates` |
| Developer Platforms | [OpenRouter Blog](https://openrouter.ai/blog/feed.xml) |  |
| AI | [Ahead of AI](https://magazine.sebastianraschka.com/feed) |  |
| AI | [Last Week in AI](https://lastweekin.ai/feed) |  |
| ChangeLogs | [Claude Code](https://code.claude.com/docs/en/changelog/rss.xml) |  |

<!-- feeds-end -->
