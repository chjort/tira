"""Evaluation runner for scoring research reports with MLflow GenAI.

Provides functions to run evaluation suites (groups of scorers) against a
completed research report and log the results to the active MLflow experiment.

Usage from the Celery task layer::

    from agent_worker.evaluation.simple_eval import run_evaluation
    run_evaluation(theme, report)
"""

import logging

import mlflow
from agent_worker.config import MLFLOW_EXPERIMENT_NAME
from agent_worker.evaluation.harness import build_eval_data
from agent_worker.evaluation.harness import load_dataset
from agent_worker.evaluation.scorers.code_based import (
    competitive_landscape_table_present,
)
from agent_worker.evaluation.scorers.code_based import (
    financial_comparison_section_present,
)
from agent_worker.evaluation.scorers.code_based import inline_citations_present
from agent_worker.evaluation.scorers.code_based import markdown_table_count
from agent_worker.evaluation.scorers.code_based import minimum_word_count
from agent_worker.evaluation.scorers.code_based import required_sections_present
from agent_worker.evaluation.scorers.code_based import required_subsections_present
from agent_worker.evaluation.scorers.code_based import risk_register_table_present
from agent_worker.evaluation.scorers.code_based import ticker_symbols_present
from agent_worker.evaluation.scorers.code_based import top_companies_extracted

# from agent_worker.evaluation.scorers.model_based import (
#     coverage_completeness_score,
#     factual_specificity_score,
#     groundedness_score,
#     source_quality_score,
# )

logger = logging.getLogger(__name__)

_DATASET = "expectations_dataset"
_SCORERS = [
    inline_citations_present,
    required_sections_present,
    required_subsections_present,
    markdown_table_count,
    minimum_word_count,
    ticker_symbols_present,
    top_companies_extracted,
    competitive_landscape_table_present,
    risk_register_table_present,
    financial_comparison_section_present,
    # groundedness_score,
    # source_quality_score,
    # coverage_completeness_score,
    # factual_specificity_score,
]


def _get_run_id_by_name(run_name: str) -> str | None:
    """Get the most recent run_id for a given run name.

    Args:
        run_name: The MLflow run name to search for.

    Returns:
        The run_id of the most recent matching run, or ``None`` if no run
        with that name exists.
    """
    runs = mlflow.search_runs(
        experiment_names=[MLFLOW_EXPERIMENT_NAME],
        filter_string=f"attributes.run_name = '{run_name}'",
        order_by=["start_time DESC"],
        max_results=1,
    )

    if not runs.empty:
        return runs.iloc[0]["run_id"]
    return None


def run_evaluation(
    theme: str,
    report: str,
) -> None:
    """Run evaluation for a completed research report.

    Loads the suite's dataset, builds the evaluation data, and calls
    ``mlflow.genai.evaluate()`` within an MLflow run. Results are logged
    as a side-effect to the currently active MLflow experiment.

    Args:
        theme: The investment theme that was researched.
        report: The Markdown report produced by the agent.
    """
    try:
        dataset = load_dataset(_DATASET)
        eval_data = build_eval_data(dataset, theme, report)
        run_name = "prod:evaluations"
        run_id = _get_run_id_by_name(run_name)
        with mlflow.start_run(run_id=run_id, run_name=run_name):
            mlflow.genai.evaluate(data=eval_data, scorers=_SCORERS)
    except Exception:
        logger.exception("Evaluation failed for theme %r.", theme)
