"""Company Exposure sub-agent builder."""

from agents import Agent, ModelSettings, WebSearchTool

from agent_worker.config import AGENT_MODEL
from agent_worker.prompts import COMPANY_EXPOSURE_INSTRUCTIONS

_SETTINGS = ModelSettings(temperature=0.2)


def build_company_agent() -> Agent:
    """Construct the Company Exposure specialist agent.

    Identifies publicly listed companies exposed to a theme, evaluates their
    competitive moat and positioning, and selects the top two most prospective
    companies for detailed financial analysis.
    """
    return Agent(
        name="Company Exposure Agent",
        instructions=COMPANY_EXPOSURE_INSTRUCTIONS,
        model=AGENT_MODEL,
        model_settings=_SETTINGS,
        tools=[WebSearchTool()],
    )
