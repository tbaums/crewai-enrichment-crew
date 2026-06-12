"""Keyless web search tool built on DuckDuckGo (via the `ddgs` package).

A custom CrewAI tool has four parts the framework and the model rely on:
  - name:        a short identifier
  - description: what the tool does — written FOR THE MODEL, which reads it
                 to decide when to call the tool
  - args_schema: a Pydantic model of the arguments the model must supply
  - _run:        the implementation, called with validated arguments

No API key required, which makes it workshop-safe.
"""

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class WebSearchInput(BaseModel):
    query: str = Field(description="The search query, e.g. 'CrewAI funding 2025'")


class WebSearchTool(BaseTool):
    name: str = "Web Search"
    description: str = (
        "Search the web (DuckDuckGo, no API key) and get back the top results: "
        "title, URL, and a snippet for each. Use focused keyword queries, and "
        "follow up by scraping the most promising URL when a snippet is not enough."
    )
    args_schema: type[BaseModel] = WebSearchInput

    def _run(self, query: str) -> str:
        try:
            from ddgs import DDGS

            results = DDGS().text(query, max_results=8)
            if not results:
                return f"No results for '{query}'. Try different keywords."
            return "\n\n".join(
                f"TITLE: {r.get('title', '')}\nURL: {r.get('href', '')}\nSNIPPET: {r.get('body', '')}"
                for r in results
            )
        except Exception as exc:  # a flaky search must never break the crew
            return f"Web search unavailable ({exc}). Proceed with other sources."
