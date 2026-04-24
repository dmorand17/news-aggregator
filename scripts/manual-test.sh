#!/bin/bash
#

WEEK=$(python3 -c "from datetime import datetime; d=datetime.now(); print(f'{d.isocalendar()[0]}-W{d.isocalendar()[1]:02d}')")

# Run the aggregator (writes reports/raw-YYYY-WNN.json)
echo "Getting feeds for ${WEEK}"
uv run python aggregate_news.py

echo "Running report generation..."
claude --model claude-sonnet-4-6 \
  --allowedTools "Read,Write,Glob,Grep,WebFetch,WebSearch,Bash(date *),Bash(ls *)" \
  --max-turns 30 \
  --print \
  "Read the raw feed data from reports/raw-${WEEK}.json. \
   Follow the instructions in CLAUDE.md to generate a polished weekly news report. \
   Save a markdown report to reports/${WEEK}.md and an HTML digest to \
   reports/${WEEK}.html. Use templates/digest-template.html as the HTML template. \
   Use WebSearch to find any breaking news that RSS feeds may have missed."
