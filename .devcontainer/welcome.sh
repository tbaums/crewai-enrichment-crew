#!/usr/bin/env bash
# Shown every time a terminal attaches to the codespace.
cat <<'EOF'

  ── CrewAI Workshop — Enrichment Crew ─────────────────────────────────
  This codespace is pre-provisioned: uv + the CrewAI CLI are installed,
  and the enrichment crew is right here at the repo root.

  Quick check:    crewai --version

  1) Load your workshop credentials (key on your handout / the screen):
       CURL_URL='<url-from-handout>' bash scripts/load-creds.sh
       source crewai-creds.env
     (no URL? paste the file in: bash scripts/load-creds.sh)
     Re-run the `source` line in every new terminal.

  2) Sign in to CrewAI AMP (opens a browser / device code):
       crewai login

  Then follow the Lab 1 guide your instructor shared. Run the crew with:
       crewai install && crewai run
  and deploy it (Section 6) with:
       crewai deploy create
  ──────────────────────────────────────────────────────────────────────

EOF
