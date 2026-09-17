from abc import ABC, abstractmethod


class RecommendationRule(ABC):

    @abstractmethod
    def matches(self, finding):
        pass

    @abstractmethod
    def create_recommendation(self, finding):
        pass