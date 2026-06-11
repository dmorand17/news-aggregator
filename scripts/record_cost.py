#!/usr/bin/env python3
"""Append a cost/token record for a Claude Code run to data/costs.json.

Reads the execution log written by anthropics/claude-code-action (path passed
as argv[1]), extracts the final ``result`` message's cost and usage, and appends
a dated record to ``data/costs.json``. Also writes a human-readable summary to
``$GITHUB_STEP_SUMMARY`` and emits ``cost_line`` to ``$GITHUB_OUTPUT`` for the
Slack step.

The execution-log schema is not formally documented, so parsing is defensive:
the file may be a JSON array of messages or newline-delimited JSON, and any
field may be absent. Missing data degrades to nulls rather than failing the run.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
COSTS_FILE = REPO_ROOT / "data" / "costs.json"


def load_messages(raw: str) -> list[dict]:
    """Parse the execution log as either a JSON array or newline-delimited JSON."""
    raw = raw.strip()
    if not raw:
        return []
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [m for m in data if isinstance(m, dict)]
        if isinstance(data, dict):
            # Could be a single object or a wrapper containing messages.
            for key in ("messages", "output", "events"):
                inner = data.get(key)
                if isinstance(inner, list):
                    return [m for m in inner if isinstance(m, dict)]
            return [data]
    except json.JSONDecodeError:
        pass
    # Fall back to newline-delimited JSON (stream-json).
    messages = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            messages.append(obj)
    return messages


def find_result(messages: list[dict]) -> dict | None:
    """Return the final message that carries cost/usage data."""
    for msg in reversed(messages):
        if msg.get("type") == "result":
            return msg
    # Some logs omit an explicit type; fall back to any message with cost/usage.
    for msg in reversed(messages):
        if "total_cost_usd" in msg or "usage" in msg:
            return msg
    return None


def extract_record(result: dict | None) -> dict:
    """Pull cost/token fields from a result message, tolerating absences."""
    result = result or {}
    usage = result.get("usage") or {}
    return {
        "cost_usd": result.get("total_cost_usd"),
        "input_tokens": usage.get("input_tokens"),
        "output_tokens": usage.get("output_tokens"),
        "cache_read_tokens": usage.get("cache_read_input_tokens"),
        "cache_creation_tokens": usage.get("cache_creation_input_tokens"),
        "num_turns": result.get("num_turns"),
    }


def load_history() -> list[dict]:
    if COSTS_FILE.exists():
        try:
            data = json.loads(COSTS_FILE.read_text())
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass
    return []


def fmt_usd(value) -> str:
    return f"${value:.4f}" if isinstance(value, (int, float)) else "n/a"


def fmt_int(value) -> str:
    return f"{value:,}" if isinstance(value, (int, float)) else "n/a"


def main() -> None:
    exec_file = sys.argv[1] if len(sys.argv) > 1 else ""
    now = datetime.now(timezone.utc)

    record = extract_record(None)
    if exec_file and Path(exec_file).exists():
        messages = load_messages(Path(exec_file).read_text())
        record = extract_record(find_result(messages))
    else:
        print(f"WARN execution file not found: {exec_file!r}", file=sys.stderr)

    record = {"date": now.strftime("%Y-%m-%d"), "timestamp": now.isoformat(), **record}

    history = load_history()
    history.append(record)
    COSTS_FILE.parent.mkdir(exist_ok=True)
    COSTS_FILE.write_text(json.dumps(history, indent=2) + "\n")

    total_cost = sum(r["cost_usd"] for r in history if isinstance(r.get("cost_usd"), (int, float)))
    tokens = (record.get("input_tokens") or 0) + (record.get("output_tokens") or 0)
    cost_line = (
        f"Cost: {fmt_usd(record['cost_usd'])} · "
        f"{fmt_int(tokens) if tokens else 'n/a'} tokens · "
        f"{record.get('num_turns', 'n/a')} turns "
        f"(total to date: {fmt_usd(total_cost)})"
    )
    print(cost_line)

    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as f:
            f.write(f"### 💸 Run cost\n\n")
            f.write("| Metric | Value |\n|---|---|\n")
            f.write(f"| Cost (est.) | {fmt_usd(record['cost_usd'])} |\n")
            f.write(f"| Input tokens | {fmt_int(record['input_tokens'])} |\n")
            f.write(f"| Output tokens | {fmt_int(record['output_tokens'])} |\n")
            f.write(f"| Cache read | {fmt_int(record['cache_read_tokens'])} |\n")
            f.write(f"| Turns | {record.get('num_turns', 'n/a')} |\n")
            f.write(f"| Total to date | {fmt_usd(total_cost)} |\n")

    output = os.environ.get("GITHUB_OUTPUT")
    if output:
        with open(output, "a") as f:
            f.write(f"cost_line={cost_line}\n")


if __name__ == "__main__":
    main()
