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
        raise AssertionError("NeverMatchingRule should never create a signal")


def test_detector_can_use_multiple_rules():
    detector = ObservationToSignal()

    detector._rules = [
        NeverMatchingRule(),
        AlwaysMatchingRule(),
    ]

    observation = Observation(
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=123,
    )

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "TEST_SIGNAL"


def test_detector_uses_first_matching_rule():
    detector = ObservationToSignal()

    first_rule = AlwaysMatchingRule()
    second_rule = AlwaysMatchingRule()

    detector._rules = [
        first_rule,
        second_rule,
    ]

    observation = Observation(
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=123,
    )

    signal = detector.detect(observation)

    assert signal is not None
    assert signal.signal_type == "TEST_SIGNAL"


def test_detector_returns_none_when_no_rule_matches():
    detector = ObservationToSignal()

    detector._rules = [
        NeverMatchingRule(),
    ]

    observation = Observation(
        source="test",
        subject="test_subject",
        attribute="test_attribute",
        value=123,
    )

    signal = detector.detect(observation)

    assert signal is None