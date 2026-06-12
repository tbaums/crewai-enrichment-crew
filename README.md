# Enrichment Crew — Instructor Solution

The complete, verified final state of [the lab](../assets/enrichment-crew-guide.md) (end of
Section 5). Use it to smoke-test before a delivery, to demo the finished
product, or to unblock an attendee who is too far behind to catch up by
pasting section checkpoints.

## Run it

```bash
crewai install
echo 'OPENAI_API_KEY=sk-...' >> .env   # plus MODEL=gpt-4o-mini if you like
crewai run                              # default company: CrewAI
uv run run_crew "Stripe" "stripe.com"   # any company
```

Outputs land in `output/company_report.md` and `output/enriched_profile.json`.

No other keys are required: web search is keyless DuckDuckGo (`ddgs`), the
public API is Wikipedia REST, and the internal-database source degrades
gracefully unless `DATABASE_URL` points at a Postgres.

Last verified end-to-end 2026-06-11 against `crewai==1.14.7` + `gpt-4o-mini`.
