import asyncio

from agent_worker.agent import run_research
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
from agent_worker.evaluation.scorers.model_based import coverage_completeness_score
from agent_worker.evaluation.scorers.model_based import factual_specificity_score
from agent_worker.evaluation.scorers.model_based import groundedness_score
from agent_worker.evaluation.scorers.model_based import source_quality_score

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

suite_name = "groundedness"
theme = "Quantum Computing"

result = asyncio.run(run_research(theme))
print(result)
# spec = _SUITE_REGISTRY[suite_name]
# dataset = load_dataset(spec["dataset"])
# eval_data = build_eval_data(dataset, report_cache)
#
# logger.info("Running suite '%s' with %d test case(s)", suite_name, len(eval_data))
#
# result = mlflow.genai.evaluate(
#     data=eval_data,
#     scorers=spec["scorers"],
# )
