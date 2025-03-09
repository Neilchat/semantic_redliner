from strategies.agentic_compare.agentic_compare import AgenticCompare
from strategies.base.strategy_config import StrategyConfig
from strategies.naive_compare.naive_compare import NaiveCompare
from strategies.naive_structure_suggest.naive_structure_suggest import NaiveStructureSuggest
from strategies.sectionwise_compare.sectionwise_compare import SectionWiseCompare
from strategies.structured_structure_suggest.structured_structure_suggest import StructuredStructureSuggest

STRATEGY_MAPPING = {
    "structuredStructureSuggest": StructuredStructureSuggest,
    "naiveCompare": NaiveCompare,
    "sectionWiseCompare": SectionWiseCompare,
    "agenticCompare": AgenticCompare,
    "naiveStructureSuggest": NaiveStructureSuggest
}

class AutoStrategy:
    @classmethod
    def from_reference(cls, strategy_name: str, config: StrategyConfig):
        try:
            return STRATEGY_MAPPING[strategy_name](config)
        except KeyError:
            raise ValueError(f"{strategy_name} not found")