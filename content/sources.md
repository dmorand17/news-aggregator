---
title: "Sources"
url: "/sources/"
summary: "The RSS feeds this digest is built from."
ShowReadingTime: false
ShowToc: true
---

Every digest is assembled from the feeds below, pulled fresh every morning and
grouped by category. A few high-volume feeds use a **filter** so only items tagged
with a specific series (e.g. AWS *Week in Review*) are included; the rest pull in
everything.

This table is generated directly from the site's feed configuration, so it always
reflects exactly what's being aggregated.

{{< feeds >}}

## Filtering

Most feeds are pulled in wholesale — every new item is a candidate for the digest.
But some sources publish far more than is relevant here (a general company blog, a
busy news section), so they use a **category filter**.

A filter is a case-insensitive keyword matched against each entry's RSS
`<category>` tags. Only items whose tags contain that keyword are kept; everything
else from that feed is ignored before it ever reaches the digest. For example, the
**AWS News** feed is filtered to `Week in Review`, so the firehose of AWS product
announcements is narrowed down to just the weekly roundup posts.

Feeds with no filter (shown as **—** in the table above) contribute all of their
recent items, subject to the usual 24-hour window and de-duplication.

## Adding a source

The feed list lives in a single file — `config/feeds.yaml` — and there are two
ways to add to it.

### With Claude Code (recommended)

This project ships an [`/add-feed`](https://github.com/dmorand17/news-aggregator/tree/main/.claude/skills/add-feed)
skill. Run it in Claude Code and it walks you through the whole thing, one question
at a time:

1. **Category** — pick an existing one or create a new category
2. **Display name** — the source label shown in the digest (e.g. *TechCrunch AI*)
3. **RSS URL** — the feed address
4. **Filter** *(optional)* — a keyword to narrow a high-volume feed

It then writes the entry to `config/feeds.yaml` in the correct format — choosing
the filtered or unfiltered form automatically — and this Sources page updates on
the next build, since it reads from that same file.

### Manually

Edit `config/feeds.yaml` directly. Use the short form for an unfiltered feed:

```yaml
"Category Name":
  "Display Name": "https://feed-url"
```

…or the expanded form to add a filter:

```yaml
"Category Name":
  "Display Name":
    url: "https://feed-url"
    category_filter: "keyword"
```

---

Found a feed worth adding? Open an issue or PR on
[GitHub](https://github.com/dmorand17/news-aggregator).
