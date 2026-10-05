# ==========================================
# Windows Technician v0.8
# BASELINE COMPARISON TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.health_baseline import HealthBaseline
from engine.baseline_comparison import BaselineComparison


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_baseline():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample(
        {
            "cpu_usage": 40,
            "memory_usage": 60,
            "disk_usage": 50,
        }
    )

    return baseline


def test_comparison_requires_health_baseline():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert comparison.baseline is baseline


def test_comparison_preserves_machine_identity():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert comparison.machine_id == "machine-001"
    assert comparison.hostname == "REMOTE-PC"


def test_comparison_can_compare_current_sample():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    result = comparison.compare(
        {
            "cpu_usage": 50,
            "memory_usage": 70,
            "disk_usage": 55,
        }
    )

    assert result["cpu_usage"] == 10
    assert result["memory_usage"] == 10
    assert result["disk_usage"] == 5


def test_comparison_uses_latest_baseline_sample():
    baseline = build_baseline()

    baseline.add_sample(
        {
            "cpu_usage": 45,
            "memory_usage": 65,
            "disk_usage": 52,
        }
    )

    comparison = BaselineComparison(baseline)

    result = comparison.compare(
        {
            "cpu_usage": 50,
            "memory_usage": 70,
            "disk_usage": 55,
        }
    )

    assert result["cpu_usage"] == 5
    assert result["memory_usage"] == 5
    assert result["disk_usage"] == 3


def test_comparison_does_not_modify_baseline_samples():
    baseline = build_baseline()

    original_samples = list(baseline.samples)

    comparison = BaselineComparison(baseline)

    comparison.compare(
        {
            "cpu_usage": 80,
            "memory_usage": 90,
        }
    )

    assert baseline.samples == original_samples


def test_comparison_does_not_add_current_sample_to_baseline():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    comparison.compare(
        {
            "cpu_usage": 80,
            "memory_usage": 90,
        }
    )

    assert len(baseline.samples) == 1


def test_comparison_does_not_change_machine_health_state():
    baseline = build_baseline()
    machine = baseline.machine

    comparison = BaselineComparison(baseline)

    comparison.compare(
        {
            "cpu_usage": 90,
            "memory_usage": 95,
        }
    )

    assert machine.health_state == "UNKNOWN"


def test_comparison_does_not_change_connection_state():
    baseline = build_baseline()
    machine = baseline.machine

    comparison = BaselineComparison(baseline)

    comparison.compare(
        {
            "cpu_usage": 90,
            "memory_usage": 95,
        }
    )

    assert machine.connection_state == "UNKNOWN"


def test_comparison_does_not_authorize_remediation():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "authorize")
    assert not hasattr(comparison, "approve")


def test_comparison_does_not_execute_remediation():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "execute")
    assert not hasattr(comparison, "remediate")


def test_comparison_does_not_create_remediation_action():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "remediation_action")
    assert not hasattr(comparison, "remediation_actions")


def test_comparison_does_not_create_alert():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "alert")
    assert not hasattr(comparison, "proactive_alert")


def test_comparison_does_not_create_diagnostic_case():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "case")
    assert not hasattr(comparison, "diagnostic_case")


def test_comparison_does_not_perform_diagnosis():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "diagnose")
    assert not hasattr(comparison, "diagnostic_pipeline")


def test_comparison_does_not_retry():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "retry")
    assert not hasattr(comparison, "retry_count")


def test_comparison_does_not_recover():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "recover")
    assert not hasattr(comparison, "recovery")


def test_comparison_preserves_platform_information():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert comparison.baseline.machine.platform == "Windows"
    assert comparison.baseline.machine.operating_system == "Windows 11"


def test_comparison_is_not_anomaly_detection():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    result = comparison.compare(
        {
            "cpu_usage": 90,
            "memory_usage": 95,
        }
    )

    assert "cpu_usage" in result
    assert "memory_usage" in result
    assert not hasattr(comparison, "is_anomaly")


def test_comparison_is_not_trend_detection():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "trend")
    assert not hasattr(comparison, "detect_trend")


def test_comparison_is_not_recurring_problem_detection():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    assert not hasattr(comparison, "recurring")
    assert not hasattr(comparison, "detect_recurring")


def test_comparison_requires_current_sample():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    try:
        comparison.compare(None)
        assert False
    except ValueError:
        assert True


def test_comparison_requires_dictionary_current_sample():
    baseline = build_baseline()

    comparison = BaselineComparison(baseline)

    try:
        comparison.compare(["cpu_usage", 50])
        assert False
    except ValueError:
        assert True


def test_comparison_requires_existing_baseline_sample():
    baseline = HealthBaseline(build_machine())

    comparison = BaselineComparison(baseline)

    try:
        comparison.compare({"cpu_usage": 50})
        assert False
    except ValueError:
        assert True