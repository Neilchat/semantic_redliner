from config import config
from evals.deepeval_metrics import Evaluator
from evals.rubric_evaluator import RubricEvaluator
from text_extraction.tika_parser import TikaParser


def get_faithfulness_score(docpath1, docpath2, result_path):
    evaluator = Evaluator(config)
    question = "What are the significant and impactful differences between the two versions of the Apple Terms and Condition report"

    tika_parser = TikaParser()
    text1 = tika_parser.get_text(docpath1)
    text2 = tika_parser.get_text(docpath2)

    context = [
        f"""
        2015 report:

        {text1}
        """,
        f"""

        .....................................................
        2023 report:

        {text2}
        """]

    with open(f"{result_path}", "r") as f:
        answer = f.read()

    faithfulness = evaluator.faithfulness_metric(answer=answer, context=context, question=question)

    return faithfulness

def get_rubric_score(result_path):
    rubric_evaluator = RubricEvaluator(config)
    return rubric_evaluator.evaluate(result_path)



if __name__ == "__main__":
    docpath1 = "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.docx"
    docpath2 = "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Mar 2023.docx"


    results = "/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/agenticCompare/agentic_compare.txt"

    # print("faithfulness", get_faithfulness_score(docpath1=docpath1, docpath2=docpath2, result_path=results))
    print("rubric", get_rubric_score(result_path=results))
