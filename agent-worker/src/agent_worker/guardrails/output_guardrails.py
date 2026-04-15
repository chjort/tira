"""Output guardrail for validating research report structural completeness.

Uses a fast, code-based check (no LLM call) to verify the generated report
contains all required sections and meets a minimum length threshold.  This
runs on every production report without adding latency or cost.
"""

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunContextWrapper,
    output_guardrail,
)
from pydantic import BaseModel, Field

_REQUIRED_HEADINGS = [
    "Executive Summary",
    "Theme Overview",
    "Market Dynamics",
    "Investment Opportunities",
    "Key Companies",
    "Financial Comparison",
    "Investment Implications",
]

_MIN_WORD_COUNT = 500


class ReportValidationOutput(BaseModel):
    """Structured result of the report structure validation."""

    is_valid_report: bool = Field(
        description="True if the report passes all structural checks.",
    )
    missing_sections: list[str] = Field(
        description="Section headings that are missing from the report.",
    )
    word_count: int = Field(
        description="Total word count of the report.",
    )


@output_guardrail
async def report_structure_guardrail(
    ctx: RunContextWrapper,
    agent: Agent,
    output: str,
) -> GuardrailFunctionOutput:
    """Validate that the report has all required sections and sufficient length."""
    report_lower = output.lower()
    missing = [h for h in _REQUIRED_HEADINGS if h.lower() not in report_lower]
    word_count = len(output.split())
    is_valid = len(missing) == 0 and word_count >= _MIN_WORD_COUNT

    return GuardrailFunctionOutput(
        output_info=ReportValidationOutput(
            is_valid_report=is_valid,
            missing_sections=missing,
            word_count=word_count,
        ),
        tripwire_triggered=not is_valid,
    )
