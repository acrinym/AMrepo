#!/bin/bash
set -eux

# Detect Codex / Codespaces before cleaning
if [ -n "$CODESPACES" ] || [ -n "$CODEX_ENV" ]; then
  echo "Codex/Codespaces environment detected — cleaning repo."
  git reset --hard
  git clean -fdx
else
  echo "Local environment detected — skipping cleanup."
fi
