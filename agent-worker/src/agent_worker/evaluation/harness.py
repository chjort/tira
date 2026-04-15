"""Evaluation harness for generating reports and preparing evaluation data.

Provides utilities for:
- MLflow experiment setup
- Generating and caching agent research reports
- Loading evaluation datasets
- Building the data structures expected by ``mlflow.genai.evaluate()``
"""

import asyncio
import json
import logging
from importlib import resources

import mlflow

from agent_worker import config
from agent_worker.agent import run_research

logger = logging.getLogger(__name__)

# Module-level cache so each theme is only run through the agent once per
# evaluation session, even when multiple suites reference the same theme.
_REPORT_CACHE: dict[str, str] = {}


def setup_mlflow() -> str:
    """Configure MLflow tracking URI and experiment for evaluation.

    Returns:
        The experiment ID.
    """
    mlflow.set_tracking_uri(config.MLFLOW_TRACKING_URI)
    experiment = mlflow.set_experiment(config.EVAL_EXPERIMENT_NAME)
    return experiment.experiment_id


def clear_report_cache() -> None:
    """Reset the report cache between evaluation runs."""
    _REPORT_CACHE.clear()


def generate_report(theme: str) -> str:
    """Generate a research report for *theme*, returning cached results when available.

    Uses ``asyncio.run()`` to bridge the sync evaluation harness with the async
    agent pipeline — same approach as the Celery task.
    """
    if theme not in _REPORT_CACHE:
        logger.info("Generating report for theme: %s", theme)
        _REPORT_CACHE[theme] = asyncio.run(run_research(theme))
        logger.info(
            "Report generated for '%s' (%d words)",
            theme,
            len(_REPORT_CACHE[theme].split()),
        )
    return _REPORT_CACHE[theme]


def load_dataset(dataset_name: str) -> list[dict]:
    """Load an evaluation dataset JSON file by name.

    Args:
        dataset_name: File name without extension (e.g. ``"groundedness"``).

    Returns:
        A list of test-case dictionaries.
    """
    datasets_package = "agent_worker.evaluation.datasets"
    filename = f"{dataset_name}.json"

    # Use importlib.resources for reliable path resolution regardless of
    # whether the package is installed as editable or as a wheel.
    ref = resources.files(datasets_package).joinpath(filename)
    text = ref.read_text(encoding="utf-8")
    return json.loads(text)


def build_eval_data(
    dataset: list[dict],
    report_cache: dict[str, str],
) -> list[dict]:
    """Convert a loaded dataset into the format expected by ``mlflow.genai.evaluate()``.

    Each returned dict has:
    - ``inputs``: ``{"theme": ...}``
    - ``outputs``: the generated Markdown report string
    - ``expectations``: all remaining dataset fields (``grading_notes``,
      ``expected_sections``, etc.)

    Args:
        dataset: Test-case dicts as returned by :func:`load_dataset`.
        report_cache: Mapping of theme -> generated report.

    Returns:
        A list of dicts suitable for passing as ``data`` to
        ``mlflow.genai.evaluate()``.
    """
    eval_rows = []
    for case in dataset:
        theme = case["theme"]
        report = report_cache.get(theme, "")

        # Everything except 'theme' goes into expectations for scorer access.
        expectations = {k: v for k, v in case.items() if k != "theme"}

        eval_rows.append(
            {
                "inputs": {"theme": theme},
                "outputs": report,
                "expectations": expectations,
            }
        )
    return eval_rows
