from config import config
from evals.deepeval_metrics import Evaluator
from text_extraction.tika_parser import TikaParser

if __name__ == "__main__":
    evaluator = Evaluator(config)
    question = "What are the significant and impactful differences between the two versions of the Apple Terms and Condition report"

    tika_parser = TikaParser()
    text1 = tika_parser.get_text("/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.docx")
    text2 = tika_parser.get_text("/Users/saswata/Documents/semantic_redliner/src/main/python/data/Mar 2023.docx")

    context = [
    f"""
    2015 report:
    
    {text1}
    """,
    """
    
    .....................................................
    2023 report:
    
    {text1}
    """]

    results_file = "naive_compare.txt"

    # results_file = "agenticComparePolicy.txt"
    # results_file = "agenticCompareProducts.txt"

    # results_file = "sectionWise_compare.txt"

    with open(f"/Users/saswata/Documents/semantic_redliner/src/main/python/data/results/{results_file}", "r") as f:
        answer = f.read()

    # relevancy = evaluator.answer_relevancy_metric(answer=answer, question=question)
    faithfulness = evaluator.faithfulness_metric(answer=answer, context=context, question=question)

    # print("relevancy", relevancy)
    print("faithfulness", faithfulness)

