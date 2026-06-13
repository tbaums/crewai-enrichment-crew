"""Structured output schema for the enrichment crew.

`output_pydantic` on the final task makes the crew return this validated
object instead of free prose — the difference between a demo and something
the next system (a CRM, a dashboard, an API) can actually consume.
"""

from pydantic import BaseModel, Field


class EnrichedCompanyProfile(BaseModel):
    """The consolidated, decision-ready profile the crew produces."""

    company_name: str = Field(description="Official company name")
    domain: str = Field(description="Primary web domain")
    description: str = Field(description="One-paragraph description of what the company does")
    industry: str = Field(description="Primary industry / sub-industry")
    headquarters: str = Field(description="Headquarters location, or 'unknown'")
    employee_count_estimate: str = Field(description="Employee count or size band, or 'unknown'")
    founded_year: str = Field(default="unknown", description="Founding year, or 'unknown'")
    business_model: str = Field(description="e.g. B2B SaaS, marketplace, services")
    key_products: list[str] = Field(default_factory=list, description="Key products or services")

    # Per-source findings, so the consolidated report is traceable to each source.
    recent_signals: list[str] = Field(
        default_factory=list,
        description="Recent web signals: funding, product, leadership, hiring",
    )
    public_api_summary: str = Field(
        default="",
        description="Background from the public company-info API",
    )

    # Scoring + recommendation.
    icp_fit_score: int = Field(ge=0, le=100, description="0-100 Ideal Customer Profile fit score")
    icp_fit_rationale: str = Field(description="Why this score — the reasoning behind the fit")
    recommended_next_action: str = Field(description="One concrete next action for the sales team")
    sources: list[str] = Field(default_factory=list, description="Source URLs used")

    # The human-readable consolidated report (Markdown).
    markdown_report: str = Field(
        description="A polished consolidated enrichment report in Markdown, "
        "combining all sources into a readable brief."
    )
