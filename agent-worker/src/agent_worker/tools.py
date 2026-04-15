"""Custom web search tool for the Novo Nordisk AI Marketplace.

The default ``WebSearchTool`` from the OpenAI Agents SDK does not work with
the marketplace proxy.  This module provides a drop-in replacement that calls
the marketplace's ``web_search_preview`` capability via the Responses API.
"""

from agent_worker.config import OPENAI_BASE_URL
from agents import function_tool
from openai import OpenAI
from openai.types.responses import WebSearchPreviewToolParam

_WEB_SEARCH_MODEL = "gemini_3_flash"
_SEARCH_CONTEXT_SIZE = "low"
_CLIENT_TIMEOUT = 120
_CLIENT_MAX_RETRIES = 3


@function_tool
def web_search(query: str) -> str:
    """Search the web for current information on a topic.

    Queries the Novo Nordisk AI Marketplace web search API and returns a
    text summary incorporating the search results.

    Args:
        query: The search query to look up on the web.
    """
    client = OpenAI(
        base_url=OPENAI_BASE_URL,
        timeout=_CLIENT_TIMEOUT,
        max_retries=_CLIENT_MAX_RETRIES,
    )
    try:
        response = client.responses.create(
            model=_WEB_SEARCH_MODEL,
            instructions="Always use the web search tool to answer queries.",
            input=query,
            tools=[
                WebSearchPreviewToolParam(
                    type="web_search_preview",
                    search_content_types=["text"],
                    search_context_size=_SEARCH_CONTEXT_SIZE,
                )
            ],
        )
        return response.output_text
    except Exception as exc:
        return f"Web search failed: {exc}"
