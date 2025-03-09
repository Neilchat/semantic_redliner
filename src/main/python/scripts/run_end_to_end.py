import re
import time
from pathlib import Path
from config import config
from evals.rubric_evaluator import RubricEvaluator
from scripts.run_evals import get_faithfulness_score
from strategies.base.auto import AutoStrategy


def camel_to_snakecase(name):
    name = re.sub(r'(?<!^)(?=[A-Z])', '_', name).lower()
    return name


if __name__ == "__main__":

    # strategy_key = "naiveCompare"
    # strategy_key = "sectionWiseCompare"
    # strategy_key = "agenticCompare"

    # strategy_key = "naiveStructureSuggest"
    strategy_key = "structuredStructureSuggest"


    results_folder = f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/{strategy_key}"
    Path(results_folder).mkdir(parents=True, exist_ok=True)

    docpath1 = "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.docx"
    docpath2 = "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Mar 2023.docx"

    strategy = AutoStrategy.from_reference(strategy_key, config)
    start = time.time()
    result = strategy.compare_docs(
        docpath1,
        docpath2,
        results_folder
    )
    end = time.time()

    final_report_path = f"{results_folder}/{camel_to_snakecase(strategy_key)}.txt"

    faithfulness = get_faithfulness_score(docpath1=docpath1, docpath2=docpath2, result_path=final_report_path)

    rubric_evaluator = RubricEvaluator(config)
    # rubric_score = rubric_evaluator.evaluate(final_report_path)

    print(f"Strategy: {strategy_key} \nTime taken: {end-start} seconds\nFaithfulness Score: {faithfulness}\n")
    with open(final_report_path, 'a') as f:
        f.write(f"\n\n..............................\n\n"
                f"Strategy: {strategy_key} \n\n"
                f"Time taken: {end-start} seconds\n\n"
                f"Faithfulness Score: {faithfulness}\n\n"
                # f"Rubric Score: {rubric_score}\n\n"
                f"Model: {config.openai_model_name}")

    print(result)
