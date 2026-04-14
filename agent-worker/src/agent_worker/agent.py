"""Research agent construction and execution using the OpenAI Agent SDK."""

from agents import Agent, ModelSettings, Runner, WebSearchTool

from agent_worker.prompts import RESEARCH_AGENT_INSTRUCTIONS


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
    agent = build_research_agent()
    prompt = f"Conduct comprehensive thematic investment research on: {theme}"
    result = await Runner.run(agent, prompt)
    return result.final_output
