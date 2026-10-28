import pytest

from engine.observation import Observation
from engine.signal import Signal
from engine.signal_rule import SignalRule


class HighMemoryUsageRule(SignalRule):

    def matches(self, observation):
        return (
            observation.source == "memory"
            and observation.subject == "system_memory"
            and observation.attribute == "usage_percent"
            and observation.value >= 85
        )

    def create_signal(self, observation):
        return Signal(
            signal_type="HIGH_MEMORY_USAGE",
            source=observation.source,
            subject=observation.subject,
            attribute=observation.attribute,
            value=observation.value,
        )


def test_signal_rule_defines_match_contract():
    rule = HighMemoryUsageRule()
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    assert rule.matches(observation) is True


def test_signal_rule_can_reject_non_matching_observation():
    rule = HighMemoryUsageRule()
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=45,
    )

    assert rule.matches(observation) is False


def test_signal_rule_can_create_signal_from_matching_observation():
    rule = HighMemoryUsageRule()
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = rule.create_signal(observation)

    assert isinstance(signal, Signal)
    assert signal.signal_type == "HIGH_MEMORY_USAGE"


def test_signal_rule_preserves_observation_context():
    rule = HighMemoryUsageRule()
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = rule.create_signal(observation)

    assert signal.source == observation.source
    assert signal.subject == observation.subject
    assert signal.attribute == observation.attribute
    assert signal.value == observation.value


def test_signal_rule_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        SignalRule()


def test_signal_rule_requires_matches_implementation():
    class IncompleteMatchesRule(SignalRule):
        def create_signal(self, observation):
            return None

    with pytest.raises(TypeError):
        IncompleteMatchesRule()


def test_signal_rule_requires_create_signal_implementation():
    class IncompleteCreateSignalRule(SignalRule):
        def matches(self, observation):
            return False

    with pytest.raises(TypeError):
        IncompleteCreateSignalRule()
