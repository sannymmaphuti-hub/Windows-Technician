# ==========================================
# Windows Technician v0.8
# ANOMALY DETECTION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.health_baseline import HealthBaseline
from engine.baseline_comparison import BaselineComparison
from engine.anomaly_detection import AnomalyDetector


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_comparison():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample(
        {
            "cpu_usage": 40,
            "memory_usage": 60,
            "disk_usage": 50,
        }
    )

    return BaselineComparison(baseline)


def build_detector():
    return AnomalyDetector(build_comparison())


def test_anomaly_detector_requires_baseline_comparison():
    comparison = build_comparison()

    detector = AnomalyDetector(comparison)

    assert detector.comparison is comparison


def test_anomaly_detector_preserves_machine_identity():
    detector = build_detector()

    assert detector.machine_id == "machine-001"
    assert detector.hostname == "REMOTE-PC"


def test_anomaly_detector_can_classify_large_difference_as_anomaly():
    detector = build_detector()

    result = detector.detect(
        {
            "cpu_usage": 90,
        }
    )

    assert result["cpu_usage"] is True


def test_anomaly_detector_can_classify_small_difference_as_normal():
    detector = build_detector()

    result = detector.detect(
        {
            "cpu_usage": 42,
        }
    )

    assert result["cpu_usage"] is False


def test_anomaly_detector_uses_configured_threshold():
    detector = build_detector()

    result = detector.detect(
        {
            "cpu_usage": 50,
        }
    )

    assert result["cpu_usage"] is False


def test_anomaly_detector_flags_difference_above_threshold():
    detector = build_detector()

    result = detector.detect(
        {
            "cpu_usage": 51,
        }
    )

    assert result["cpu_usage"] is True


def test_anomaly_detector_can_detect_multiple_dimensions():
    detector = build_detector()

    result = detector.detect(
        {
            "cpu_usage": 90,
            "memory_usage": 95,
            "disk_usage": 55,
        }
    )

    assert result["cpu_usage"] is True
    assert result["memory_usage"] is True
    assert result["disk_usage"] is False


def test_anomaly_detector_does_not_modify_baseline():
    comparison = build_comparison()
    detector = AnomalyDetector(comparison)

    original_samples = list(comparison.baseline.samples)

    detector.detect(
        {
            "cpu_usage": 90,
            "memory_usage": 95,
        }
    )

    assert comparison.baseline.samples == original_samples


def test_anomaly_detector_does_not_modify_machine_state():
    detector = build_detector()
    machine = detector.comparison.baseline.machine

    detector.detect(
        {
            "cpu_usage": 90,
        }
    )

    assert machine.health_state == "UNKNOWN"
    assert machine.connection_state == "UNKNOWN"


def test_anomaly_detector_does_not_authorize_remediation():
    detector = build_detector()

    assert not hasattr(detector, "authorize")
    assert not hasattr(detector, "approve")


def test_anomaly_detector_does_not_execute_remediation():
    detector = build_detector()

    assert not hasattr(detector, "execute")
    assert not hasattr(detector, "remediate")


def test_anomaly_detector_does_not_create_remediation_action():
    detector = build_detector()

    assert not hasattr(detector, "remediation_action")
    assert not hasattr(detector, "remediation_actions")


def test_anomaly_detector_does_not_create_alert():
    detector = build_detector()

    assert not hasattr(detector, "alert")
    assert not hasattr(detector, "proactive_alert")


def test_anomaly_detector_does_not_create_diagnostic_case():
    detector = build_detector()

    assert not hasattr(detector, "case")
    assert not hasattr(detector, "diagnostic_case")


def test_anomaly_detector_does_not_perform_diagnosis():
    detector = build_detector()

    assert not hasattr(detector, "diagnose")
    assert not hasattr(detector, "diagnostic_pipeline")


def test_anomaly_detector_does_not_retry():
    detector = build_detector()

    assert not hasattr(detector, "retry")
    assert not hasattr(detector, "retry_count")


def test_anomaly_detector_does_not_recover():
    detector = build_detector()

    assert not hasattr(detector, "recover")
    assert not hasattr(detector, "recovery")


def test_anomaly_detector_requires_dictionary_input():
    detector = build_detector()

    try:
        detector.detect(None)
        assert False
    except ValueError:
        assert True


def test_anomaly_detector_is_distinct_from_comparison():
    detector = build_detector()

    assert hasattr(detector, "comparison")
    assert not hasattr(detector, "compare")


def test_anomaly_detector_does_not_change_comparison_result():
    detector = build_detector()

    comparison_result = detector.comparison.compare(
        {
            "cpu_usage": 90,
        }
    )

    detector.detect(
        {
            "cpu_usage": 90,
        }
    )

    assert comparison_result["cpu_usage"] == 50


def test_anomaly_detection_is_classification_not_remediation():
    detector = build_detector()

    result = detector.detect(
        {
            "memory_usage": 95,
        }
    )

    assert result["memory_usage"] is True
    assert not hasattr(detector, "execute")


def test_anomaly_detection_does_not_equal_authorization():
    detector = build_detector()

    result = detector.detect(
        {
            "memory_usage": 95,
        }
    )

    assert result["memory_usage"] is True
    assert not hasattr(detector, "authorize")


def test_anomaly_detection_preserves_platform_information():
    detector = build_detector()

    assert detector.comparison.baseline.machine.platform == "Windows"
    assert (
        detector.comparison.baseline.machine.operating_system
        == "Windows 11"
    )