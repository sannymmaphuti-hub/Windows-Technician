# ==========================================
# Windows Technician v0.8
# TREND DETECTION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.health_baseline import HealthBaseline
from engine.trend_detection import TrendDetector


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_baseline():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample({"memory_usage": 60})
    baseline.add_sample({"memory_usage": 65})
    baseline.add_sample({"memory_usage": 70})

    return baseline


def build_detector():
    return TrendDetector(build_baseline())


def test_trend_detector_requires_health_baseline():
    baseline = build_baseline()

    detector = TrendDetector(baseline)

    assert detector.baseline is baseline


def test_trend_detector_preserves_machine_identity():
    detector = build_detector()

    assert detector.machine_id == "machine-001"
    assert detector.hostname == "REMOTE-PC"


def test_trend_detector_detects_increasing_trend():
    detector = build_detector()

    result = detector.detect()

    assert result["memory_usage"] == "INCREASING"


def test_trend_detector_detects_decreasing_trend():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample({"memory_usage": 80})
    baseline.add_sample({"memory_usage": 70})
    baseline.add_sample({"memory_usage": 60})

    detector = TrendDetector(baseline)

    result = detector.detect()

    assert result["memory_usage"] == "DECREASING"


def test_trend_detector_detects_stable_values():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample({"memory_usage": 60})
    baseline.add_sample({"memory_usage": 60})
    baseline.add_sample({"memory_usage": 60})

    detector = TrendDetector(baseline)

    result = detector.detect()

    assert result["memory_usage"] == "STABLE"


def test_trend_detector_supports_multiple_dimensions():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample(
        {
            "cpu_usage": 40,
            "memory_usage": 60,
        }
    )

    baseline.add_sample(
        {
            "cpu_usage": 50,
            "memory_usage": 60,
        }
    )

    baseline.add_sample(
        {
            "cpu_usage": 60,
            "memory_usage": 60,
        }
    )

    detector = TrendDetector(baseline)

    result = detector.detect()

    assert result["cpu_usage"] == "INCREASING"
    assert result["memory_usage"] == "STABLE"


def test_trend_detector_requires_enough_samples():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample({"memory_usage": 60})

    detector = TrendDetector(baseline)

    try:
        detector.detect()
        assert False
    except ValueError:
        assert True


def test_trend_detector_does_not_modify_samples():
    baseline = build_baseline()

    original_samples = list(baseline.samples)

    detector = TrendDetector(baseline)
    detector.detect()

    assert baseline.samples == original_samples


def test_trend_detector_does_not_add_samples():
    baseline = build_baseline()

    detector = TrendDetector(baseline)
    detector.detect()

    assert len(baseline.samples) == 3


def test_trend_detector_does_not_change_machine_health():
    baseline = build_baseline()
    detector = TrendDetector(baseline)

    detector.detect()

    assert baseline.machine.health_state == "UNKNOWN"


def test_trend_detector_does_not_change_machine_connection():
    baseline = build_baseline()
    detector = TrendDetector(baseline)

    detector.detect()

    assert baseline.machine.connection_state == "UNKNOWN"


def test_trend_detector_does_not_authorize_remediation():
    detector = build_detector()

    assert not hasattr(detector, "authorize")
    assert not hasattr(detector, "approve")


def test_trend_detector_does_not_execute_remediation():
    detector = build_detector()

    assert not hasattr(detector, "execute")
    assert not hasattr(detector, "remediate")


def test_trend_detector_does_not_create_remediation_action():
    detector = build_detector()

    assert not hasattr(detector, "remediation_action")
    assert not hasattr(detector, "remediation_actions")


def test_trend_detector_does_not_create_alert():
    detector = build_detector()

    assert not hasattr(detector, "alert")
    assert not hasattr(detector, "proactive_alert")


def test_trend_detector_does_not_create_diagnostic_case():
    detector = build_detector()

    assert not hasattr(detector, "case")
    assert not hasattr(detector, "diagnostic_case")


def test_trend_detector_does_not_perform_diagnosis():
    detector = build_detector()

    assert not hasattr(detector, "diagnose")
    assert not hasattr(detector, "diagnostic_pipeline")


def test_trend_detector_does_not_retry():
    detector = build_detector()

    assert not hasattr(detector, "retry")
    assert not hasattr(detector, "retry_count")


def test_trend_detector_does_not_recover():
    detector = build_detector()

    assert not hasattr(detector, "recover")
    assert not hasattr(detector, "recovery")


def test_trend_detector_is_distinct_from_anomaly_detection():
    detector = build_detector()

    assert not hasattr(detector, "anomaly")
    assert not hasattr(detector, "is_anomaly")


def test_trend_detector_preserves_platform_information():
    detector = build_detector()

    assert detector.baseline.machine.platform == "Windows"
    assert (
        detector.baseline.machine.operating_system
        == "Windows 11"
    )


def test_trend_detector_does_not_create_recommendation():
    detector = build_detector()

    assert not hasattr(detector, "recommendation")
    assert not hasattr(detector, "recommendations")


def test_trend_detection_is_observation_analysis_only():
    detector = build_detector()

    result = detector.detect()

    assert result["memory_usage"] == "INCREASING"
    assert not hasattr(detector, "execute")
    assert not hasattr(detector, "authorize")