from strategies.agenticCompare.agentic_compare import AgenticCompare
from strategies.base.strategy_config import StrategyConfig
from strategies.naive_compare.naive_compare import NaiveCompare
from strategies.sectionwise_compare.sectionwise_compare import SectionWiseCompare

STRATEGY_MAPPING = {
    "naiveCompare": NaiveCompare,
    "sectionWiseCompare": SectionWiseCompare,
    "agenticCompare": AgenticCompare
}

class AutoStrategy:
    @classmethod
    def from_reference(cls, strategy_name: str, config: StrategyConfig):
        try:
            return STRATEGY_MAPPING[strategy_name](config)
        except KeyError:
            raise ValueError(f"{strategy_name} not found")