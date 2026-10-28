from abc import ABC, abstractmethod


class SignalRule(ABC):
    """Abstract contract for rules that convert observations into signals."""

    @abstractmethod
    def matches(self, observation):
        """Return True when this rule applies to the observation."""
        raise NotImplementedError

    @abstractmethod
    def create_signal(self, observation):
        """Create a signal from a matching observation."""
        raise NotImplementedError
