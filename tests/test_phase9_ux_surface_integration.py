from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)
from engine.remediation_action import RemediationAction
from engine.authorization_ux import AuthorizationUX
from engine.remediation_preview import RemediationPreview
from engine.status_communication import StatusCommunication
from engine.accessibility_clarity import AccessibilityClarity
from engine.technician_language import TechnicianLanguage
from engine.user_facing_language import UserFacingLanguage


def create_case():
    case = DiagnosticCase()
    case.machine_id = "machine-001"
    case.hostname = "TEST-PC"
    return case


def create_workflow():
    return TechnicianWorkflow(create_case())


def create_action():
    return RemediationAction(
        action_id="memory-review-001",
        description="Review excessive memory usage.",
        requires_authorization=True,
    )


def progress_to_action_required(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()
    workflow.require_action()


# ============================================================
# USER-FACING LANGUAGE
# ============================================================


def test_user_facing_language_translates_known_diagnostic():
    language = UserFacingLanguage()

    result = language.translate("MEMORY_PRESSURE")

    assert isinstance(result, str)
    assert result


def test_user_facing_language_has_fallback():
    language = UserFacingLanguage()

    result = language.translate("UNKNOWN_DIAGNOSTIC")

    assert isinstance(result, str)
    assert result


# ============================================================
# TECHNICIAN LANGUAGE
# ============================================================


def test_technician_language_translates_known_diagnostic():
    language = TechnicianLanguage()

    result = language.translate("MEMORY_PRESSURE")

    assert isinstance(result, str)
    assert result


def test_technician_language_has_fallback():
    language = TechnicianLanguage()

    result = language.translate("UNKNOWN_DIAGNOSTIC")

    assert isinstance(result, str)
    assert result


# ============================================================
# AUTHORIZATION UX
# ============================================================


def test_authorization_ux_reflects_unauthorized_action():
    action = create_action()

    ux = AuthorizationUX(action)

    assert ux.action_id == action.action_id
    assert ux.description == action.description
    assert ux.status == "UNAUTHORIZED"
    assert ux.message


def test_authorization_ux_reflects_authorized_action():
    action = create_action()
    action.authorize()

    ux = AuthorizationUX(action)

    assert ux.status == "AUTHORIZED"
    assert ux.message


def test_authorization_ux_reflects_denied_action():
    action = create_action()
    action.deny()

    ux = AuthorizationUX(action)

    assert ux.status == "DENIED"
    assert ux.message


# ============================================================
# REMEDIATION PREVIEW
# ============================================================


def test_remediation_preview_exposes_action_identity():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.action_id == action.action_id
    assert preview.description == action.description


def test_remediation_preview_exposes_authorization_state():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.authorization_status == "UNAUTHORIZED"
    assert preview.requires_authorization is True


def test_remediation_preview_updates_after_authorization():
    action = create_action()
    action.authorize()

    preview = RemediationPreview(action)

    assert preview.authorization_status == "AUTHORIZED"


# ============================================================
# STATUS COMMUNICATION
# ============================================================


def test_status_communication_reports_not_executed():
    action = create_action()

    communication = StatusCommunication(action)

    assert communication.message == (
        "This action has not been executed."
    )


def test_status_communication_reports_executed_state():
    action = create_action()
    action.authorize()

    action.operation = lambda: None
    action.execute()

    communication = StatusCommunication(action)

    assert communication.message == (
        "This action was executed successfully. "
        "Verification is still required."
    )


def test_status_communication_reports_failed_state():
    action = create_action()
    action.authorize()

    def failing_operation():
        raise RuntimeError("test failure")

    action.operation = failing_operation
    action.execute()

    communication = StatusCommunication(action)

    assert communication.message == (
        "This action could not be completed."
    )


# ============================================================
# ACCESSIBILITY / CLARITY
# ============================================================


def test_accessibility_clarity_labels_unauthorized_action():
    action = create_action()
    clarity = AccessibilityClarity()

    authorization_label = clarity.authorization_label(
        action.authorization_status
    )
    execution_label = clarity.execution_label(
        action.execution_status
    )

    assert authorization_label == "Authorization required"
    assert execution_label == "Not executed"


def test_accessibility_clarity_updates_after_authorization():
    action = create_action()
    clarity = AccessibilityClarity()

    action.authorize()

    authorization_label = clarity.authorization_label(
        action.authorization_status
    )
    execution_label = clarity.execution_label(
        action.execution_status
    )

    assert authorization_label == "Authorized"
    assert execution_label == "Not executed"


# ============================================================
# UX + WORKFLOW INTEGRATION
# ============================================================


def test_workflow_reaches_action_required_before_remediation():
    workflow = create_workflow()

    progress_to_action_required(workflow)

    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_action_is_unauthorized_when_workflow_requires_action():
    workflow = create_workflow()
    action = create_action()

    progress_to_action_required(workflow)

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert action.authorization_status == "UNAUTHORIZED"


def test_authorization_ux_matches_remediation_action_state():
    workflow = create_workflow()
    action = create_action()

    progress_to_action_required(workflow)

    ux = AuthorizationUX(action)

    assert workflow.state is WorkflowState.ACTION_REQUIRED
    assert ux.status == action.authorization_status


def test_preview_matches_authorization_ux():
    action = create_action()

    authorization = AuthorizationUX(action)
    preview = RemediationPreview(action)

    assert authorization.action_id == preview.action_id
    assert authorization.description == preview.description
    assert authorization.status == preview.authorization_status


# ============================================================
# AUTHORIZATION → REMEDIATION
# ============================================================


def test_authorization_changes_all_relevant_ux_state():
    action = create_action()

    before_authorization = AuthorizationUX(action)
    before_preview = RemediationPreview(action)

    assert before_authorization.status == "UNAUTHORIZED"
    assert before_preview.authorization_status == "UNAUTHORIZED"

    action.authorize()

    after_authorization = AuthorizationUX(action)
    after_preview = RemediationPreview(action)

    assert after_authorization.status == "AUTHORIZED"
    assert after_preview.authorization_status == "AUTHORIZED"


def test_authorization_does_not_execute_action():
    action = create_action()

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"


def test_preview_does_not_execute_action():
    action = create_action()

    preview = RemediationPreview(action)

    assert preview.action_id == action.action_id
    assert action.execution_status == "NOT_EXECUTED"


# ============================================================
# EXECUTION → STATUS COMMUNICATION
# ============================================================


def test_successful_execution_updates_status_communication():
    action = create_action()

    action.authorize()
    action.operation = lambda: None

    assert action.execute() is True

    communication = StatusCommunication(action)

    assert action.execution_status == "EXECUTED"
    assert communication.message == (
        "This action was executed successfully. "
        "Verification is still required."
    )


def test_failed_execution_updates_status_communication():
    action = create_action()

    action.authorize()

    def fail():
        raise RuntimeError("execution failed")

    action.operation = fail

    assert action.execute() is False

    communication = StatusCommunication(action)

    assert action.execution_status == "FAILED"
    assert communication.message == (
        "This action could not be completed."
    )


def test_execution_status_is_distinct_from_authorization_status():
    action = create_action()

    action.authorize()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "NOT_EXECUTED"

    action.operation = lambda: None
    action.execute()

    assert action.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"


# ============================================================
# ACCESSIBILITY + EXECUTION STATE
# ============================================================


def test_accessibility_clarity_reflects_successful_execution():
    action = create_action()
    clarity = AccessibilityClarity()

    action.authorize()
    action.operation = lambda: None
    action.execute()

    assert clarity.authorization_label(
        action.authorization_status
    ) == "Authorized"

    assert clarity.execution_label(
        action.execution_status
    ) == "Executed"


def test_accessibility_clarity_reflects_failed_execution():
    action = create_action()
    clarity = AccessibilityClarity()

    action.authorize()

    def fail():
        raise RuntimeError("execution failed")

    action.operation = fail
    action.execute()

    assert clarity.authorization_label(
        action.authorization_status
    ) == "Authorized"

    assert clarity.execution_label(
        action.execution_status
    ) == "Failed"


# ============================================================
# VERIFICATION BOUNDARY
# ============================================================


def test_successful_execution_does_not_mark_workflow_resolved():
    workflow = create_workflow()
    action = create_action()

    progress_to_action_required(workflow)

    action.authorize()
    action.operation = lambda: None
    action.execute()

    workflow.start_remediation()
    workflow.start_verification()

    assert action.execution_status == "EXECUTED"
    assert workflow.state is WorkflowState.VERIFYING


def test_failed_execution_does_not_mark_workflow_resolved():
    workflow = create_workflow()
    action = create_action()

    progress_to_action_required(workflow)

    action.authorize()

    def fail():
        raise RuntimeError("execution failed")

    action.operation = fail
    action.execute()

    assert action.execution_status == "FAILED"
    assert workflow.state is WorkflowState.ACTION_REQUIRED


# ============================================================
# FULL UX STATE CONSISTENCY
# ============================================================


def test_full_ux_surface_remains_consistent_before_execution():
    action = create_action()
    clarity = AccessibilityClarity()

    authorization = AuthorizationUX(action)
    preview = RemediationPreview(action)
    communication = StatusCommunication(action)

    assert authorization.status == "UNAUTHORIZED"
    assert preview.authorization_status == "UNAUTHORIZED"

    assert communication.message == (
        "This action has not been executed."
    )

    assert clarity.authorization_label(
        action.authorization_status
    ) == "Authorization required"

    assert clarity.execution_label(
        action.execution_status
    ) == "Not executed"


def test_full_ux_surface_remains_consistent_after_execution():
    action = create_action()
    clarity = AccessibilityClarity()

    action.authorize()
    action.operation = lambda: None
    action.execute()

    authorization = AuthorizationUX(action)
    preview = RemediationPreview(action)
    communication = StatusCommunication(action)

    assert authorization.status == "AUTHORIZED"
    assert preview.authorization_status == "AUTHORIZED"
    assert action.execution_status == "EXECUTED"

    assert communication.message == (
        "This action was executed successfully. "
        "Verification is still required."
    )

    assert clarity.authorization_label(
        action.authorization_status
    ) == "Authorized"

    assert clarity.execution_label(
        action.execution_status
    ) == "Executed"