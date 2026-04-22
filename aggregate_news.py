#!/usr/bin/env python3
"""Fetch RSS/Atom feeds from configured sources, filter to last 24 hours, de-dupe."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml
from dateutil import parser as dateparser

REPO_ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = REPO_ROOT / "reports"
SEEN_FILE = REPORTS_DIR / "seen.json"
FEEDS_CONFIG = REPO_ROOT / "config" / "feeds.yaml"


def load_feeds() -> dict[str, dict[str, str]]:
    """Load feed definitions from config/feeds.yaml."""
    with FEEDS_CONFIG.open() as f:
        data = yaml.safe_load(f)
    return data.get("feeds", {})


def load_seen() -> dict[str, str]:
    """Load the seen URLs tracker. Values are ISO date strings."""
    if SEEN_FILE.exists():
        return json.loads(SEEN_FILE.read_text())
    return {}


def save_seen(seen: dict[str, str]) -> None:
    """Save seen URLs, pruning entries older than 7 days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    pruned = {url: ts for url, ts in seen.items() if ts > cutoff}
    SEEN_FILE.write_text(json.dumps(pruned, indent=2))


def parse_entry_date(entry: feedparser.FeedParserDict) -> datetime | None:
    """Extract a timezone-aware datetime from a feed entry."""
    for field in ("published", "updated"):
        raw = entry.get(f"{field}_parsed") or entry.get(field)
        if raw is None:
            continue
        # feedparser's *_parsed is a time.struct_time
        if hasattr(raw, "tm_year"):
            from calendar import timegm

            return datetime.fromtimestamp(timegm(raw), tz=timezone.utc)
        # Fall back to dateutil for string dates
        if isinstance(raw, str):
            try:
                dt = dateparser.parse(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                continue
    return None


def fetch_feeds(
    cutoff: datetime, seen: dict[str, str], feeds: dict[str, dict[str, str]]
) -> list[dict]:
    """Fetch all feeds and return entries newer than cutoff that haven't been seen."""
    entries = []
    for category, sources in feeds.items():
        for source_name, url in sources.items():
            try:
                feed = feedparser.parse(url)
            except Exception as exc:
                print(f"  [WARN] Failed to fetch {source_name}: {exc}", file=sys.stderr)
                continue

            for entry in feed.entries:
                link = entry.get("link", "")
                if not link or link in seen:
                    continue

                pub_date = parse_entry_date(entry)
                if pub_date is None or pub_date < cutoff:
                    continue

                entries.append(
                    {
                        "title": entry.get("title", "(untitled)"),
                        "url": link,
                        "source": source_name,
                        "category": category,
                        "published": pub_date.isoformat(),
                        "summary": (entry.get("summary") or "")[:500],
                    }
                )
                seen[link] = pub_date.isoformat()

            print(
                f"  [{category}] {source_name}: OK ({len(feed.entries)} total entries)"
            )
    return entries


def main() -> None:
    REPORTS_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

    feeds = load_feeds()
    print(
        f"Loaded {sum(len(v) for v in feeds.values())} feeds across {len(feeds)} categories."
    )
    print(f"Fetching feeds (cutoff: {cutoff.isoformat()})...")

    seen = load_seen()
    entries = fetch_feeds(cutoff, seen, feeds)
    save_seen(seen)

    out_file = REPORTS_DIR / f"raw-{today}.json"
    out_file.write_text(json.dumps(entries, indent=2))
    print(f"\nCollected {len(entries)} new entries -> {out_file}")


if __name__ == "__main__":
    main()
