#!/bin/bash
#

DAY=$(date +%F)

# Run the aggregator (writes reports/raw-YYYY-MM-DD.json)
echo "Getting feeds for ${DAY}"
uv run news-aggregator

echo "Running digest generation..."
claude --model claude-sonnet-4-6 \
  --allowedTools "Read,Write,Glob,Grep,WebFetch,WebSearch,Bash(date *),Bash(ls *)" \
  --max-turns 30 \
  --print \
  "Read the raw feed data from reports/raw-${DAY}.json. \
   Follow the instructions in CLAUDE.md to generate a polished daily news digest. \
   Save a markdown post to content/posts/${DAY}.md including the required Hugo \
   front matter. \
   Use WebSearch to find any breaking news that RSS feeds may have missed."
