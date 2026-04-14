"""Research agent construction and execution using the OpenAI Agent SDK."""

from agent_worker.config import OPENAI_BASE_URL
from agent_worker.prompts import RESEARCH_AGENT_INSTRUCTIONS
from agents import Agent
from agents import ModelSettings
from agents import Runner
from agents import WebSearchTool
from agents.models.openai_provider import OpenAIProvider
from agents.run import RunConfig
from openai import AsyncOpenAI


def build_research_agent() -> Agent:
    """Construct the thematic research agent with web search capability."""
    return Agent(
        name="TIRA Research Agent",
        instructions=RESEARCH_AGENT_INSTRUCTIONS,
        model="openai_gpt52",
        model_settings=ModelSettings(temperature=0.2),
        tools=[WebSearchTool()],
    )


async def run_research(theme: str) -> str:
    """Execute the research agent for a given investment theme.

    Args:
        theme: The investment theme to research (e.g., "Quantum Computing").

    Returns:
        A Markdown-formatted research report.
    """
    async with AsyncOpenAI(base_url=OPENAI_BASE_URL) as client:
        agent = build_research_agent()
        prompt = f"Conduct comprehensive thematic investment research on: {theme}"
        result = await Runner.run(
            agent,
            prompt,
            run_config=RunConfig(model_provider=OpenAIProvider(openai_client=client)),
        )
        return result.final_output
