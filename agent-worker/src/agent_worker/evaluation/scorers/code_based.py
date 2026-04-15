"""Code-based scorers for structural and quantitative evaluation of research reports.

Each scorer is decorated with ``@scorer`` from ``mlflow.genai`` and receives
``outputs`` (the Markdown report string) and ``expectations`` (metadata from the
evaluation dataset row).  Scorers return a ``Feedback`` object or a plain numeric
/ boolean value.
"""

import re

from mlflow.entities import Feedback
from mlflow.genai.scorers import scorer

# ---------------------------------------------------------------------------
# Section / subsection presence
# ---------------------------------------------------------------------------

_REQUIRED_SECTIONS = [
    "Executive Summary",
    "Theme Overview",
    "Market Dynamics",
    "Investment Opportunities",
    "Key Companies",
    "Financial Comparison",
    "Investment Implications",
]


@scorer
def required_sections_present(outputs: str) -> Feedback:
    """Check that all 7 top-level report sections are present."""
    report_lower = outputs.lower()
    missing = [s for s in _REQUIRED_SECTIONS if s.lower() not in report_lower]
    return Feedback(
        name="required_sections_present",
        value=len(missing) == 0,
        rationale=f"Missing sections: {missing}" if missing else "All sections present",
    )


@scorer
def required_subsections_present(outputs: str, expectations: dict) -> Feedback:
    """Check what fraction of expected subsections are present."""
    expected = expectations.get("expected_subsections", [])
    if not expected:
        return Feedback(
            name="required_subsections_present",
            value=1.0,
            rationale="No expected subsections defined",
        )
    report_lower = outputs.lower()
    found = [s for s in expected if s.lower() in report_lower]
    ratio = len(found) / len(expected)
    missing = [s for s in expected if s.lower() not in report_lower]
    return Feedback(
        name="required_subsections_present",
        value=ratio,
        rationale=f"Found {len(found)}/{len(expected)}. Missing: {missing}",
    )


# ---------------------------------------------------------------------------
# Markdown table checks
# ---------------------------------------------------------------------------

_TABLE_SEPARATOR_PATTERN = re.compile(r"\|[\s\-:]+\|")


@scorer
def markdown_table_count(outputs: str, expectations: dict) -> Feedback:
    """Count Markdown tables and check against the minimum threshold."""
    count = len(_TABLE_SEPARATOR_PATTERN.findall(outputs))
    threshold = expectations.get("min_table_count", 3)
    return Feedback(
        name="markdown_table_count",
        value=count >= threshold,
        rationale=f"Found {count} table(s), threshold is {threshold}",
    )


# ---------------------------------------------------------------------------
# Word count
# ---------------------------------------------------------------------------


@scorer
def minimum_word_count(outputs: str, expectations: dict) -> Feedback:
    """Check that the report meets the minimum word count."""
    word_count = len(outputs.split())
    threshold = expectations.get("min_word_count", 2000)
    return Feedback(
        name="minimum_word_count",
        value=word_count >= threshold,
        rationale=f"Word count: {word_count}, threshold: {threshold}",
    )


# ---------------------------------------------------------------------------
# Inline citations
# ---------------------------------------------------------------------------

_CITATION_PATTERNS = re.compile(
    r"(?:"
    r"[A-Z][a-zA-Z]+\s+(?:estimates?|reports?|notes?|data|says?|projects?|forecasts?)"
    r"|according to [A-Z]"
    r"|(?:Source|Sources):"
    r"|https?://"
    r")",
    re.IGNORECASE,
)


@scorer
def inline_citations_present(outputs: str) -> Feedback:
    """Count inline citation / source attribution patterns in the report."""
    matches = _CITATION_PATTERNS.findall(outputs)
    count = len(matches)
    return Feedback(
        name="inline_citations_present",
        value=count,
        rationale=f"Found {count} citation pattern(s)",
    )


# ---------------------------------------------------------------------------
# Top companies extraction
# ---------------------------------------------------------------------------

_TOP_COMPANY_A = re.compile(r"\*\*Top Company A[:\*]", re.IGNORECASE)
_TOP_COMPANY_B = re.compile(r"\*\*Top Company B[:\*]", re.IGNORECASE)


@scorer
def top_companies_extracted(outputs: str) -> Feedback:
    """Verify the Top Company A / Top Company B markers are present."""
    has_a = bool(_TOP_COMPANY_A.search(outputs))
    has_b = bool(_TOP_COMPANY_B.search(outputs))
    return Feedback(
        name="top_companies_extracted",
        value=has_a and has_b,
        rationale=(
            f"Top Company A: {'found' if has_a else 'MISSING'}, "
            f"Top Company B: {'found' if has_b else 'MISSING'}"
        ),
    )


# ---------------------------------------------------------------------------
# Ticker symbols
# ---------------------------------------------------------------------------

_TICKER_PATTERN = re.compile(r"[A-Z]{1,10}:[A-Z]{1,10}")


@scorer
def ticker_symbols_present(outputs: str) -> Feedback:
    """Count unique exchange:ticker symbols in the report."""
    tickers = set(_TICKER_PATTERN.findall(outputs))
    return Feedback(
        name="ticker_symbols_present",
        value=len(tickers),
        rationale=f"Found {len(tickers)} unique ticker(s): {sorted(tickers)}",
    )


# ---------------------------------------------------------------------------
# Financial comparison section
# ---------------------------------------------------------------------------


@scorer
def financial_comparison_section_present(outputs: str) -> Feedback:
    """Check that the Financial Comparison heading is present with company names."""
    pattern = re.compile(r"##\s+Financial Comparison:", re.IGNORECASE)
    found = bool(pattern.search(outputs))
    return Feedback(
        name="financial_comparison_section_present",
        value=found,
        rationale=(
            "Financial Comparison section found"
            if found
            else "Financial Comparison section MISSING"
        ),
    )


# ---------------------------------------------------------------------------
# Risk register table
# ---------------------------------------------------------------------------


@scorer
def risk_register_table_present(outputs: str) -> Feedback:
    """Check that a Markdown table exists in the Risk Factors section."""
    risk_match = re.search(r"###?\s+Risk\s+Factors", outputs, re.IGNORECASE)
    if not risk_match:
        return Feedback(
            name="risk_register_table_present",
            value=False,
            rationale="Risk Factors section not found",
        )
    section_text = outputs[risk_match.start() :]
    next_heading = re.search(r"\n##", section_text[1:])
    if next_heading:
        section_text = section_text[: next_heading.start() + 1]
    has_table = bool(_TABLE_SEPARATOR_PATTERN.search(section_text))
    return Feedback(
        name="risk_register_table_present",
        value=has_table,
        rationale=(
            "Table found in Risk Factors section"
            if has_table
            else "No table in Risk Factors section"
        ),
    )


# ---------------------------------------------------------------------------
# Competitive landscape table
# ---------------------------------------------------------------------------


@scorer
def competitive_landscape_table_present(outputs: str) -> Feedback:
    """Check that a Markdown table exists in the Competitive Landscape section."""
    cl_match = re.search(r"###?\s+Competitive Landscape", outputs, re.IGNORECASE)
    if not cl_match:
        return Feedback(
            name="competitive_landscape_table_present",
            value=False,
            rationale="Competitive Landscape section not found",
        )
    section_text = outputs[cl_match.start() :]
    next_heading = re.search(r"\n##", section_text[1:])
    if next_heading:
        section_text = section_text[: next_heading.start() + 1]
    has_table = bool(_TABLE_SEPARATOR_PATTERN.search(section_text))
    return Feedback(
        name="competitive_landscape_table_present",
        value=has_table,
        rationale=(
            "Table found in Competitive Landscape section"
            if has_table
            else "No table in Competitive Landscape section"
        ),
    )
