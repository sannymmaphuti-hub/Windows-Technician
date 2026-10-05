# ==========================================
# Windows Technician v0.8
# RECURRING PROBLEM DETECTION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.health_baseline import HealthBaseline
from engine.recurring_problem_detection import RecurringProblemDetector


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_baseline():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample({"memory_usage": 90})
    baseline.add_sample({"memory_usage": 60})
    baseline.add_sample({"memory_usage": 92})
    baseline.add_sample({"memory_usage": 65})
    baseline.add_sample({"memory_usage": 91})

    return baseline


def build_detector():
    return RecurringProblemDetector(build_baseline())


def test_recurring_detector_requires_health_baseline():
    baseline = build_baseline()

    detector = RecurringProblemDetector(baseline)

    assert detector.baseline is baseline


def test_recurring_detector_preserves_machine_identity():
    detector = build_detector()

    assert detector.machine_id == "machine-001"
    assert detector.hostname == "REMOTE-PC"


def test_recurring_detector_detects_repeated_high_values():
    detector = build_detector()

    result = detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert result["memory_usage"] is True


def test_recurring_detector_does_not_flag_insufficient_occurrences():
    detector = build_detector()

    result = detector.detect(
        threshold=80,
        minimum_occurrences=4,
    )

    assert result["memory_usage"] is False


def test_recurring_detector_does_not_flag_values_below_threshold():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample({"memory_usage": 60})
    baseline.add_sample({"memory_usage": 65})
    baseline.add_sample({"memory_usage": 70})
    baseline.add_sample({"memory_usage": 75})

    detector = RecurringProblemDetector(baseline)

    result = detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert result["memory_usage"] is False


def test_recurring_detector_supports_multiple_dimensions():
    baseline = HealthBaseline(build_machine())

    baseline.add_sample(
        {
            "memory_usage": 90,
            "cpu_usage": 30,
        }
    )

    baseline.add_sample(
        {
            "memory_usage": 60,
            "cpu_usage": 95,
        }
    )

    baseline.add_sample(
        {
            "memory_usage": 92,
            "cpu_usage": 40,
        }
    )

    baseline.add_sample(
        {
            "memory_usage": 65,
            "cpu_usage": 96,
        }
    )

    baseline.add_sample(
        {
            "memory_usage": 91,
            "cpu_usage": 35,
        }
    )

    detector = RecurringProblemDetector(baseline)

    result = detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert result["memory_usage"] is True
    assert result["cpu_usage"] is False


def test_recurring_detector_does_not_modify_samples():
    baseline = build_baseline()
    original_samples = list(baseline.samples)

    detector = RecurringProblemDetector(baseline)

    detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert baseline.samples == original_samples


def test_recurring_detector_does_not_add_samples():
    baseline = build_baseline()

    detector = RecurringProblemDetector(baseline)

    detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert len(baseline.samples) == 5


def test_recurring_detector_does_not_change_health_state():
    baseline = build_baseline()

    detector = RecurringProblemDetector(baseline)

    detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert baseline.machine.health_state == "UNKNOWN"


def test_recurring_detector_does_not_change_connection_state():
    baseline = build_baseline()

    detector = RecurringProblemDetector(baseline)

    detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert baseline.machine.connection_state == "UNKNOWN"


def test_recurring_detector_does_not_authorize_remediation():
    detector = build_detector()

    assert not hasattr(detector, "authorize")
    assert not hasattr(detector, "approve")


def test_recurring_detector_does_not_execute_remediation():
    detector = build_detector()

    assert not hasattr(detector, "execute")
    assert not hasattr(detector, "remediate")


def test_recurring_detector_does_not_create_remediation_action():
    detector = build_detector()

    assert not hasattr(detector, "remediation_action")
    assert not hasattr(detector, "remediation_actions")


def test_recurring_detector_does_not_create_alert():
    detector = build_detector()

    assert not hasattr(detector, "alert")
    assert not hasattr(detector, "proactive_alert")


def test_recurring_detector_does_not_create_diagnostic_case():
    detector = build_detector()

    assert not hasattr(detector, "case")
    assert not hasattr(detector, "diagnostic_case")


def test_recurring_detector_does_not_perform_diagnosis():
    detector = build_detector()

    assert not hasattr(detector, "diagnose")
    assert not hasattr(detector, "diagnostic_pipeline")


def test_recurring_detector_does_not_retry():
    detector = build_detector()

    assert not hasattr(detector, "retry")
    assert not hasattr(detector, "retry_count")


def test_recurring_detector_does_not_recover():
    detector = build_detector()

    assert not hasattr(detector, "recover")
    assert not hasattr(detector, "recovery")


def test_recurring_detector_is_distinct_from_trend_detection():
    detector = build_detector()

    assert not hasattr(detector, "trend")
    assert not hasattr(detector, "detect_trend")


def test_recurring_detector_preserves_platform_information():
    detector = build_detector()

    assert detector.baseline.machine.platform == "Windows"
    assert (
        detector.baseline.machine.operating_system
        == "Windows 11"
    )


def test_recurring_detector_requires_valid_threshold():
    detector = build_detector()

    try:
        detector.detect(
            threshold=None,
            minimum_occurrences=3,
        )
        assert False
    except ValueError:
        assert True


def test_recurring_detector_requires_valid_occurrence_count():
    detector = build_detector()

    try:
        detector.detect(
            threshold=80,
            minimum_occurrences=0,
        )
        assert False
    except ValueError:
        assert True


def test_recurring_detection_is_analysis_only():
    detector = build_detector()

    result = detector.detect(
        threshold=80,
        minimum_occurrences=3,
    )

    assert result["memory_usage"] is True
    assert not hasattr(detector, "execute")
    assert not hasattr(detector, "authorize")