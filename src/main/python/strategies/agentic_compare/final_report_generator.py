from langchain_openai import ChatOpenAI
from strategies.agentic_compare.prompt_store import policy_product_merger_prompt, intro_comparison_prompt
from strategies.base.strategy_config import StrategyConfig


class FinalReportGenerator:
    def __init__(self, config: StrategyConfig):
        self.llm = ChatOpenAI(openai_api_key=config.openai_api_key, model="gpt-4o-mini", temperature=0)

    def create_policy_product_report(self, product_report, policy_report):
        prompt = policy_product_merger_prompt.format(product_report=product_report,
                                                     policy_report=policy_report)
        report = self.llm.predict(prompt)
        return report

    def compare_introductions(self, page2015, page2023):
        prompt = intro_comparison_prompt.format(page2015=page2015,
                                                page2023=page2023)
        report = self.llm.predict(prompt)
        return report




