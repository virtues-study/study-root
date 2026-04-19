#!/usr/bin/env bash

# Loop through all .md files in the current directory
for f in *.md; do
    # Skip if no .md files exist (prevents literal "*.md")
    [ -e "$f" ] || continue

    # Extract filename without extension
    name="${f%.md}"

    # Output in desired format
    echo "[${name}](related/${name})"
done
