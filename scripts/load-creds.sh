#!/usr/bin/env bash
# Load workshop credentials into the codespace at lab time.
#
# Keys are NEVER baked into the image. At the workshop you get a creds file
# (OPENAI_API_KEY=... and any others) either as a URL on your handout or as
# text to paste. This script writes it to ./crewai-creds.env, which you then
# `source` to export the variables into your shell.
#
# Run it with bash directly (no chmod needed):
#
#   # Option A — fetch from a URL (on your handout / the screen):
#   CURL_URL='https://example.com/workshop/creds.env' bash scripts/load-creds.sh
#
#   # Option B — paste the file in: run with no URL, paste, then Ctrl-D:
#   bash scripts/load-creds.sh
#
#   # Option C — point at a file you already saved:
#   bash scripts/load-creds.sh path/to/creds.env
#
# Then, in THIS terminal (and any new one), export the vars:
#
#   source crewai-creds.env
#
# The file is written to the repo root and is git-ignored — do not commit it.
set -euo pipefail

OUT="crewai-creds.env"

if [[ -n "${CURL_URL:-}" ]]; then
  echo "==> Fetching credentials from CURL_URL"
  curl -fsSL "$CURL_URL" -o "$OUT"
elif [[ "${1:-}" != "" ]]; then
  echo "==> Copying credentials from $1"
  cp "$1" "$OUT"
else
  echo "==> Paste your creds file (KEY=value per line), then press Ctrl-D:"
  cat > "$OUT"
fi

if [[ ! -s "$OUT" ]]; then
  echo "error: $OUT is empty — no credentials loaded." >&2
  rm -f "$OUT"
  exit 1
fi

# Make sure we never commit secrets.
if [[ -d .git ]] && ! grep -qxF "$OUT" .gitignore 2>/dev/null; then
  echo "$OUT" >> .gitignore
  echo "==> Added $OUT to .gitignore"
fi

KEYS=$(grep -cE '^[A-Za-z_][A-Za-z0-9_]*=' "$OUT" || true)
echo "==> Wrote $OUT ($KEYS variable(s)). Now run:"
echo
echo "    source $OUT"
echo
echo "    (re-run that in every new terminal)"
