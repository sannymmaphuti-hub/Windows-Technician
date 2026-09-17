from engine.finding_engine import FindingEngine
from engine.high_cpu_pressure_rule import HighCpuPressureRule
from engine.high_memory_pressure_rule import HighMemoryPressureRule
from engine.signal import Signal


def create_memory_signal():
    return Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=97,
        strength="HIGH",
    )


def create_cpu_signal():
    return Signal(
        signal_type="HIGH_CPU_USAGE",
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=99,
        strength="HIGH",
    )


def create_engine():
    engine = FindingEngine()

    engine.register_rule(HighMemoryPressureRule())
    engine.register_rule(HighCpuPressureRule())

    return engine


def test_memory_signal_produces_memory_finding():
    engine = create_engine()

    findings = engine.detect(create_memory_signal())

    assert len(findings) == 1
    assert findings[0].finding_type == "MEMORY_PRESSURE"
    assert findings[0].category == "MEMORY"
    assert findings[0].severity == "HIGH"


def test_cpu_signal_produces_cpu_finding():
    engine = create_engine()

    findings = engine.detect(create_cpu_signal())

    assert len(findings) == 1
    assert findings[0].finding_type == "CPU_PRESSURE"
    assert findings[0].category == "CPU"
    assert findings[0].severity == "HIGH"


def test_memory_signal_does_not_produce_cpu_finding():
    engine = create_engine()

    findings = engine.detect(create_memory_signal())

    assert all(
        finding.finding_type != "CPU_PRESSURE"
        for finding in findings
    )


def test_cpu_signal_does_not_produce_memory_finding():
    engine = create_engine()

    findings = engine.detect(create_cpu_signal())

    assert all(
        finding.finding_type != "MEMORY_PRESSURE"
        for finding in findings
    )


def test_engine_can_process_different_signals_independently():
    engine = create_engine()

    memory_findings = engine.detect(create_memory_signal())
    cpu_findings = engine.detect(create_cpu_signal())

    assert memory_findings[0].finding_type == "MEMORY_PRESSURE"
    assert cpu_findings[0].finding_type == "CPU_PRESSURE"


def test_findings_preserve_their_supporting_signals():
    engine = create_engine()

    memory_signal = create_memory_signal()
    cpu_signal = create_cpu_signal()

    memory_findings = engine.detect(memory_signal)
    cpu_findings = engine.detect(cpu_signal)

    assert memory_findings[0].supporting_signals == [memory_signal]
    assert cpu_findings[0].supporting_signals == [cpu_signal]