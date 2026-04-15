"""Evaluation runner for scoring research reports with MLflow GenAI.

Provides functions to run evaluation suites (groups of scorers) against a
completed research report and log the results to the active MLflow experiment.

Usage from the Celery task layer::

    from agent_worker.evaluation.simple_eval import run_evaluation
    run_evaluation(theme, report)
"""

import logging

import mlflow

from agent_worker.evaluation.harness import build_eval_data, load_dataset
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

SUITE_NAMES: list[str] = list(_SUITE_REGISTRY.keys())


def run_suite(suite_name: str, theme: str, report: str) -> None:
    """Run a single evaluation suite and log results to MLflow.

    Loads the suite's dataset, builds the evaluation data, and calls
    ``mlflow.genai.evaluate()`` within an MLflow run. Results are logged
    as a side-effect to the currently active MLflow experiment.

    Args:
        suite_name: Key into the suite registry (e.g. ``"groundedness"``).
        theme: The investment theme that was researched.
        report: The Markdown report produced by the agent.

    Raises:
        KeyError: If *suite_name* is not in the suite registry.
    """
    spec = _SUITE_REGISTRY[suite_name]
    dataset = load_dataset(spec["dataset"])
    eval_data = build_eval_data(dataset, theme, report)

    with mlflow.start_run(run_name=f"eval:{suite_name}:{theme}"):
        mlflow.genai.evaluate(data=eval_data, scorers=spec["scorers"])


def run_evaluation(
    theme: str,
    report: str,
    suite_names: list[str] | None = None,
) -> None:
    """Run evaluation suites for a completed research report.

    Iterates over the requested suites and calls :func:`run_suite` for each.
    Individual suite failures are logged as warnings and do not propagate,
    so a scorer crash never fails the calling Celery task.

    Args:
        theme: The investment theme that was researched.
        report: The Markdown report produced by the agent.
        suite_names: Suite names to run. Defaults to all registered suites.
    """
    suites = suite_names if suite_names is not None else SUITE_NAMES

    for name in suites:
        try:
            run_suite(name, theme, report)
        except Exception:
            logger.exception("Evaluation suite %r failed for theme %r.", name, theme)
