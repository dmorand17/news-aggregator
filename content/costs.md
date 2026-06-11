---
title: "Costs"
url: "/costs/"
summary: "What it costs to run this site, tracked per run."
ShowReadingTime: false
ShowToc: false
---

This site is cheap to run, but not free — each daily digest makes a series of
[Claude Code](https://www.claude.com/product/claude-code) API calls (reading the
feeds, searching the web, writing the post). The numbers below are recorded
automatically after every run for visibility into where the money goes.

{{< costs >}}

> **Note:** costs are **client-side estimates** reported by Claude Code, not
> authoritative billing figures. They're great for spotting trends but won't match
> your invoice to the penny. Token counts include the model's reasoning, tool use,
> and the full prompt context (which is re-sent each run, since daily runs are too
> far apart to share a prompt cache).

The aggregator (RSS fetching), Hugo build, and GitHub Pages hosting are all free,
so this is effectively the entire cost of the project.
