"""A custom CrewAI tool that scores Ideal Customer Profile (ICP) fit.

This demonstrates the full BaseTool pattern: a Pydantic args schema plus a
deterministic `_run` method. The scoring logic is plain Python — a good example
of pushing deterministic work into a tool instead of asking the LLM to do math.
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Priority industries for our ICP (lowercased for matching).
PRIORITY_INDUSTRIES = {
    "technology", "software", "saas", "financial services", "fintech",
    "banking", "telecom", "telecommunications", "cpg",
    "consumer packaged goods", "healthcare", "life sciences",
}

# Keywords in recent signals that indicate AI / automation investment.
AI_INVESTMENT_KEYWORDS = {
    "ai", "artificial intelligence", "machine learning", "ml", "automation",
    "agent", "agents", "llm", "genai", "generative", "digital transformation",
    "data platform", "cloud migration",
}


class ICPFitInput(BaseModel):
    """Inputs for the ICP fit score."""

    industry: str = Field(description="The company's primary industry")
    employee_estimate: str = Field(
        description="Employee count or size band, e.g. '1200', '500-1000', or 'unknown'"
    )
    recent_signals: str = Field(
        description="Recent signals as free text (funding, hiring, product, tech)"
    )


class ICPFitScoreTool(BaseTool):
    name: str = "ICP Fit Score"
    description: str = (
        "Calculate a 0-100 Ideal Customer Profile fit score from a company's "
        "industry, employee estimate, and a free-text summary of recent signals. "
        "Returns the score and a short rationale."
    )
    args_schema: type[BaseModel] = ICPFitInput

    def _run(self, industry: str, employee_estimate: str, recent_signals: str) -> str:
        score = 0
        reasons: list[str] = []

        # Industry fit (0-40)
        industry_l = (industry or "").lower()
        if any(p in industry_l for p in PRIORITY_INDUSTRIES):
            score += 40
            reasons.append(f"Priority industry ({industry}): +40")
        else:
            score += 10
            reasons.append(f"Non-priority industry ({industry}): +10")

        # Company size (0-35) — parse the first number we find
        size = _first_int(employee_estimate)
        if size is None:
            score += 10
            reasons.append("Company size unknown: +10")
        elif size >= 1000:
            score += 35
            reasons.append(f"Enterprise size (~{size}): +35")
        elif size >= 250:
            score += 25
            reasons.append(f"Mid-market size (~{size}): +25")
        else:
            score += 10
            reasons.append(f"SMB size (~{size}): +10")

        # AI / transformation signals (0-25)
        signals_l = (recent_signals or "").lower()
        hits = sorted({kw for kw in AI_INVESTMENT_KEYWORDS if kw in signals_l})
        if hits:
            bonus = min(25, 10 + 5 * len(hits))
            score += bonus
            reasons.append(f"AI/automation signals {hits}: +{bonus}")
        else:
            reasons.append("No clear AI/automation signals: +0")

        score = max(0, min(100, score))
        return f"ICP_FIT_SCORE={score} | RATIONALE: " + "; ".join(reasons)


def _first_int(text: str) -> int | None:
    """Return the first integer found in a string, ignoring commas."""
    digits = ""
    for ch in (text or "").replace(",", ""):
        if ch.isdigit():
            digits += ch
        elif digits:
            break
    return int(digits) if digits else None
