from models.auto import AutoStrategy
from models.strategy_config import StrategyConfig

if __name__ == "__main__":
    config = StrategyConfig("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",
                            "https://api.openai.com",
                            "",
                            "gpt-4o-mini",
                            "text-embedding-ada-002")

    strategy = AutoStrategy.from_reference("sectionWiseCompare", config)
    strategy.compare_docs("/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.docx",
                          "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Mar 2023.docx")