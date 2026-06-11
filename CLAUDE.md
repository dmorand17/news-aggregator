# News Aggregator — Claude Code Instructions

## Your Task
You receive a raw JSON file of RSS feed entries collected over the last 24 hours.
Your job is to synthesize these into a polished daily news digest published as a
Hugo post.

## Report Format
Write a single markdown file to `content/posts/YYYY-MM-DD.md` (today's date, e.g.
`2026-06-11.md`). This is a Hugo content page — it must begin with TOML/YAML front
matter, then the body.

### Front matter (required)
```yaml
---
title: "<editorial headline summarizing the day's top theme>"
date: <today as RFC3339, e.g. 2026-06-11T10:00:00Z>
summary: "<2-3 sentence overview of the day's news>"
---
```
The `title` and `summary` render as the post's heading and the archive/home
listing blurb, so write them for a reader scanning a list of days. Do not repeat
the title as an `#` heading in the body — Hugo renders `title` automatically.

### Body
1. **Top story callout**: blockquote (`>`) with the single most important story —
   title, source, and a 2-3 sentence summary.
2. **Dynamic categories** (aim for 3-5 sections; daily volume is small): each
   category is an emoji-prefixed `##` heading. Within a category, organize items
   by relevance tier and group related items covering the same story:
   - **High-relevance**: `**[Title](URL)** — *Source*` followed by a 2-3 sentence summary paragraph
   - **Medium-relevance**: `[Title](URL) — *Source*` with a 1-sentence summary
   - **Low-relevance**: `[Title](URL) — *Source*` (no summary)
3. **Footer line**: `---` followed by model name and generation timestamp.

### Relevance tiers
- **High**: major launches, breaking news, significant policy/security events
- **Medium**: notable updates, ecosystem moves, worthwhile reads
- **Low**: minor items, niche updates, tangential coverage

### Category guidelines
- Choose 3-5 categories that best fit the day's news (e.g., "Frontier Models",
  "Security & Safety", "Developer Tools", "Enterprise", "Policy", "Open Source & Research")
- Each category gets an emoji prefix
- Omit categories with no items rather than showing empty sections

## Guidelines
- Skip items that are clearly marketing fluff or minor patch notes
- Group related items (e.g., multiple articles about the same release)
- Each item: `- [Title](URL) — *Source*` with optional 1-sentence summary
- For YouTube videos, use format: `- [Title](URL) — *Creator* (video)`
- Only include creator content related to AI/ML/developer tools — skip unrelated uploads
- If no items exist for a section, omit that section entirely
- Use WebSearch to find breaking news from the day that RSS feeds may have missed
- Keep the digest concise and scannable — aim for quality over quantity
- With only a day of data, some days will be light; surface the most significant
  stories rather than padding. A short, sharp digest is better than a padded one.
