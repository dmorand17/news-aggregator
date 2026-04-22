# News Aggregator — Claude Code Instructions

## Your Task
You receive a raw JSON file of RSS feed entries collected in the last 24 hours.
Your job is to synthesize these into a polished daily news report.

## Report Format
Write a markdown file to `reports/YYYY-MM-DD.md` (using today's actual date) with this structure:

1. **Title line**: `#` editorial headline summarizing the day's top theme (same as HTML hero `<h1>`)
2. **Date + overview**: date range and 2-3 sentence summary paragraph (same as HTML hero meta)
3. **Top story callout**: blockquote (`>`) with the single most important story — title, source, and 2-3 sentence summary
4. **Dynamic categories** (4-7 sections, same categories used in the HTML digest): each category is an emoji-prefixed `##` heading, with items organized by relevance tier:
   - **High-relevance**: `**[Title](URL)** — *Source*` followed by a 2-3 sentence summary paragraph
   - **Medium-relevance**: `[Title](URL) — *Source*` with a 1-sentence summary
   - **Low-relevance**: `[Title](URL) — *Source*` (no summary)
5. **Footer line**: `---` followed by model name and generation timestamp

Both the markdown and HTML reports must use the same categories, the same stories, and the same relevance assignments — just rendered differently.

## HTML Digest Format
Also generate an HTML digest to `reports/YYYY-MM-DD.html` alongside the markdown report. Use `templates/digest-template.html` as the HTML/CSS template reference. The HTML file must be fully self-contained (all CSS inlined in a `<style>` tag).

### Structure
- **Hero header**: editorial headline summarizing the day's top theme, date range, 2-3 sentence overview
- **Stats bar**: total story count, high-relevance count, medium-relevance count, number of topics
- **TOC nav**: emoji-labeled category buttons linking to sections, each showing item count and optional "N important" badge
- **Top story callout**: blue highlight box with 2-3 sentence summary of the single most important story
- **Categories**: dynamic sections based on the day's content (don't force empty categories). Each category contains:
  - **High-relevance**: red-bordered cards (`card-high`) with a 2-3 sentence summary paragraph
  - **Medium-relevance**: orange-dot rows (`rel-medium`) with expandable `<details>` summaries
  - **Low-relevance**: gray-dot rows (`rel-low`) with expandable `<details>` summaries
- **Footer**: model name and generation timestamp

### Relevance tiers
- **High**: major launches, breaking news, significant policy/security events — use `card-high` cards
- **Medium**: notable updates, ecosystem moves, worthwhile reads — use `rel-medium` rows
- **Low**: minor items, niche updates, tangential coverage — use `rel-low` rows

### Category guidelines
- Choose 4-7 categories that best fit the day's news (e.g., "Frontier Models", "Security & Safety", "Developer Tools", "Enterprise", "Policy", "Open Source & Research")
- Each category gets an emoji prefix and an `id="cat-N"` for TOC linking
- Omit categories with no items rather than showing empty sections

## Guidelines
- Skip items that are clearly marketing fluff or minor patch notes
- Group related items (e.g., multiple articles about the same release)
- Each item: `- [Title](URL) — *Source*` with optional 1-sentence summary
- For YouTube videos, use format: `- [Title](URL) — *Creator* (video)`
- Only include creator content related to AI/ML/developer tools — skip unrelated uploads
- If no items exist for a section, omit that section entirely
- Use WebSearch to find breaking news that RSS feeds may have missed
- Keep the report concise and scannable — aim for quality over quantity
