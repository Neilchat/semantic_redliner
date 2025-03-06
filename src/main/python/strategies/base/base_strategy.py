from abc import ABC, abstractmethod

from strategies.base.strategy_config import StrategyConfig


class BaseStrategy(ABC):
    def __init__(self, config: StrategyConfig):
        self.config = config

    @abstractmethod
    def compare_docs(self, docpath1, docpath2) -> str:
        pass