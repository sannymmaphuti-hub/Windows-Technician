# ==========================================
# Windows Technician v0.8
# PROACTIVE SAFETY BOUNDARY TESTS
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert
from engine.proactive_case_creation import ProactiveCaseCreator
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


def build_case():
    recommendation = build_recommendation()
    creator = ProactiveCaseCreator()

    return creator.create(recommendation)


def test_proactive_alert_does_not_authorize():
    alert = build_alert()

    assert not hasattr(alert, "authorize")
    assert not hasattr(alert, "approve")
    assert not hasattr(alert, "authorization_status")


def test_proactive_recommendation_does_not_authorize():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "authorize")
    assert not hasattr(recommendation, "approve")
    assert not hasattr(recommendation, "authorization_status")


def test_proactive_case_does_not_authorize():
    case = build_case()

    assert not hasattr(case, "authorize")
    assert not hasattr(case, "approve")
    assert not hasattr(case, "authorization_status")


def test_proactive_alert_does_not_execute():
    alert = build_alert()

    assert not hasattr(alert, "execute")
    assert not hasattr(alert, "remediate")


def test_proactive_recommendation_does_not_execute():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "execute")
    assert not hasattr(recommendation, "remediate")


def test_proactive_case_does_not_execute():
    case = build_case()

    assert not hasattr(case, "execute")
    assert not hasattr(case, "remediate")


def test_proactive_alert_has_no_remediation_action():
    alert = build_alert()

    assert not hasattr(alert, "remediation_action")
    assert not hasattr(alert, "remediation_actions")
    assert not hasattr(alert, "operation")


def test_proactive_recommendation_has_no_remediation_action():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "remediation_action")
    assert not hasattr(recommendation, "remediation_actions")
    assert not hasattr(recommendation, "operation")


def test_proactive_case_has_no_remediation_action():
    case = build_case()

    assert not hasattr(case, "remediation_action")
    assert not hasattr(case, "remediation_actions")
    assert not hasattr(case, "operation")


def test_proactive_alert_does_not_create_workflow():
    alert = build_alert()

    assert not hasattr(alert, "workflow")
    assert not hasattr(alert, "technician_workflow")


def test_proactive_recommendation_does_not_create_workflow():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "workflow")
    assert not hasattr(recommendation, "technician_workflow")


def test_proactive_case_does_not_create_workflow():
    case = build_case()

    assert not hasattr(case, "workflow")
    assert not hasattr(case, "technician_workflow")


def test_proactive_alert_does_not_perform_diagnosis():
    alert = build_alert()

    assert not hasattr(alert, "diagnose")
    assert not hasattr(alert, "diagnostic_pipeline")


def test_proactive_recommendation_does_not_perform_diagnosis():
    recommendation = build_recommendation()

    assert not hasattr(recommendation, "diagnose")
    assert not hasattr(recommendation, "diagnostic_pipeline")


def test_proactive_case_does_not_perform_diagnosis():
    case = build_case()

    assert not hasattr(case, "diagnose")
    assert not hasattr(case, "diagnostic_pipeline")


def test_proactive_chain_preserves_detection_state():
    alert = build_alert()
    recommendation = build_recommendation(alert)
    creator = ProactiveCaseCreator()

    case = creator.create(recommendation)

    assert alert.status == "ACTIVE"
    assert recommendation.status == "PENDING"
    assert case.proactive_alert is alert
    assert case.proactive_recommendation is recommendation


def test_proactive_chain_does_not_execute_anything():
    alert = build_alert()
    recommendation = build_recommendation(alert)
    creator = ProactiveCaseCreator()

    case = creator.create(recommendation)

    assert alert.status == "ACTIVE"
    assert recommendation.status == "PENDING"
    assert isinstance(case, DiagnosticCase)


def test_proactive_case_creation_is_not_remediation():
    case = build_case()

    assert isinstance(case, DiagnosticCase)
    assert not hasattr(case, "execution_status")
    assert not hasattr(case, "handler")


def test_proactive_detection_is_not_authorization():
    alert = build_alert()
    recommendation = build_recommendation(alert)

    assert alert.status == "ACTIVE"
    assert recommendation.status == "PENDING"

    assert not hasattr(alert, "authorization_status")
    assert not hasattr(recommendation, "authorization_status")


def test_proactive_recommendation_requires_separate_authorization():
    recommendation = build_recommendation()

    assert recommendation.status == "PENDING"
    assert not hasattr(recommendation, "authorize")


def test_proactive_case_uses_existing_diagnostic_case():
    case = build_case()

    assert type(case) is DiagnosticCase


def test_proactive_case_does_not_bypass_existing_case_model():
    case = build_case()

    assert isinstance(case, DiagnosticCase)
    assert hasattr(case, "case_id")
    assert hasattr(case, "lifecycle_state")
    assert case.lifecycle_state == "OPEN"


def test_proactive_chain_is_safe_before_technician_action():
    alert = build_alert()
    recommendation = build_recommendation(alert)
    creator = ProactiveCaseCreator()

    case = creator.create(recommendation)

    assert alert.status == "ACTIVE"
    assert recommendation.status == "PENDING"
    assert case.lifecycle_state == "OPEN"

    assert not hasattr(alert, "execute")
    assert not hasattr(recommendation, "execute")
    assert not hasattr(case, "execute")


def test_proactive_chain_preserves_machine_identity():
    machine = build_machine()
    alert = build_alert(machine)
    recommendation = build_recommendation(alert)
    creator = ProactiveCaseCreator()

    case = creator.create(recommendation)

    assert alert.machine is machine
    assert recommendation.machine_id == machine.machine_id
    assert case.machine_id == machine.machine_id
    assert case.hostname == machine.hostname