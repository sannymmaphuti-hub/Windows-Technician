from abc import ABC, abstractmethod


class RootCauseEvaluationRule(ABC):

    @abstractmethod
    def matches(self, candidate, findings):
        pass

    @abstractmethod
    def create_evaluation(self, candidate, findings):
        pass