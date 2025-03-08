import math

import numpy as np
from openai import OpenAI

from strategies.base.strategy_config import StrategyConfig

rubric = \
    [
        "The 2015 document focused more on iTunes rather than Apple products as a whole.",
        "The 2015 document states that the agreement needs careful read through, the 2023 one doesn't.",
        "The 2015 document mentions 1-click, 2023 document doesn't."
        "The 2023 document mentions Apple Fitness+, 2015 document doesn't.",
        "The 2023 document mentions Apple New+, 2015 document doesn't.",
        "The 2023 document mentions Apple One, 2015 document doesn't."
        "The 2023 document Agreement is governed by California Law and the 2015 one is governed by English Law",
        "For family sharing, the 2023 document stipulates a minimum age of 13 or equivalent in their home country, whereas the 2015 document doesn't mention home country",
     ]

class RubricEvaluator:
    def __init__(self, config: StrategyConfig):
        self.model = OpenAI(api_key=config.openai_api_key)
        self.config = config

    def calculate_average_metric(self, prompt):
        probs = {}
        scores = np.array([0, 1, 2, 3, 4, 5])

        completion_params = {
            "model": self.config.openai_model_name,
            "messages": prompt,
            "temperature": 0.0,
            "logprobs": True,
            "max_tokens": 1,
            "top_logprobs": 6
        }
        response = self.model.chat.completions.create(**completion_params)
        logprobs = response.choices[0].logprobs.content[0].top_logprobs
        for lp in logprobs:
            if lp.token.isdigit() and int(lp.token) in scores and int(lp.token) not in probs:
                probs[int(lp.token)] = math.exp(lp.logprob)

        if len(probs) == 0:
            return 0.0

        total_prob = sum(probs.values())
        normalized_probs = []
        for k in scores:
            normalized_probs.append(probs.get(k, 0) / total_prob)

        expected_score = np.sum(scores * normalized_probs)

        return expected_score

    def create_evaluation_prompt(self, result, rubric):
        prompt = [{
            'role': 'system',
            'content': (
                "You are an expert evaluator of answers. "
                "Please evaluate the ANSWER the User provides on the following CRITERIA:\n"
                f"\n{rubric}\n"
                "The criteria is a statement or an assertion that the answer must satisfy in order to get a high score.\n"
                "Provide your score as a single digit number only, ranging from 0 to 5.\n"
                "0 means the answer is completely incorrect, 5 means the answer is completely correct.\n"
                "Penalize the answer if it doesn't satisfy the criteria.\n"
                "Remember, you should not output anything other than the evaluation score (number between 0 and 5).\n"
                "No explanation for the score is needed either, just the score itself."
            )}, {
            'role': 'user',
            'content': (
                f"ANSWER: {result}"
            ),
        }]
        return prompt


    def evaluate(self, results_path):
        with open(results_path, 'r') as f:
            result = f.read()
        score = 0
        for r in rubric:
            prompt = self.create_evaluation_prompt(result, r)
            r_score = self.calculate_average_metric(prompt)
            score += r_score/5.0
        return score/len(rubric)
