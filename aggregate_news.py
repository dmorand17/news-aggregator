#!/usr/bin/env python3
"""Fetch RSS/Atom feeds from configured sources, filter to last 7 days, de-dupe."""

from __future__ import annotations

import json
import logging
from calendar import timegm
from datetime import datetime, timedelta, timezone
from pathlib import Path

import feedparser
import yaml
from dateutil import parser as dateparser

log = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent
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
    """Save seen URLs, pruning entries older than 14 days."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
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
        for source_name, feed_config in sources.items():
            if isinstance(feed_config, dict):
                url = feed_config["url"]
                category_filter = feed_config.get("category_filter", "").lower()
            else:
                url = feed_config
                category_filter = ""

            try:
                feed = feedparser.parse(url)
            except Exception as exc:
                log.warning("Failed to fetch %s: %s", source_name, exc)
                continue

            for entry in feed.entries:
                link = entry.get("link", "")
                if not link or link in seen:
                    continue

                title = entry.get("title", "(untitled)")

                if category_filter:
                    tags = entry.tags if hasattr(entry, "tags") else []
                    entry_categories = [t.get("term", "").lower() for t in (tags or [])]
                    if not any(category_filter in c for c in entry_categories):
                        continue

                pub_date = parse_entry_date(entry)
                if pub_date is None or pub_date < cutoff:
                    continue

                entries.append(
                    {
                        "title": title,
                        "url": link,
                        "source": source_name,
                        "category": category,
                        "published": pub_date.isoformat(),
                        "summary": (entry.get("summary") or "")[:500],
                    }
                )
                seen[link] = pub_date.isoformat()

            log.info("[%s] %s: OK (%d total entries)", category, source_name, len(feed.entries))
    return entries


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    REPORTS_DIR.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    iso_year, iso_week, _ = now.isocalendar()
    week_label = f"{iso_year}-W{iso_week:02d}"
    cutoff = now - timedelta(days=7)

    feeds = load_feeds()
    log.info(
        "Loaded %d feeds across %d categories.",
        sum(len(v) for v in feeds.values()),
        len(feeds),
    )
    log.info("Fetching feeds (cutoff: %s)...", cutoff.isoformat())

    seen = load_seen()
    entries = fetch_feeds(cutoff, seen, feeds)
    save_seen(seen)

    out_file = REPORTS_DIR / f"raw-{week_label}.json"
    out_file.write_text(json.dumps(entries, indent=2))
    log.info("Collected %d new entries -> %s", len(entries), out_file)


if __name__ == "__main__":
    main()
