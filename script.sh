#!/bin/bash
#

# Run the aggregator (writes reports/raw-YYYY-MM-DD.json)
echo "Getting blogs for $(date +%Y-%m-%d)"
uv run python aggregate_news.py

echo "Running report generation..."
claude --model claude-sonnet-4-6 \
  --allowedTools "Read,Write,Glob,Grep,WebFetch,WebSearch,Bash(date *),Bash(ls *)" \
  --print \
  "Read the raw feed data from reports/raw-$(date +%Y-%m-%d).json. \
   Follow the instructions in CLAUDE.md to generate a polished daily news report. \
   Save a markdown report to reports/$(date +%Y-%m-%d).md and an HTML digest to \
   reports/$(date +%Y-%m-%d).html. Use templates/digest-template.html as the HTML template. \
   Use WebSearch to find any breaking news that RSS feeds may have missed."
