"""Internal company database tool — NL2SQL with a graceful fallback.

This demonstrates how easily CrewAI's NL2SQLTool drops in:

    Set DATABASE_URL to a Postgres connection string and the crew will translate
    the agent's natural-language questions into SQL against your schema. With no
    DATABASE_URL set, the crew still runs end-to-end — the fallback tool reports
    that no internal database is configured and the agent moves on to the public
    sources.

Example connection string (placeholder — never commit real credentials):
    DATABASE_URL=postgresql://user:password@localhost:5432/crm
"""

import os

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class _DBQueryInput(BaseModel):
    question: str = Field(
        description="A natural-language question about the company's internal records"
    )


class NoDatabaseTool(BaseTool):
    """Graceful fallback used when DATABASE_URL is not set."""

    name: str = "Internal Company Database"
    description: str = (
        "Look up existing internal records about the company (CRM, prior deals, "
        "accounts). If no internal database is configured, it says so and the crew "
        "continues with public sources."
    )
    args_schema: type[BaseModel] = _DBQueryInput

    def _run(self, question: str) -> str:
        return (
            "No internal database is configured (DATABASE_URL is not set). "
            "Skipping internal records and proceeding with public sources. "
            "To enable this source, set DATABASE_URL to a Postgres connection string."
        )


def build_internal_db_tool() -> BaseTool:
    """Return an NL2SQL tool if DATABASE_URL is set, else the graceful fallback.

    Swapping in a real database is a one-liner for the workshop attendee: provide
    DATABASE_URL and this function returns a fully-wired NL2SQLTool instead.
    """
    db_uri = os.getenv("DATABASE_URL")
    if db_uri:
        # Imported lazily so the base install doesn't require SQLAlchemy/psycopg
        # unless a database is actually configured.
        from crewai_tools import NL2SQLTool

        return NL2SQLTool(db_uri=db_uri)
    return NoDatabaseTool()
