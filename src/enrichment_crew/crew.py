"""The enrichment crew: three parallel source researchers + a consolidating analyst.

Sources:
  1. The open web       (keyless DuckDuckGo search + website scraping)
  2. A public API       (Wikipedia REST — free, no key)
  3. Internal database  (NL2SQL via DATABASE_URL, with a graceful fallback)
The analyst merges all three into one structured profile + Markdown report.
"""

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.tasks.hallucination_guardrail import HallucinationGuardrail
from crewai_tools import ScrapeWebsiteTool

from enrichment_crew.schemas import EnrichedCompanyProfile
from enrichment_crew.tools.company_api_tool import CompanyInfoAPITool
from enrichment_crew.tools.db_tool import build_internal_db_tool
from enrichment_crew.tools.icp_tool import ICPFitScoreTool
from enrichment_crew.tools.web_search_tool import WebSearchTool


@CrewBase
class EnrichmentCrew():
    """Research a company across three sources in parallel, then consolidate."""

    agents: list[BaseAgent]
    tasks: list[Task]

    # --- Agents -----------------------------------------------------------

    @agent
    def web_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['web_researcher'],  # type: ignore[index]
            tools=[WebSearchTool(), ScrapeWebsiteTool()],
            max_iter=8,
            max_rpm=10,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def api_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['api_researcher'],  # type: ignore[index]
            tools=[CompanyInfoAPITool()],
            max_iter=5,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def internal_data_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['internal_data_researcher'],  # type: ignore[index]
            # NL2SQLTool if DATABASE_URL is set, else a graceful fallback tool.
            tools=[build_internal_db_tool()],
            max_iter=5,
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def enrichment_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['enrichment_analyst'],  # type: ignore[index]
            tools=[ICPFitScoreTool()],
            max_iter=6,
            allow_delegation=False,
            verbose=True,
        )

    # --- Tasks ------------------------------------------------------------

    @task
    def research_web(self) -> Task:
        return Task(
            config=self.tasks_config['research_web'],  # type: ignore[index]
        )

    @task
    def fetch_public_api(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_public_api'],  # type: ignore[index]
        )

    @task
    def query_internal_records(self) -> Task:
        return Task(
            config=self.tasks_config['query_internal_records'],  # type: ignore[index]
        )

    @task
    def compile_report(self) -> Task:
        return Task(
            config=self.tasks_config['compile_report'],  # type: ignore[index]
            context=[
                self.research_web(),
                self.fetch_public_api(),
                self.query_internal_records(),
            ],
            output_pydantic=EnrichedCompanyProfile,
            # Production safety net: the HallucinationGuardrail validates the
            # final report's faithfulness against the gathered research before
            # the task is allowed to complete (faithfulness score 0-10). It's a
            # CrewAI library feature — it runs wherever the crew runs. On AMP,
            # the guardrail's events stream out (llm_guardrail_completed,
            # task_failed) so you can route a hallucination alert to Slack /
            # Datadog / PagerDuty via webhook streaming.
            guardrail=HallucinationGuardrail(
                context=(
                    "The enrichment report must only contain facts supported by "
                    "the research gathered for this company (open-web findings, "
                    "the public company API, and internal records). Every claim "
                    "must be grounded in those sources; anything not supported "
                    "should be marked 'unknown', never fabricated."
                ),
                llm=LLM(model="gpt-4o-mini"),
            ),
        )

    # --- Crew -------------------------------------------------------------

    @crew
    def crew(self) -> Crew:
        """Creates the EnrichmentCrew crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
