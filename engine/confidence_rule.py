from abc import ABC, abstractmethod


class ConfidenceRule(ABC):

    @abstractmethod
    def matches(self, subject, evidence):
        pass

    @abstractmethod
    def create_confidence(self, subject, evidence):
        pass