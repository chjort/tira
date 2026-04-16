"""Model-based scorers using LLM-as-judge for qualitative evaluation.

Each scorer is decorated with ``@scorer`` from ``mlflow.genai`` and delegates
to a ``make_judge`` instance that evaluates the report on a 1-5 integer scale.
The judge model and base URL are read from ``agent_worker.config``.
"""

from agent_worker import config
from mlflow.genai import make_judge
from mlflow.genai.scorers import scorer

# ---------------------------------------------------------------------------
# Judge definitions (created once at module level)
# ---------------------------------------------------------------------------

_groundedness_judge = make_judge(
    name="groundedness",
    instructions=(
        "You are an expert financial research reviewer.\n\n"
        "Evaluate the following investment research report for **groundedness**: "
        "the degree to which every factual claim is supported by an explicitly "
        "cited source.\n\n"
        "Report:\n{{ outputs }}\n\n"
        "Score on a 1-5 integer scale:\n"
        "5 = Every quantitative claim and factual statement has a specific, named "
        "source attribution (e.g. 'BloombergNEF estimates', 'according to IDC').\n"
        "4 = Most claims are cited; only minor statements lack attribution.\n"
        "3 = About half the claims have citations; some important figures are unsourced.\n"
        "2 = Few claims are cited; most data appears without attribution.\n"
        "1 = Virtually no source citations; claims are unsubstantiated.\n\n"
        "Return ONLY the integer score."
    ),
    model=config.EVAL_JUDGE_MODEL,
    base_url=config.OPENAI_BASE_URL,
    feedback_value_type=int,
    inference_params={"temperature": 0.0},
)

_source_quality_judge = make_judge(
    name="source_quality",
    instructions=(
        "You are an expert financial research reviewer.\n\n"
        "Evaluate the following investment research report for **source quality**: "
        "the credibility and authority of the sources cited.\n\n"
        "Report:\n{{ outputs }}\n\n"
        "Acceptable institutional sources include: Bloomberg, BloombergNEF, Reuters, "
        "McKinsey, BCG, Gartner, IDC, SEC filings, company 10-K/annual reports, "
        "IEA, IRENA, Wood Mackenzie, FactSet, Refinitiv, Grand View Research, "
        "MarketsandMarkets.\n"
        "Unacceptable sources: Wikipedia, personal blogs, unverifiable references, "
        "social media, unnamed analysts.\n\n"
        "Score on a 1-5 integer scale:\n"
        "5 = All cited sources are institutional-grade and authoritative.\n"
        "4 = Mostly institutional sources with minor secondary references.\n"
        "3 = Mix of credible and non-credible sources.\n"
        "2 = Mostly blogs, Wikipedia, or vague attributions.\n"
        "1 = No credible sources cited.\n\n"
        "Return ONLY the integer score."
    ),
    model=config.EVAL_JUDGE_MODEL,
    base_url=config.OPENAI_BASE_URL,
    feedback_value_type=int,
    inference_params={"temperature": 0.0},
)

_coverage_completeness_judge = make_judge(
    name="coverage_completeness",
    instructions=(
        "You are an expert financial research reviewer.\n\n"
        "Evaluate the following investment research report for **coverage "
        "completeness**: whether all required sections are present and contain "
        "sufficient analytical depth.\n\n"
        "Report:\n{{ outputs }}\n\n"
        "The report MUST contain these sections with substantive content:\n"
        "1. Executive Summary\n"
        "2. Theme Overview & Definition\n"
        "3. Market Dynamics (with Market Size, Drivers, Headwinds, Competitive "
        "Landscape subsections)\n"
        "4. Investment Opportunities (with Thesis, Positioning, Risk Factors "
        "subsections)\n"
        "5. Key Companies & Exposure (with Universe, Moat Analysis, Top Two "
        "subsections)\n"
        "6. Financial Comparison (detailed side-by-side analysis)\n"
        "7. Investment Implications & Conclusion\n\n"
        "Score on a 1-5 integer scale:\n"
        "5 = All sections present with detailed, specific, analytical content.\n"
        "4 = All sections present but one or two are thinner than expected.\n"
        "3 = Most sections present; some lack analytical depth.\n"
        "2 = Several sections missing or severely underdeveloped.\n"
        "1 = Major sections missing; report is incomplete.\n\n"
        "Return ONLY the integer score."
    ),
    model=config.EVAL_JUDGE_MODEL,
    base_url=config.OPENAI_BASE_URL,
    feedback_value_type=int,
    inference_params={"temperature": 0.0},
)

_factual_specificity_judge = make_judge(
    name="factual_specificity",
    instructions=(
        "You are an expert financial research reviewer.\n\n"
        "Evaluate the following investment research report for **factual "
        "specificity**: whether numerical facts and financial figures are specific, "
        "dated, include units, and appear verifiable.\n\n"
        "Report:\n{{ outputs }}\n\n"
        "Good examples: '$1.2B revenue in FY2024', '23.5% CAGR from 2024-2030 "
        "(Grand View Research)', 'P/E of 34.2x (trailing)'.\n"
        "Bad examples: 'strong revenue growth', 'significant market opportunity', "
        "'around $X billion', 'high margins'.\n\n"
        "Score on a 1-5 integer scale:\n"
        "5 = All figures have exact values with units, time period, and source.\n"
        "4 = Most figures are specific; only minor data points lack precision.\n"
        "3 = Mixed — some figures are precise, others are vague approximations.\n"
        "2 = Most figures are vague or lack units/dates.\n"
        "1 = Virtually no specific figures; report relies on qualitative language.\n\n"
        "Return ONLY the integer score."
    ),
    model=config.EVAL_JUDGE_MODEL,
    base_url=config.OPENAI_BASE_URL,
    feedback_value_type=int,
    inference_params={"temperature": 0.0},
)


# ---------------------------------------------------------------------------
# Scorer functions
# ---------------------------------------------------------------------------


@scorer
def groundedness_score(inputs: dict, outputs: str) -> list:
    """Evaluate whether claims in the report are grounded in cited sources."""
    return _groundedness_judge(inputs=inputs, outputs=outputs)


@scorer
def source_quality_score(inputs: dict, outputs: str) -> list:
    """Evaluate the credibility of sources cited in the report."""
    return _source_quality_judge(inputs=inputs, outputs=outputs)


@scorer
def coverage_completeness_score(inputs: dict, outputs: str) -> list:
    """Evaluate depth and completeness of all report sections."""
    return _coverage_completeness_judge(inputs=inputs, outputs=outputs)


@scorer
def factual_specificity_score(inputs: dict, outputs: str) -> list:
    """Evaluate whether numerical facts are specific, dated, and verifiable."""
    return _factual_specificity_judge(inputs=inputs, outputs=outputs)
