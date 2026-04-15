"""Evaluation test suites mapping to the four success criteria.

Each suite function:
1. Loads its evaluation dataset.
2. Assembles the appropriate code-based and model-based scorers.
3. Calls ``mlflow.genai.evaluate()`` and returns the result.

The ``run_all_suites`` orchestrator pre-generates reports for all unique themes
before running individual suites so the expensive agent calls happen only once.
"""

import logging

import mlflow.genai
from mlflow.genai.evaluation.entities import EvaluationResult

from agent_worker.evaluation.harness import (
    build_eval_data,
    clear_report_cache,
    generate_report,
    load_dataset,
    setup_mlflow,
)
from agent_worker.evaluation.scorers.code_based import (
    competitive_landscape_table_present,
    financial_comparison_section_present,
    inline_citations_present,
    markdown_table_count,
    minimum_word_count,
    required_sections_present,
    required_subsections_present,
    risk_register_table_present,
    ticker_symbols_present,
    top_companies_extracted,
)
from agent_worker.evaluation.scorers.model_based import (
    coverage_completeness_score,
    factual_specificity_score,
    groundedness_score,
    source_quality_score,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Suite definitions
# ---------------------------------------------------------------------------

_SUITE_REGISTRY: dict[str, dict] = {
    "groundedness": {
        "dataset": "groundedness",
        "scorers": [
            inline_citations_present,
            groundedness_score,
        ],
    },
    "source_quality": {
        "dataset": "source_quality",
        "scorers": [
            source_quality_score,
        ],
    },
    "coverage": {
        "dataset": "coverage",
        "scorers": [
            required_sections_present,
            required_subsections_present,
            markdown_table_count,
            minimum_word_count,
            ticker_symbols_present,
            top_companies_extracted,
            competitive_landscape_table_present,
            risk_register_table_present,
            coverage_completeness_score,
        ],
    },
    "factual_accuracy": {
        "dataset": "factual_accuracy",
        "scorers": [
            financial_comparison_section_present,
            factual_specificity_score,
        ],
    },
}

SUITE_NAMES = list(_SUITE_REGISTRY.keys())


def run_suite(
    suite_name: str,
    report_cache: dict[str, str],
) -> EvaluationResult:
    """Run a single evaluation suite.

    Args:
        suite_name: One of ``SUITE_NAMES``.
        report_cache: Pre-populated mapping of theme -> report string.

    Returns:
        The ``EvaluationResult`` containing per-row and aggregate metrics.
    """
    if suite_name not in _SUITE_REGISTRY:
        raise ValueError(f"Unknown suite '{suite_name}'. Choose from: {SUITE_NAMES}")

    spec = _SUITE_REGISTRY[suite_name]
    dataset = load_dataset(spec["dataset"])
    eval_data = build_eval_data(dataset, report_cache)

    logger.info("Running suite '%s' with %d test case(s)", suite_name, len(eval_data))

    result = mlflow.genai.evaluate(
        data=eval_data,
        scorers=spec["scorers"],
    )
    return result


def run_all_suites(
    suite_filter: str = "all",
    theme_override: str | None = None,
) -> dict[str, EvaluationResult]:
    """Orchestrate evaluation: generate reports, then run requested suites.

    Args:
        suite_filter: ``"all"`` or a single suite name from ``SUITE_NAMES``.
        theme_override: If set, use this single theme for every test case
            instead of the themes defined in the datasets.

    Returns:
        Dict mapping suite name to its ``EvaluationResult``.
    """
    setup_mlflow()
    clear_report_cache()

    # Determine which suites to run.
    if suite_filter == "all":
        suites_to_run = SUITE_NAMES
    else:
        suites_to_run = [suite_filter]

    # Collect all unique themes across the requested suites.
    themes: set[str] = set()
    for name in suites_to_run:
        dataset = load_dataset(_SUITE_REGISTRY[name]["dataset"])
        if theme_override:
            themes.add(theme_override)
        else:
            for case in dataset:
                themes.add(case["theme"])

    # Pre-generate reports (cached across suites).
    logger.info("Generating reports for %d theme(s): %s", len(themes), sorted(themes))
    report_cache: dict[str, str] = {}
    for theme in sorted(themes):
        report_cache[theme] = generate_report(theme)

    # If theme_override is set, patch the datasets so every case uses it.
    if theme_override:
        for name in suites_to_run:
            dataset = load_dataset(_SUITE_REGISTRY[name]["dataset"])
            for case in dataset:
                case["theme"] = theme_override

    # Run each suite.
    results: dict[str, EvaluationResult] = {}
    for name in suites_to_run:
        logger.info("--- Running suite: %s ---", name)
        results[name] = run_suite(name, report_cache)

    return results
