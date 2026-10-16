#!/usr/bin/env bash
set -euo pipefail
dest="$HOME/.claude/skills"
mkdir -p "$dest"
cp -R "$(dirname "$0")/skills/." "$dest/"
echo "Installed skills into $dest. Restart Claude Code to load them."
