from abc import ABC, abstractmethod


class RootCauseRule(ABC):

    @abstractmethod
    def matches(self, findings):
        pass

    @abstractmethod
    def create_candidate(self, findings):
        pass