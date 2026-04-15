"""Financial Comparison sub-agent builder."""

from agents import Agent, ModelSettings, WebSearchTool

from agent_worker.prompts import FINANCIAL_COMPARISON_INSTRUCTIONS

_MODEL = "openai_gpt52"
_SETTINGS = ModelSettings(temperature=0.2)


def build_financials_agent() -> Agent:
    """Construct the Financial Comparison specialist agent.

    Produces a detailed financial comparison of two named companies, covering
    revenue growth, margins, valuation multiples, balance sheet, and free cash
    flow, with a side-by-side summary table.
    """
    return Agent(
        name="Financial Comparison Agent",
        instructions=FINANCIAL_COMPARISON_INSTRUCTIONS,
        model=_MODEL,
        model_settings=_SETTINGS,
        tools=[WebSearchTool()],
    )
