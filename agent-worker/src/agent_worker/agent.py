"""Orchestrator agent construction and execution for the multi-agent research system."""

from agents import Agent, ModelSettings, Runner
from agents.models.openai_provider import OpenAIProvider
from agents.run import RunConfig
from openai import AsyncOpenAI

from agent_worker.config import OPENAI_BASE_URL
from agent_worker.guardrails.input_guardrails import theme_relevance_guardrail
from agent_worker.guardrails.output_guardrails import report_structure_guardrail
from agent_worker.models import (
    CompanyResearchInput,
    FinancialComparisonInput,
    ThemeInput,
)
from agent_worker.prompts import ORCHESTRATOR_INSTRUCTIONS
from agent_worker.sub_agents.company import build_company_agent
from agent_worker.sub_agents.financials import build_financials_agent
from agent_worker.sub_agents.investment import build_investment_agent
from agent_worker.sub_agents.market import build_market_agent

_MODEL = "openai_gpt52"
_SETTINGS = ModelSettings(temperature=0.2)
_ORCHESTRATOR_MAX_TURNS = 50
_SUB_AGENT_MAX_TURNS = 15


def build_orchestrator() -> Agent:
    """Construct the TIRA Orchestrator with four specialist sub-agents as tools.

    The orchestrator coordinates market dynamics research, investment opportunity
    analysis, company exposure evaluation, and financial comparison through
    the agent-as-tool pattern.
    """
    market_tool = build_market_agent().as_tool(
        tool_name="research_market_dynamics",
        tool_description=(
            "Research market size, growth projections, key drivers, tailwinds, "
            "headwinds, and the competitive landscape for the given investment theme."
        ),
        parameters=ThemeInput,
        max_turns=_SUB_AGENT_MAX_TURNS,
    )
    investment_tool = build_investment_agent().as_tool(
        tool_name="research_investment_opportunities",
        tool_description=(
            "Evaluate the investment thesis, portfolio positioning strategies, "
            "relevant ETFs and vehicles, and a structured risk register for the theme."
        ),
        parameters=ThemeInput,
        max_turns=_SUB_AGENT_MAX_TURNS,
    )
    company_tool = build_company_agent().as_tool(
        tool_name="research_company_exposure",
        tool_description=(
            "Identify publicly listed companies exposed to the theme, assess their "
            "competitive moat and positioning, and select the top two most prospective "
            "companies for detailed financial analysis."
        ),
        parameters=CompanyResearchInput,
        max_turns=_SUB_AGENT_MAX_TURNS,
    )
    financials_tool = build_financials_agent().as_tool(
        tool_name="research_financial_comparison",
        tool_description=(
            "Produce a detailed financial comparison of two named companies, covering "
            "revenue growth, margins, valuation multiples, balance sheet, and "
            "free cash flow, with a side-by-side summary table."
        ),
        parameters=FinancialComparisonInput,
        max_turns=_SUB_AGENT_MAX_TURNS,
    )
    return Agent(
        name="TIRA Orchestrator",
        instructions=ORCHESTRATOR_INSTRUCTIONS,
        model=_MODEL,
        model_settings=_SETTINGS,
        tools=[market_tool, investment_tool, company_tool, financials_tool],
        input_guardrails=[theme_relevanWce_guardrail],
        output_guardrails=[report_structure_guardrail],
    )


async def run_research(theme: str) -> str:
    """Execute the multi-agent research pipeline for a given investment theme.

    Orchestrates four specialist sub-agents (Market Dynamics, Investment
    Opportunities, Company Exposure, Financial Comparison) and returns a
    synthesised Markdown research report.

    Args:
        theme: The investment theme to research (e.g., "Quantum Computing").

    Returns:
        A Markdown-formatted institutional research report.
    """
    async with AsyncOpenAI(base_url=OPENAI_BASE_URL) as client:
        orchestrator = build_orchestrator()
        prompt = (
            f"Conduct comprehensive thematic investment research on: {theme}. "
            f"Follow the procedure in your instructions."
        )
        result = await Runner.run(
            orchestrator,
            prompt,
            max_turns=_ORCHESTRATOR_MAX_TURNS,
            run_config=RunConfig(
                model_provider=OpenAIProvider(openai_client=client),
                workflow_name=f"TIRA Research: {theme}",
            ),
        )
        return result.final_output
