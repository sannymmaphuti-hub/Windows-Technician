from engine.case_access_policy import CaseAccessPolicy
from engine.case_ownership import CaseOwnership
from engine.case_status_coordination import CaseStatusCoordinator
from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.operation_authorization_policy import OperationAuthorizationPolicy
from engine.security_audit_event import SecurityAuditEventFactory
from engine.security_audit_history import SecurityAuditHistory
from engine.security_decision_projection import SecurityDecisionProjection
from engine.technician_collaboration_boundary import TechnicianCollaborationBoundary
from engine.technician_identity import TechnicianIdentity
from engine.technician_permissions import TechnicianPermission
from engine.technician_role_policy import TechnicianRolePolicy
from engine.technician_workflow import TechnicianWorkflow


def create_context():
    case = DiagnosticCase()
    case.machine_id = "MACHINE-001"
    case.hostname = "TEST-PC"

    workflow = TechnicianWorkflow(case)
    technician = TechnicianIdentity(
        technician_id="TECH-001",
        name="Alice",
        role="TECHNICIAN",
    )

    ownership = CaseOwnership(case, technician)
    boundary = TechnicianCollaborationBoundary(workflow)
    status = CaseStatusCoordinator(workflow)
    timeline = CaseTimeline(case)

    role_policy = TechnicianRolePolicy()
    operation_policy = OperationAuthorizationPolicy(role_policy)
    case_policy = CaseAccessPolicy(operation_policy)

    history = SecurityAuditHistory()
    event_factory = SecurityAuditEventFactory()

    return {
        "case": case,
        "workflow": workflow,
        "technician": technician,
        "ownership": ownership,
        "boundary": boundary,
        "status": status,
        "timeline": timeline,
        "role_policy": role_policy,
        "operation_policy": operation_policy,
        "case_policy": case_policy,
        "history": history,
        "event_factory": event_factory,
    }


def record_decision(context, decision):
    context["history"].append(
        context["event_factory"].create(
            event_type="SECURITY_DECISION",
            actor_id=decision.technician_id,
            resource_id=decision.case_id or "UNKNOWN_RESOURCE",
            action=decision.operation,
            outcome="ALLOWED" if decision.allowed else "DENIED",
            reason=decision.reason,
        )
    )


def test_security_integration_preserves_canonical_case():
    context = create_context()

    assert context["boundary"].case is context["case"]
    assert context["ownership"].case is context["case"]
    assert context["status"].case is context["case"]
    assert context["timeline"].case is context["case"]


def test_role_policy_and_operation_policy_agree():
    context = create_context()
    technician = context["technician"]

    assert context["role_policy"].allows(
        technician, TechnicianPermission.VIEW_CASE
    )

    decision = context["operation_policy"].evaluate(
        technician, "VIEW_CASE"
    )

    assert decision.allowed


def test_case_access_respects_role_permissions():
    context = create_context()

    decision = context["case_policy"].evaluate(
        context["technician"],
        context["case"],
        "ASSIGN_CASE",
    )

    assert not decision.allowed
    assert decision.reason == "PERMISSION_DENIED"


def test_case_access_respects_ownership():
    context = create_context()

    other = TechnicianIdentity(
        technician_id="TECH-002",
        name="Bob",
        role="TECHNICIAN",
    )

    decision = context["case_policy"].evaluate(
        other,
        context["case"],
        "VIEW_CASE",
        context["ownership"],
    )

    assert not decision.allowed
    assert decision.reason == "CASE_NOT_OWNED_BY_TECHNICIAN"


def test_security_decisions_can_be_recorded_in_audit_history():
    context = create_context()

    decision = context["case_policy"].evaluate(
        context["technician"],
        context["case"],
        "VIEW_CASE",
        context["ownership"],
    )

    record_decision(context, decision)

    assert context["history"].event_count == 1
    assert context["history"].events[0].outcome == "ALLOWED"


def test_denied_decision_can_be_audited():
    context = create_context()

    decision = context["case_policy"].evaluate(
        context["technician"],
        context["case"],
        "ASSIGN_CASE",
    )

    record_decision(context, decision)

    event = context["history"].events[0]

    assert event.outcome == "DENIED"
    assert event.reason == "PERMISSION_DENIED"


def test_security_projection_combines_decisions_and_history():
    context = create_context()

    operation_decision = context["operation_policy"].evaluate(
        context["technician"], "VIEW_CASE"
    )
    case_decision = context["case_policy"].evaluate(
        context["technician"],
        context["case"],
        "VIEW_CASE",
        context["ownership"],
    )

    record_decision(context, case_decision)

    projection = SecurityDecisionProjection(
        context["history"],
        operation_decisions=[operation_decision],
        case_access_decisions=[case_decision],
    ).projection()

    assert projection["summary"]["operation_decision_count"] == 1
    assert projection["summary"]["case_access_decision_count"] == 1
    assert projection["summary"]["audit_event_count"] == 1


def test_security_evaluation_does_not_change_workflow():
    context = create_context()
    initial_state = context["workflow"].state

    context["operation_policy"].evaluate(
        context["technician"], "VIEW_CASE"
    )
    context["case_policy"].evaluate(
        context["technician"],
        context["case"],
        "VIEW_CASE",
        context["ownership"],
    )

    assert context["workflow"].state == initial_state


def test_security_integration_does_not_execute_remediation():
    context = create_context()
    technician = context["technician"]

    assert not context["operation_policy"].evaluate(
        technician, "EXECUTE_REMEDIATION"
    ).allowed

    assert not context["operation_policy"].evaluate(
        technician, "AUTHORIZE_REMEDIATION"
    ).allowed

    assert context["workflow"].state.value == "OPEN"


def test_security_projections_do_not_mutate_case():
    context = create_context()
    initial_case_id = context["case"].case_id
    initial_state = context["workflow"].state

    context["boundary"].projection()
    context["status"].projection()
    context["timeline"].projection()
    SecurityDecisionProjection(
        context["history"]
    ).projection()

    assert context["case"].case_id == initial_case_id
    assert context["workflow"].state == initial_state
