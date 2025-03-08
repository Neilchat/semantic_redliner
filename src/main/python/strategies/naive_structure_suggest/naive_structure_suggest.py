from openai import OpenAI

from strategies.base.base_strategy import BaseStrategy
from strategies.base.strategy_config import StrategyConfig
from text_extraction.tika_parser import TikaParser


class NaiveStructureSuggest(BaseStrategy):
    def __init__(self, config: StrategyConfig):
        super().__init__(config)
        self.llm = OpenAI(api_key=config.openai_api_key)
        self.tika_parser = TikaParser()

    def compare_docs(self, docpath1, docpath2, results_folder) -> str:
        text1 = self.tika_parser.get_text(docpath1)
        text2 = self.tika_parser.get_text(docpath2)

        system_prompt = \
"""
You are an advanced NLP system specialized in understanding Legal documents.
Your job is to compare two legal documents in terms of their structure and suggest a better structure that combines the qualities of both.

The user will supply you with Apple's Terms and Conditions from 2015 and 2023. Please understand the structure of each document, and suggest a better unified structure.
"""

        user_prompt = \
            f""" 
You have been given two versions of publicly available Apple Music’s Terms & Conditions from different years as follows.

Apple Music's terms and conditions from 2015: 
{text1}

Apple Music's terms and conditions from 2023: 
{text2}

Please provide suggestions for standardizing the Terms and Conditions to create a more consistent format.
"""
        completion_parameters = {"model": self.config.openai_model_name,
                                 "messages": [{"role": "system",
                                               "content": system_prompt},
                                              {"role": "user",
                                               "content": user_prompt}],
                                 "temperature": 0.0}

        ans = self.llm.chat.completions.create(**completion_parameters).choices[0].message.content

        with open(f"{results_folder}/naive_structure_suggest.txt",
                  'w') as f:
            f.write(ans)
        return ans

