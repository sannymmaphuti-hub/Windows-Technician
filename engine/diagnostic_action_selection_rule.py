from abc import ABC, abstractmethod


class DiagnosticActionSelectionRule(ABC):
    @abstractmethod
    def matches(self, decision_type):
        """Return True when this rule applies to the diagnostic decision."""
        raise NotImplementedError

    @abstractmethod
    def create_action(self, decision_type):
        """Create the diagnostic action for a matching decision."""
        raise NotImplementedError