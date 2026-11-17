---
title: "How This Site Works"
url: "/how-it-works/"
summary: "The pipeline behind the weekly digest, from RSS feeds to published site."
ShowReadingTime: true
ShowToc: true
mermaid: true
---

This site is fully automated. No one writes the digests by hand — a GitHub Actions
workflow collects feed entries every day, and every Friday another turns the week's
collection into a digest and publishes the site. Here's the full picture.

## Architecture

```mermaid
flowchart TD
    subgraph schedule[" "]
        daily([⏰ daily fetch])
        weekly([⏰ weekly digest · Fri 1 PM EST])
    end

    subgraph aggregate["1 · Aggregate"]
        feeds[(config/feeds.yaml<br/>curated feed list)]
        py[🐍 news-aggregator<br/>fetch · filter 7d · dedupe]
        seen[(reports/seen.json<br/>dedupe memory)]
        raw[(reports/pending.json<br/>weekly buffer)]
        feeds --> py
        seen <--> py
        py --> raw
    end

    subgraph synth["2 · Synthesize"]
        llm[🤖 LLM via OpenRouter<br/>read · rank · group · write]
        web([🌐 WebSearch<br/>breaking news])
        post[/content/posts/<br/>YYYY-MM-DD.md/]
        raw --> llm
        web --> llm
        llm --> post
    end

    subgraph publish["3 · Publish"]
        hugo[⚡ Hugo<br/>build static site]
        pages[☁️ GitHub Pages]
        post --> hugo
        hugo --> pages
    end

    daily --> py
    weekly --> llm
    pages --> reader([👀 You])

    style daily fill:#2563eb,color:#fff
    style weekly fill:#2563eb,color:#fff
    style llm fill:#6366f1,color:#fff
    style reader fill:#16a34a,color:#fff
```

## Step by step

### 1 · Aggregate

A small Python tool (`news-aggregator`) reads the feed list from
[`config/feeds.yaml`](/sources/), fetches every feed, and keeps only entries from
the **last 7 days**. It runs **every day** — some feeds only keep a few hours of
history — and appends new entries to a buffer, `pending.json`. It tracks every URL
it has already seen in `seen.json`, so the same story is never collected twice.
On Friday the buffer holds the whole week's entries; the digest step consumes it
and starts a fresh one.

### 2 · Synthesize

An LLM, called through [OpenRouter](https://openrouter.ai), reads that raw JSON
and does the editorial work: it skips marketing fluff and minor patch notes, groups
articles that cover the same story, picks the week's top story, sorts everything
into themed categories, and assigns each item a relevance tier. It also runs a
**web search** to catch breaking news the RSS feeds may have missed. The output is
one Markdown post with front matter — the same format you're reading now.

### 3 · Publish

[Hugo](https://gohugo.io) builds the Markdown into this static site — archive,
navigation, RSS feed, and all — and the workflow deploys it to **GitHub Pages**.
Posts older than 90 days are pruned automatically to keep things current.

## The whole thing is open source

Feed config, aggregator, editorial prompt, and site templates all live in one
repo. Browse it, fork it, or suggest a feed on
[GitHub](https://github.com/dmorand17/news-aggregator).
