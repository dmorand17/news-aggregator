#!/bin/bash
#
# Run the full pipeline locally. Requires OPENROUTER_API_KEY (optionally OPENROUTER_MODEL).

DAY=$(date +%F)

# Run the aggregator (appends to reports/pending.json)
echo "Getting feeds for ${DAY}"
uv run news-aggregator

echo "Running digest generation..."
uv run news-digest
