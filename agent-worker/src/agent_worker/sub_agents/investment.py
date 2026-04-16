"""Investment Opportunities sub-agent builder."""

from agents import Agent, ModelSettings, WebSearchTool

from agent_worker.config import AGENT_MODEL
from agent_worker.prompts import INVESTMENT_OPPORTUNITIES_INSTRUCTIONS

_SETTINGS = ModelSettings(temperature=0.2)


def build_investment_agent() -> Agent:
    """Construct the Investment Opportunities specialist agent.

    Evaluates the investment thesis, portfolio positioning strategies,
    relevant ETFs and vehicles, and a structured risk register for a theme.
    """
    return Agent(
        name="Investment Opportunities Agent",
        instructions=INVESTMENT_OPPORTUNITIES_INSTRUCTIONS,
        model=AGENT_MODEL,
        model_settings=_SETTINGS,
        tools=[WebSearchTool()],
    )
