from deepeval.metrics import FaithfulnessMetric, AnswerRelevancyMetric, SummarizationMetric
from deepeval.models import GPTModel
from deepeval.test_case import LLMTestCase
from strategies.base.strategy_config import StrategyConfig


class Evaluator:
    def __init__(self, config: StrategyConfig):
        self.model = GPTModel(model="gpt-4o-mini", _openai_api_key=config.openai_api_key)

    def faithfulness_metric(self, answer, context, question):
        metric = FaithfulnessMetric(
            threshold=0.7,
            model=self.model,
            include_reason=True,
            async_mode=False
        )

        test_case = LLMTestCase(
            input=question,
            actual_output=answer,
            retrieval_context=context
        )

        return metric.measure(test_case), metric.reason

    def answer_relevancy_metric(self, answer, question):
        metric = AnswerRelevancyMetric(
            threshold=0.7,
            model=self.model,
            include_reason=True,
            async_mode=False
        )
        test_case = LLMTestCase(
            input=question,
            actual_output=answer
        )

        return metric.measure(test_case), metric.reason

    def summarization_metric(self, question, answer):
        test_case = LLMTestCase(input=question, actual_output=answer)
        metric = SummarizationMetric(
            threshold=0.5,
            model=self.model,
            async_mode=False
        )

        return metric.measure(test_case), metric.reason
