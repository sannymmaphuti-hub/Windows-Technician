from abc import ABC, abstractmethod


class FindingRule(ABC):

    @abstractmethod
    def matches(self, signal):
        pass

    @abstractmethod
    def create_finding(self, signal):
        pass
