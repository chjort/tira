"""Evaluation harness for generating reports and preparing evaluation data.

Provides utilities for:
- Loading evaluation datasets
- Building the data structures expected by ``mlflow.genai.evaluate()``
"""

import json
from importlib import resources


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
    theme: str,
    report: str,
) -> list[dict]:
    """Convert a loaded dataset into the format expected by ``mlflow.genai.evaluate()``.

    Each returned dict has:
    - ``inputs``: ``{"theme": ...}``
    - ``outputs``: the generated Markdown report string
    - ``expectations``: all remaining dataset fields (``grading_notes``,
      ``expected_sections``, etc.)

    Args:
        dataset: Test-case dicts as returned by :func:`load_dataset`.
        theme: Theme of the generated report.
        report: Generated report.

    Returns:
        A list of dicts suitable for passing as ``data`` to
        ``mlflow.genai.evaluate()``.
    """
    eval_rows = []
    for case in dataset:
        expectations = {k: v for k, v in case.items()}
        eval_rows.append(
            {
                "inputs": {"theme": theme},
                "outputs": report,
                "expectations": expectations,
            }
        )
    return eval_rows
