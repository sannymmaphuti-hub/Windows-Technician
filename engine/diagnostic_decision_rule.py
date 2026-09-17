from abc import ABC, abstractmethod


class DiagnosticDecisionRule(ABC):
    @abstractmethod
    def matches(self, evidence):
        """Return True when this rule applies to the current evidence."""
        raise NotImplementedError

    @abstractmethod
    def create_decision(self, evidence):
        """Create the diagnostic decision for matching evidence."""
        raise NotImplementedError