from engine.finding_engine import FindingEngine
from engine.high_cpu_pressure_rule import HighCpuPressureRule
from engine.high_memory_pressure_rule import HighMemoryPressureRule
from engine.observation import Observation
from engine.observation_to_signal import ObservationToSignal


def create_finding_engine():
    engine = FindingEngine()

    engine.register_rule(HighMemoryPressureRule())
    engine.register_rule(HighCpuPressureRule())

    return engine


def create_signal_detector():
    return ObservationToSignal()


def test_memory_observation_produces_memory_finding():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
    )

    signal_detector = create_signal_detector()
    finding_engine = create_finding_engine()

    signal = signal_detector.detect(observation)
    findings = finding_engine.detect(signal)

    assert signal is not None
    assert signal.signal_type == "HIGH_MEMORY_USAGE"

    assert len(findings) == 1
    assert findings[0].finding_type == "MEMORY_PRESSURE"
    assert findings[0].category == "MEMORY"
    assert findings[0].severity == "HIGH"


def test_cpu_observation_produces_cpu_finding():
    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
    )

    signal_detector = create_signal_detector()
    finding_engine = create_finding_engine()

    signal = signal_detector.detect(observation)
    findings = finding_engine.detect(signal)

    assert signal is not None
    assert signal.signal_type == "HIGH_CPU_USAGE"

    assert len(findings) == 1
    assert findings[0].finding_type == "CPU_PRESSURE"
    assert findings[0].category == "CPU"
    assert findings[0].severity == "HIGH"


def test_memory_observation_value_reaches_final_finding_evidence():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
    )

    signal_detector = create_signal_detector()
    finding_engine = create_finding_engine()

    signal = signal_detector.detect(observation)
    findings = finding_engine.detect(signal)

    finding = findings[0]

    supporting_signal = finding.supporting_signals[0]

    assert supporting_signal.value == 97
    assert supporting_signal.signal_type == "HIGH_MEMORY_USAGE"


def test_cpu_observation_value_reaches_final_finding_evidence():
    observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
    )

    signal_detector = create_signal_detector()
    finding_engine = create_finding_engine()

    signal = signal_detector.detect(observation)
    findings = finding_engine.detect(signal)

    finding = findings[0]

    supporting_signal = finding.supporting_signals[0]

    assert supporting_signal.value == 99
    assert supporting_signal.signal_type == "HIGH_CPU_USAGE"


def test_non_matching_observation_produces_no_finding():
    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=50,
    )

    signal_detector = create_signal_detector()
    finding_engine = create_finding_engine()

    signal = signal_detector.detect(observation)

    assert signal is None