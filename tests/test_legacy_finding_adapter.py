from engine.finding import Finding
from engine.legacy_finding_adapter import LegacyFindingAdapter


def test_legacy_cpu_finding_can_be_converted_to_v05_finding():

    legacy_finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": "Elevated CPU utilization.",
        "confidence": 0.85,
    }

    adapter = LegacyFindingAdapter()

    finding = adapter.convert(legacy_finding)

    assert isinstance(finding, Finding)
    assert finding.finding_type == "CPU_PRESSURE"
    assert finding.category == "CPU"
    assert finding.severity == "MEDIUM"
    assert finding.description == "Elevated CPU utilization."


def test_legacy_memory_finding_can_be_converted_to_v05_finding():

    legacy_finding = {
        "category": "MEMORY",
        "severity": "WARNING",
        "message": "High memory usage.",
        "confidence": 0.85,
    }

    adapter = LegacyFindingAdapter()

    finding = adapter.convert(legacy_finding)

    assert isinstance(finding, Finding)
    assert finding.finding_type == "MEMORY_PRESSURE"
    assert finding.category == "MEMORY"
    assert finding.severity == "MEDIUM"
    assert finding.description == "High memory usage."


def test_legacy_finding_adapter_returns_none_for_unsupported_category():
    adapter = LegacyFindingAdapter()

    finding = {
        "category": "GPU",
        "severity": "WARNING",
        "message": "No GPU was detected.",
    }

    assert adapter.convert(finding) is None

def test_legacy_finding_adapter_converts_critical_severity():

    legacy_finding = {
        "category": "CPU",
        "severity": "CRITICAL",
        "message": "Critical CPU utilization.",
    }

    adapter = LegacyFindingAdapter()

    finding = adapter.convert(legacy_finding)

    assert finding.severity == "HIGH"

def test_adapter_ignores_unsupported_legacy_category():
    adapter = LegacyFindingAdapter()

    finding = {
        "category": "GPU",
        "severity": "WARNING",
        "message": "No GPU was detected.",
    }

    assert adapter.convert(finding) is None


def test_adapter_still_converts_supported_legacy_category():
    adapter = LegacyFindingAdapter()

    finding = {
        "category": "CPU",
        "severity": "WARNING",
        "message": "CPU usage is high.",
    }

    converted = adapter.convert(finding)

    assert converted is not None
    assert converted.category == "CPU"
    assert converted.finding_type == "CPU_PRESSURE"