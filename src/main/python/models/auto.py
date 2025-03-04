from models.strategy_config import StrategyConfig
from naive_compare.naive_compare import NaiveCompare

STRATEGY_MAPPING = {
    "naiveCompare": NaiveCompare
}

class AutoStrategy:
    @classmethod
    def from_reference(cls, strategy_name: str, config: StrategyConfig):
        try:
            return STRATEGY_MAPPING[strategy_name](config)
        except KeyError:
            raise ValueError(f"{strategy_name} not found")