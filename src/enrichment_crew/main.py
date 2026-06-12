#!/usr/bin/env python
"""Entry point for the enrichment crew.

Run with `crewai run` (default company), or pick any company:
    uv run run_crew "Stripe" "stripe.com"
"""

import sys
import warnings
from pathlib import Path

from enrichment_crew.crew import EnrichmentCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

DEFAULT_COMPANY = "CrewAI"
DEFAULT_DOMAIN = "crewai.com"


def run():
    """Kick off the crew for one company and write the outputs."""
    company = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_COMPANY
    domain = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DOMAIN

    out_dir = Path("output")
    out_dir.mkdir(exist_ok=True)

    inputs = {"company": company, "domain": domain}
    print(f"\nEnriching: {company} ({domain})\n" + "-" * 40)

    result = EnrichmentCrew().crew().kickoff(inputs=inputs)

    if result.pydantic:
        profile = result.pydantic
        # Write the human-readable report and the structured JSON.
        (out_dir / "company_report.md").write_text(profile.markdown_report, encoding="utf-8")
        (out_dir / "enriched_profile.json").write_text(
            profile.model_dump_json(indent=2), encoding="utf-8"
        )
        print("\n=== SUMMARY ===")
        print(f"Industry:   {profile.industry}")
        print(f"HQ:         {profile.headquarters}")
        print(f"Size:       {profile.employee_count_estimate}")
        print(f"ICP score:  {profile.icp_fit_score}/100 — {profile.icp_fit_rationale}")
        print(f"Next step:  {profile.recommended_next_action}")
        print("\nWrote output/company_report.md and output/enriched_profile.json")
    else:
        # Fallback if structured parsing didn't occur.
        (out_dir / "company_report.md").write_text(result.raw, encoding="utf-8")
        print("\n" + result.raw)
        print("\nWrote output/company_report.md")


# The remaining entry points are part of the scaffold; we don't use them in
# this lab, but they must exist because pyproject.toml points at them.

def train():
    raise NotImplementedError("Not used in this lab.")


def replay():
    raise NotImplementedError("Not used in this lab.")


def test():
    raise NotImplementedError("Not used in this lab.")


def run_with_trigger():
    raise NotImplementedError("Not used in this lab.")
