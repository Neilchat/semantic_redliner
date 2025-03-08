from config import config
from strategies.base.auto import AutoStrategy

if __name__ == "__main__":

    strategy_key = "agentic_compare"
    # strategy_key = "sectionWiseCompare"

    strategy = AutoStrategy.from_reference(strategy_key, config)
    result = strategy.compare_docs(
        "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Jan 2015.docx",
        "/Users/saswata/Documents/semantic_redliner/src/main/python/data/Mar 2023.docx"
    )

    print(result)
