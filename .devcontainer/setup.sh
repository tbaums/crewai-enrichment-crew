#!/usr/bin/env bash
# Codespace provisioning for the CrewAI workshop.
# Runs once when the codespace is created (onCreateCommand) — and during
# prebuilds, if prebuilds are enabled for the repo, so attendees skip it.
set -euo pipefail

echo "==> Installing uv"
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

echo "==> Installing the CrewAI CLI (pinned — see labs/workshop-setup)"
uv tool install crewai==1.14.7

echo "==> Pre-warming the package cache so 'crewai install' is fast in the labs"
uv venv /tmp/warmup
VIRTUAL_ENV=/tmp/warmup uv pip install 'crewai[tools]==1.14.7' 'ddgs>=9.0' >/dev/null
rm -rf /tmp/warmup

echo "==> Done. uv $(uv --version | cut -d' ' -f2), $(crewai --version 2>/dev/null || echo 'crewai CLI installed')"
