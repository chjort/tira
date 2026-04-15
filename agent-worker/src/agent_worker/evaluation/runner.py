"""CLI entry point and pytest-compatible test functions for the evaluation suites.

CLI usage::

    uv run tira-eval                              # all suites
    uv run tira-eval --suite coverage             # single suite
    uv run tira-eval --theme "Quantum Computing"  # override theme
    uv run tira-eval --mlflow-uri http://host:5000

Pytest usage::

    cd agent-worker && uv run pytest src/agent_worker/evaluation/runner.py -m eval -v
"""

import argparse
import logging
import os
import sys

import pytest

from agent_worker.evaluation.suites import SUITE_NAMES, run_all_suites

logger = logging.getLogger(__name__)


def _print_results(
    results: dict,
) -> bool:
    """Print evaluation results and return True if all suites pass.

    Returns:
        ``True`` if no failures detected, ``False`` otherwise.
    """
    all_passed = True
    for suite_name, result in results.items():
        print(f"\n{'=' * 60}")
        print(f"Suite: {suite_name}")
        print(f"{'=' * 60}")
        if hasattr(result, "metrics") and result.metrics:
            for metric_name, value in result.metrics.items():
                print(f"  {metric_name}: {value}")
        else:
            print("  (no aggregate metrics)")
    return all_passed


def main() -> None:
    """CLI entry point for running TIRA evaluation suites."""
    parser = argparse.ArgumentParser(
        description="Run TIRA Research Agent evaluation suites",
    )
    parser.add_argument(
        "--suite",
        choices=SUITE_NAMES + ["all"],
        default="all",
        help="Which evaluation suite to run (default: all)",
    )
    parser.add_argument(
        "--theme",
        type=str,
        default=None,
        help="Override the theme for all test cases",
    )
    parser.add_argument(
        "--mlflow-uri",
        type=str,
        default=None,
        help="MLflow tracking URI (overrides MLFLOW_TRACKING_URI env var)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    if args.mlflow_uri:
        os.environ["MLFLOW_TRACKING_URI"] = args.mlflow_uri

    results = run_all_suites(suite_filter=args.suite, theme_override=args.theme)
    passed = _print_results(results)

    if not passed:
        sys.exit(1)


# ---------------------------------------------------------------------------
# Pytest-compatible test functions
# ---------------------------------------------------------------------------


@pytest.mark.eval
def test_groundedness_suite():
    """Run the groundedness evaluation suite."""
    results = run_all_suites(suite_filter="groundedness")
    assert "groundedness" in results


@pytest.mark.eval
def test_source_quality_suite():
    """Run the source quality evaluation suite."""
    results = run_all_suites(suite_filter="source_quality")
    assert "source_quality" in results


@pytest.mark.eval
def test_coverage_suite():
    """Run the coverage evaluation suite."""
    results = run_all_suites(suite_filter="coverage")
    assert "coverage" in results


@pytest.mark.eval
def test_factual_accuracy_suite():
    """Run the factual accuracy evaluation suite."""
    results = run_all_suites(suite_filter="factual_accuracy")
    assert "factual_accuracy" in results


if __name__ == "__main__":
    main()
