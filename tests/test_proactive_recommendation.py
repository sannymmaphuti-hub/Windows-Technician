# ==========================================
# Windows Technician v0.8
# PROACTIVE RECOMMENDATION TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.proactive_recommendation import ProactiveRecommendation


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_alert(machine=None):
    if machine is None:
        machine = build_machine()

    return ProactiveAlert(
        machine=machine,
        alert_type="ANOMALY",
        metric="memory_usage",
        message="Memory usage is significantly above baseline.",
    )


def build_recommendation(alert=None):
    if alert is None:
        alert = build_alert()

    return ProactiveRecommendation(
        alert=alert,
        recommendation="Review applications consuming excessive memory.",
    )


def test_proactive_recommendation_requires_proactive_alert():
    alert = build_alert()

    recommendation = build_recommendation(alert)

    assert recommendation.alert is alert


def test_proactive_recommendation_preserves_machine_identity():
    recommendation = build_recommendation()

    assert recommendation.machine_id == "machine-001"
    assert recommendation.hostname == "REMOTE-PC"


def test_proactive_recommendation_preserves_alert():
    alert = build_alert()

    recommendation = build_recommendation(alert)

    assert recommendation.alert is alert


def test_proactive_recommendation_preserves_recommendation_text():
    recommendation = build_recommendation()

    assert (
        recommendation.recommendation
        == "Review applications consuming excessive memory."
    )


def test_proactive_recommendation_is_pending_by_default():
    recommendation = build_recommendation()

    assert recommendation.status == "PENDING"


def test_proactive_recommendation_can_be_acknowledged():
    recommendation = build_recommendation()

    recommendation.acknowledge()

    assert recommendation.status == "ACKNOWLEDGED"


def test_proactive_recommendation_can_be_dismissed():
    recommendation = build_recommendation()

    recommendation.dismiss()

    assert recommendation.status == "DISMISSED"


def test_proactive_recommendation_does_not_authorize_remediation():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "authorize")
    assert not hasattr(recommendation, "approve")


def test_proactive_recommendation_does_not_execute_remediation():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "execute")
    assert not hasattr(recommendation, "remediate")


def test_proactive_recommendation_does_not_contain_remediation_action():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "remediation_action")
    assert not hasattr(recommendation, "remediation_actions")


def test_proactive_recommendation_does_not_create_diagnostic_case():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "case")
    assert not hasattr(recommendation, "diagnostic_case")


def test_proactive_recommendation_does_not_create_workflow():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "workflow")
    assert not hasattr(recommendation, "technician_workflow")


def test_proactive_recommendation_does_not_perform_diagnosis():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "diagnose")
    assert not hasattr(recommendation, "diagnostic_pipeline")


def test_proactive_recommendation_does_not_retry():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "retry")
    assert not hasattr(recommendation, "retry_count")


def test_proactive_recommendation_does_not_recover():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "recover")
    assert not hasattr(recommendation, "recovery")


def test_proactive_recommendation_is_machine_specific():
    machine_a = build_machine()

    machine_b = ManagedMachine(
        machine_id="machine-002",
        hostname="SECOND-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    alert_a = build_alert(machine_a)
    alert_b = build_alert(machine_b)

    recommendation_a = build_recommendation(alert_a)
    recommendation_b = build_recommendation(alert_b)

    assert recommendation_a.machine_id != recommendation_b.machine_id
    assert recommendation_a.hostname != recommendation_b.hostname


def test_proactive_recommendation_status_is_not_execution_status():
    recommendation = build_recommendation()

    assert recommendation.status == "PENDING"
    assert not hasattr(recommendation, "execution_status")


def test_proactive_recommendation_status_is_not_authorization_status():
    recommendation = build_recommendation()

    assert recommendation.status == "PENDING"
    assert not hasattr(recommendation, "authorization_status")


def test_proactive_recommendation_does_not_equal_diagnosis():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "findings")
    assert not hasattr(recommendation, "root_causes")


def test_proactive_recommendation_preserves_alert_state():
    alert = build_alert()
    recommendation = build_recommendation(alert)

    alert.acknowledge()

    assert alert.status == "ACKNOWLEDGED"
    assert recommendation.alert is alert


def test_proactive_recommendation_is_detection_output_not_authorization():
    recommendation = build_recommendation()

    assert recommendation.machine_id is not None
    assert recommendation.recommendation is not None
    assert recommendation.status == "PENDING"