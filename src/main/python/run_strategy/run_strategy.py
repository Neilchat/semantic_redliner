from models.auto import AutoStrategy
from models.strategy_config import StrategyConfig

if __name__ == "__main__":
    config = StrategyConfig("",
                            "https://api.openai.com",
                            "",
                            "gpt-4o-mini",
                            "text-embedding-ada-002")

    strategy = AutoStrategy.from_reference("sectionWiseCompare", config)
    strategy.compare_docs("/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.docx",
                          "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Mar 2023.docx")