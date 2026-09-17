from abc import ABC, abstractmethod


class ExplanationRule(ABC):

    @abstractmethod
    def matches(self, subject, evidence):
        pass

    @abstractmethod
    def create_explanation(self, subject, evidence):
        pass