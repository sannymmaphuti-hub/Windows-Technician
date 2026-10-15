import pytest

from engine.case_access_policy import CaseAccessPolicy
from engine.diagnostic_case import DiagnosticCase
from engine.operation_authorization_policy import OperationAuthorizationPolicy
from engine.security_audit_event import SecurityAuditEventFactory
from engine.security_audit_history import SecurityAuditHistory
from engine.security_decision_projection import SecurityDecisionProjection
from engine.technician_identity import TechnicianIdentity


def create_context():
    technician = TechnicianIdentity(
        technician_id="TECH-001",
        name="Test Technician",
        role="TECHNICIAN",
    )

    case = DiagnosticCase()
    case.machine_id = "MACHINE-001"
    case.hostname = "TEST-PC"

    operation_policy = OperationAuthorizationPolicy()
    case_policy = CaseAccessPolicy(operation_policy)

    operation_decisions = (
        operation_policy.evaluate(technician, "VIEW_CASE"),
        operation_policy.evaluate(technician, "ASSIGN_CASE"),
    )

    case_access_decisions = (
        case_policy.evaluate(technician, case, "VIEW_CASE"),
        case_policy.evaluate(technician, case, "ASSIGN_CASE"),
    )

    history = SecurityAuditHistory()
    history.append(
        SecurityAuditEventFactory().create(
            event_type="CASE_ACCESS",
            actor_id=technician.technician_id,
            resource_id=case.case_id,
            action="VIEW_CASE",
            outcome="ALLOWED",
            reason="CASE_ACCESS_GRANTED",
        )
    )

    return SecurityDecisionProjection(
        history,
        operation_decisions,
        case_access_decisions,
    )


def test_projection_combines_security_surfaces():
    projection = create_context().projection()

    assert set(projection) == {
        "operation_decisions",
        "case_access_decisions",
        "audit_history",
        "summary",
    }


def test_projection_reports_operation_decisions():
    projection = create_context().projection()

    assert len(projection["operation_decisions"]) == 2
    assert projection["operation_decisions"][0]["allowed"] is True
    assert projection["operation_decisions"][1]["allowed"] is False


def test_projection_reports_case_access_decisions():
    projection = create_context().projection()

    assert len(projection["case_access_decisions"]) == 2
    assert projection["case_access_decisions"][0]["allowed"] is True
    assert projection["case_access_decisions"][1]["allowed"] is False


def test_projection_reports_audit_history():
    projection = create_context().projection()

    assert projection["audit_history"]["event_count"] == 1


def test_summary_counts_denials():
    summary = create_context().projection()["summary"]

    assert summary["operation_decision_count"] == 2
    assert summary["case_access_decision_count"] == 2
    assert summary["audit_event_count"] == 1
    assert summary["operation_denials"] == 1
    assert summary["case_access_denials"] == 1


def test_projection_is_defensive():
    projection = create_context()

    first = projection.projection()
    first["operation_decisions"].clear()
    first["audit_history"]["events"].clear()
    first["summary"]["operation_denials"] = 999

    second = projection.projection()

    assert len(second["operation_decisions"]) == 2
    assert second["audit_history"]["event_count"] == 1
    assert second["summary"]["operation_denials"] == 1


def test_projection_rejects_invalid_history():
    with pytest.raises(TypeError):
        SecurityDecisionProjection(object())


def test_projection_rejects_invalid_operation_decisions():
    with pytest.raises(TypeError):
        SecurityDecisionProjection(
            SecurityAuditHistory(),
            operation_decisions=[object()],
        )


def test_projection_rejects_invalid_case_access_decisions():
    with pytest.raises(TypeError):
        SecurityDecisionProjection(
            SecurityAuditHistory(),
            case_access_decisions=[object()],
        )


def test_projection_does_not_execute_or_change_decisions():
    projection = create_context()

    before = projection.projection()

    assert not hasattr(projection, "execute")
    assert not hasattr(projection, "authorize")
    assert not hasattr(projection, "remediate")
    assert projection.projection() == before


def test_repr_reports_counts_without_decision_details():
    projection = create_context()

    representation = repr(projection)

    assert "TECH-001" not in representation
    assert "operation_decisions=2" in representation
    assert "audit_events=1" in representation
