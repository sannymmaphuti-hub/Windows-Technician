import pytest

from engine.observation import Observation
from engine.observation_to_signal import ObservationToSignal
from engine.signal import Signal
from engine.signal_rule import SignalRule


class AlwaysMatchingRule(SignalRule):

    def matches(self, observation):
        return True

    def create_signal(self, observation):
        return Signal(
            signal_type="TEST_SIGNAL",
            source=observation.source,
            subject=observation.subject,
            attribute=observation.attribute,
            value=observation.value,
        )


class NeverMatchingRule(SignalRule):

    def matches(self, observation):
        return False

    def create_signal(self, observation):
        raise AssertionError(
            "NeverMatchingRule should never create a signal"
        )


def test_detector_can_register_a_rule():
    detector = ObservationToSignal()

    detector.register_rule(AlwaysMatchingRule())

    observation = Observation(
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=123,
    )

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "TEST_SIGNAL"


def test_registered_rules_are_checked_in_registration_order():
    detector = ObservationToSignal()

    detector.register_rule(NeverMatchingRule())
    detector.register_rule(AlwaysMatchingRule())

    observation = Observation(
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=123,
    )

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "TEST_SIGNAL"


def test_detector_can_register_multiple_rules():
    detector = ObservationToSignal()

    detector.register_rule(NeverMatchingRule())
    detector.register_rule(AlwaysMatchingRule())
    detector.register_rule(NeverMatchingRule())

    observation = Observation(
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=123,
    )

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "TEST_SIGNAL"


def test_register_rule_rejects_invalid_rule():
    detector = ObservationToSignal()

    with pytest.raises(ValueError):
        detector.register_rule(None)