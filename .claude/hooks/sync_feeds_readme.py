#!/usr/bin/env python3
"""Update the ## Feeds section in README.md from config/feeds.yaml."""

from pathlib import Path
import re
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FEEDS_CONFIG = REPO_ROOT / "config" / "feeds.yaml"
README = REPO_ROOT / "README.md"

START = "<!-- feeds-start -->"
END = "<!-- feeds-end -->"


def build_section(feeds: dict) -> str:
    lines = [START, "", "| Category | Source | Filter |", "| --- | --- | --- |"]
    for category, sources in feeds.items():
        for name, value in sources.items():
            url = value if isinstance(value, str) else value["url"]
            filter_val = value.get("category_filter", "") if isinstance(value, dict) else ""
            filter_col = f"`{filter_val}`" if filter_val else ""
            lines.append(f"| {category} | [{name}]({url}) | {filter_col} |")
    lines.append(f"\n{END}")
    return "\n".join(lines)


def main():
    data = yaml.safe_load(FEEDS_CONFIG.read_text())
    feeds = data.get("feeds", {})
    section = build_section(feeds)

    readme = README.read_text()
    pattern = re.compile(f"{re.escape(START)}.*?{re.escape(END)}", re.DOTALL)

    if pattern.search(readme):
        updated = pattern.sub(section, readme)
    else:
        updated = readme.rstrip() + f"\n\n## Feeds\n\n{section}\n"

    README.write_text(updated)
    print("README.md feeds section updated.")


if __name__ == "__main__":
    main()
