# ==========================================
# Windows Technician v0.8
# PROACTIVE CASE CREATION TESTS
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


def build_creator():
    return ProactiveCaseCreator()


def test_proactive_case_creator_exists():
    creator = build_creator()

    assert creator is not None


def test_proactive_case_creator_creates_diagnostic_case():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert isinstance(case, DiagnosticCase)


def test_proactive_case_creation_requires_proactive_recommendation():
    creator = build_creator()

    try:
        creator.create(None)
    except ValueError:
        return

    assert False, "Expected ValueError"


def test_proactive_case_preserves_machine_identity():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert case.machine_id == "machine-001"


def test_proactive_case_preserves_hostname():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert case.hostname == "REMOTE-PC"


def test_proactive_case_preserves_proactive_recommendation():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert case.proactive_recommendation is recommendation


def test_proactive_case_preserves_proactive_alert():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert case.proactive_alert is recommendation.alert


def test_proactive_case_is_not_a_new_case_type():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert type(case) is DiagnosticCase


def test_proactive_case_does_not_authorize_remediation():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert not hasattr(case, "authorize")
    assert not hasattr(case, "approve")


def test_proactive_case_does_not_execute_remediation():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert not hasattr(case, "execute")
    assert not hasattr(case, "remediate")


def test_proactive_case_does_not_contain_remediation_action():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert not hasattr(case, "remediation_action")
    assert not hasattr(case, "remediation_actions")


def test_proactive_case_does_not_create_automatic_workflow():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert not hasattr(case, "workflow")
    assert not hasattr(case, "technician_workflow")


def test_proactive_case_does_not_perform_diagnosis():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert not hasattr(case, "diagnose")
    assert not hasattr(case, "diagnostic_pipeline")


def test_proactive_case_does_not_retry():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert not hasattr(case, "retry")
    assert not hasattr(case, "retry_count")


def test_proactive_case_does_not_recover():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert not hasattr(case, "recover")
    assert not hasattr(case, "recovery")


def test_proactive_case_creation_does_not_change_recommendation_status():
    creator = build_creator()
    recommendation = build_recommendation()

    creator.create(recommendation)

    assert recommendation.status == "PENDING"


def test_proactive_case_creation_does_not_change_alert_status():
    creator = build_creator()
    recommendation = build_recommendation()

    creator.create(recommendation)

    assert recommendation.alert.status == "ACTIVE"


def test_proactive_case_creation_is_machine_specific():
    machine_a = build_machine()

    machine_b = ManagedMachine(
        machine_id="machine-002",
        hostname="SECOND-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    recommendation_a = build_recommendation(build_alert(machine_a))
    recommendation_b = build_recommendation(build_alert(machine_b))

    creator = build_creator()

    case_a = creator.create(recommendation_a)
    case_b = creator.create(recommendation_b)

    assert case_a.machine_id != case_b.machine_id
    assert case_a.hostname != case_b.hostname


def test_proactive_case_creation_does_not_authorize_anything():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert recommendation.status == "PENDING"
    assert recommendation.alert.status == "ACTIVE"
    assert not hasattr(case, "authorization_status")


def test_proactive_case_creation_is_detection_to_case_boundary():
    creator = build_creator()
    recommendation = build_recommendation()

    case = creator.create(recommendation)

    assert isinstance(case, DiagnosticCase)
    assert case.proactive_recommendation is recommendation
    assert case.proactive_alert is recommendation.alert