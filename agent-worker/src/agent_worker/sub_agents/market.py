"""Market Dynamics sub-agent builder."""

from agents import Agent, ModelSettings, WebSearchTool

from agent_worker.prompts import MARKET_DYNAMICS_INSTRUCTIONS

_MODEL = "openai_gpt52"
_SETTINGS = ModelSettings(temperature=0.2)


def build_market_agent() -> Agent:
    """Construct the Market Dynamics specialist agent.

    Researches market size, growth projections, key drivers, tailwinds,
    headwinds, and the competitive landscape for a given investment theme.
    """
    return Agent(
        name="Market Dynamics Agent",
        instructions=MARKET_DYNAMICS_INSTRUCTIONS,
        model=_MODEL,
        model_settings=_SETTINGS,
        tools=[WebSearchTool()],
    )
