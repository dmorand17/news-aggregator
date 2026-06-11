---
name: add-feed
description: Add a new RSS/Atom feed to the news-aggregator's config/feeds.yaml. Use when user says "add a feed", "add an RSS feed", "subscribe to a feed", or wants to register a new source for the daily digest.
---

# Add Feed

Adds a new RSS/Atom feed entry to `config/feeds.yaml`, prompting for category, display name, URL, and optional category filter.

## Process

Ask the user these questions **one at a time**, waiting for an answer before proceeding to the next:

1. **Category** — read `config/feeds.yaml`, list its existing top-level categories, and offer "New category" as an additional choice.
2. **New category name** — only if the user chose "New category".
3. **Display name** — the source label shown in the digest (e.g. "TechCrunch AI").
4. **RSS URL** — the feed URL.
5. **Category filter** (optional) — a case-insensitive substring matched against the RSS `<category>` tags. Skip if not needed.

## Writing the entry

Edit `config/feeds.yaml` and add the feed under the chosen category, creating the category if new.

Use the **short form** when there is no filter:

```yaml
"Display Name": "https://feed-url"
```

Use the **expanded form** when a filter was provided:

```yaml
"Display Name":
  url: "https://feed-url"
  category_filter: "keyword"
```

Note: the key is `category_filter`, not `filter`.

## After saving

Confirm to the user what was added — category, display name, URL, and filter (if any).
