from abc import ABC, abstractmethod


class CorrelationRule(ABC):

    @abstractmethod
    def matches(self, findings):
        pass

    @abstractmethod
    def create_correlation(self, findings):
        pass