"""Public company-info API tool.

Uses the free, no-key Wikipedia REST API to pull public background on a company.
The endpoint is isolated in one place so it is a one-line swap to another free,
no-key company source:

    - SEC EDGAR  (https://data.sec.gov)         — US public-company filings/financials
    - GLEIF      (https://api.gleif.org)         — global legal-entity (LEI) records

Uses only the Python standard library (urllib) so the repo runs with no extra
dependency, and fails gracefully so a lookup miss never breaks the crew.
"""

import json
import urllib.parse
import urllib.request

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
_SEARCH_URL = (
    "https://en.wikipedia.org/w/api.php"
    "?action=opensearch&limit=1&namespace=0&format=json&search={q}"
)
_HEADERS = {"User-Agent": "CrewAI-Workshop/1.0 (enrichment lab)"}


class CompanyInfoInput(BaseModel):
    company: str = Field(description="The company name to look up, e.g. 'Stripe'")


class CompanyInfoAPITool(BaseTool):
    name: str = "Company Info API"
    description: str = (
        "Fetch public background on a company from the Wikipedia REST API "
        "(free, no API key). Returns a short description, a summary, and the "
        "source URL. Use this for neutral, citable company background."
    )
    args_schema: type[BaseModel] = CompanyInfoInput

    def _run(self, company: str) -> str:
        try:
            title = self._resolve_title(company) or company
            url = _SUMMARY_URL.format(
                title=urllib.parse.quote(title.replace(" ", "_"))
            )
            data = self._get_json(url)
            if not data or data.get("title") == "Not found.":
                return f"No public encyclopedia entry found for '{company}'."
            description = data.get("description", "")
            summary = data.get("extract", "")
            source = (
                data.get("content_urls", {})
                .get("desktop", {})
                .get("page", "")
            )
            return (
                f"DESCRIPTION: {description}\n"
                f"SUMMARY: {summary}\n"
                f"SOURCE: {source}"
            )
        except Exception as exc:  # network/parse issues never break the crew
            return f"Company Info API unavailable ({exc}). Proceeding without it."

    def _resolve_title(self, query: str) -> str | None:
        """Resolve a company name to its best-matching article title."""
        try:
            data = self._get_json(_SEARCH_URL.format(q=urllib.parse.quote(query)))
            # opensearch returns [query, [titles], [descriptions], [urls]]
            if isinstance(data, list) and len(data) >= 2 and data[1]:
                return data[1][0]
        except Exception:
            return None
        return None

    def _get_json(self, url: str):
        request = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
