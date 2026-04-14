"""Pydantic input schemas for sub-agent tool calls."""

from pydantic import BaseModel, Field


class ThemeInput(BaseModel):
    """Input schema shared by Market Dynamics and Investment Opportunities agents."""

    theme: str = Field(..., description="The investment theme to research.")


class CompanyResearchInput(BaseModel):
    """Input schema for the Company Exposure agent."""

    theme: str = Field(..., description="The investment theme.")
    market_context: str = Field(
        ...,
        description=(
            "Summary of market size, CAGR, key drivers, and competitive landscape "
            "from the Market Dynamics analysis."
        ),
    )


class FinancialComparisonInput(BaseModel):
    """Input schema for the Financial Comparison agent."""

    theme: str = Field(..., description="The investment theme.")
    company_a: str = Field(..., description="Name of the first company to compare.")
    company_b: str = Field(..., description="Name of the second company to compare.")
    company_context: str = Field(
        ...,
        description=(
            "Key facts about each company's exposure and moat from the "
            "Company Exposure analysis."
        ),
    )
