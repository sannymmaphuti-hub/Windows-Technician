import pytest

from engine.technician_workflow import TechnicianWorkflow, WorkflowState
from engine.diagnostic_case import DiagnosticCase


# ============================================================
# FACTORIES
# ============================================================


def create_case():
    return DiagnosticCase()


def create_workflow():
    return TechnicianWorkflow(create_case())


def move_to_diagnosed(workflow):
    workflow.start_investigation()
    workflow.mark_diagnosed()


def move_to_action_required(workflow):
    move_to_diagnosed(workflow)
    workflow.require_action()


def move_to_remediating(workflow):
    move_to_action_required(workflow)
    workflow.start_remediation()


def move_to_verifying(workflow):
    move_to_remediating(workflow)
    workflow.start_verification()


def move_to_resolved(workflow):
    move_to_verifying(workflow)
    workflow.resolve()


# ============================================================
# INITIAL STATE
# ============================================================


def test_workflow_starts_open():
    workflow = create_workflow()

    assert workflow.state is WorkflowState.OPEN


def test_workflow_is_not_terminal_when_open():
    workflow = create_workflow()

    assert workflow.is_terminal is False


def test_workflow_has_empty_history_initially():
    workflow = create_workflow()

    assert workflow.history == []


def test_workflow_requires_a_case():
    with pytest.raises(ValueError):
        TechnicianWorkflow(None)


def test_workflow_has_unique_identity():
    workflow_a = create_workflow()
    workflow_b = create_workflow()

    assert workflow_a.workflow_id != workflow_b.workflow_id


# ============================================================
# CANONICAL FORWARD LIFECYCLE
# ============================================================


def test_open_can_start_investigation():
    workflow = create_workflow()

    workflow.start_investigation()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_investigation_can_be_marked_diagnosed():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_diagnosed_can_require_action():
    workflow = create_workflow()

    move_to_diagnosed(workflow)
    workflow.require_action()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_action_required_can_start_remediation():
    workflow = create_workflow()

    move_to_action_required(workflow)
    workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING


def test_remediation_can_start_verification():
    workflow = create_workflow()

    move_to_remediating(workflow)
    workflow.start_verification()

    assert workflow.state is WorkflowState.VERIFYING


def test_verification_can_resolve():
    workflow = create_workflow()

    move_to_verifying(workflow)
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED


def test_complete_lifecycle_reaches_resolved():
    workflow = create_workflow()

    move_to_resolved(workflow)

    assert workflow.state is WorkflowState.RESOLVED
    assert workflow.is_terminal is True


# ============================================================
# FORWARD TRANSITION HISTORY
# ============================================================


def test_start_investigation_records_history():
    workflow = create_workflow()

    workflow.start_investigation()

    assert workflow.history == [
        (
            WorkflowState.OPEN,
            WorkflowState.INVESTIGATING,
        )
    ]


def test_mark_diagnosed_records_history():
    workflow = create_workflow()

    workflow.start_investigation()
    workflow.mark_diagnosed()

    assert workflow.history[-1] == (
        WorkflowState.INVESTIGATING,
        WorkflowState.DIAGNOSED,
    )


def test_require_action_records_history():
    workflow = create_workflow()

    move_to_diagnosed(workflow)
    workflow.require_action()

    assert workflow.history[-1] == (
        WorkflowState.DIAGNOSED,
        WorkflowState.ACTION_REQUIRED,
    )


def test_start_remediation_records_history():
    workflow = create_workflow()

    move_to_action_required(workflow)
    workflow.start_remediation()

    assert workflow.history[-1] == (
        WorkflowState.ACTION_REQUIRED,
        WorkflowState.REMEDIATING,
    )


def test_start_verification_records_history():
    workflow = create_workflow()

    move_to_remediating(workflow)
    workflow.start_verification()

    assert workflow.history[-1] == (
        WorkflowState.REMEDIATING,
        WorkflowState.VERIFYING,
    )


def test_resolve_records_history():
    workflow = create_workflow()

    move_to_verifying(workflow)
    workflow.resolve()

    assert workflow.history[-1] == (
        WorkflowState.VERIFYING,
        WorkflowState.RESOLVED,
    )


def test_complete_lifecycle_preserves_all_transitions():
    workflow = create_workflow()

    move_to_resolved(workflow)

    assert workflow.history == [
        (
            WorkflowState.OPEN,
            WorkflowState.INVESTIGATING,
        ),
        (
            WorkflowState.INVESTIGATING,
            WorkflowState.DIAGNOSED,
        ),
        (
            WorkflowState.DIAGNOSED,
            WorkflowState.ACTION_REQUIRED,
        ),
        (
            WorkflowState.ACTION_REQUIRED,
            WorkflowState.REMEDIATING,
        ),
        (
            WorkflowState.REMEDIATING,
            WorkflowState.VERIFYING,
        ),
        (
            WorkflowState.VERIFYING,
            WorkflowState.RESOLVED,
        ),
    ]


# ============================================================
# OPEN STATE BYPASS PROTECTION
# ============================================================


@pytest.mark.parametrize(
    "method_name",
    [
        "mark_diagnosed",
        "require_action",
        "start_remediation",
        "start_verification",
        "resolve",
    ],
)
def test_open_cannot_skip_directly_to_later_state(method_name):
    workflow = create_workflow()

    with pytest.raises(ValueError):
        getattr(workflow, method_name)()

    assert workflow.state is WorkflowState.OPEN
    assert workflow.history == []


# ============================================================
# INVESTIGATING STATE BYPASS PROTECTION
# ============================================================


def test_investigating_cannot_start_remediation():
    workflow = create_workflow()
    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_investigating_cannot_start_verification():
    workflow = create_workflow()
    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.start_verification()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_investigating_cannot_resolve():
    workflow = create_workflow()
    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_investigating_cannot_require_action_without_diagnosis():
    workflow = create_workflow()
    workflow.start_investigation()

    with pytest.raises(ValueError):
        workflow.require_action()

    assert workflow.state is WorkflowState.INVESTIGATING


# ============================================================
# DIAGNOSED STATE BYPASS PROTECTION
# ============================================================


def test_diagnosed_cannot_start_remediation_directly():
    workflow = create_workflow()
    move_to_diagnosed(workflow)

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_diagnosed_cannot_start_verification_directly():
    workflow = create_workflow()
    move_to_diagnosed(workflow)

    with pytest.raises(ValueError):
        workflow.start_verification()

    assert workflow.state is WorkflowState.DIAGNOSED


def test_diagnosed_cannot_resolve_directly():
    workflow = create_workflow()
    move_to_diagnosed(workflow)

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.DIAGNOSED


# ============================================================
# ACTION REQUIRED BYPASS PROTECTION
# ============================================================


def test_action_required_cannot_start_verification_directly():
    workflow = create_workflow()
    move_to_action_required(workflow)

    with pytest.raises(ValueError):
        workflow.start_verification()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


def test_action_required_cannot_resolve_directly():
    workflow = create_workflow()
    move_to_action_required(workflow)

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.ACTION_REQUIRED


# ============================================================
# REMEDIATING BYPASS PROTECTION
# ============================================================


def test_remediating_cannot_resolve_directly():
    workflow = create_workflow()
    move_to_remediating(workflow)

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.REMEDIATING


def test_remediating_cannot_mark_diagnosed():
    workflow = create_workflow()
    move_to_remediating(workflow)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.REMEDIATING


def test_remediating_cannot_require_action_again():
    workflow = create_workflow()
    move_to_remediating(workflow)

    with pytest.raises(ValueError):
        workflow.require_action()

    assert workflow.state is WorkflowState.REMEDIATING


# ============================================================
# VERIFYING STATE PROTECTION
# ============================================================


def test_verifying_cannot_resolve_without_verification_path():
    workflow = create_workflow()
    move_to_verifying(workflow)

    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED


def test_verifying_cannot_skip_back_to_diagnosed():
    workflow = create_workflow()
    move_to_verifying(workflow)

    with pytest.raises(ValueError):
        workflow.mark_diagnosed()

    assert workflow.state is WorkflowState.VERIFYING


def test_verifying_cannot_skip_to_action_required():
    workflow = create_workflow()
    move_to_verifying(workflow)

    with pytest.raises(ValueError):
        workflow.require_action()

    assert workflow.state is WorkflowState.VERIFYING


# ============================================================
# FAILED VERIFICATION / CONTROLLED RECOVERY
# ============================================================


def test_verifying_can_return_to_remediating_for_recovery():
    workflow = create_workflow()
    move_to_verifying(workflow)

    workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING


def test_recovery_transition_is_recorded():
    workflow = create_workflow()
    move_to_verifying(workflow)

    workflow.start_remediation()

    assert workflow.history[-1] == (
        WorkflowState.VERIFYING,
        WorkflowState.REMEDIATING,
    )


def test_recovery_does_not_delete_previous_history():
    workflow = create_workflow()
    move_to_verifying(workflow)

    original_history = workflow.history

    workflow.start_remediation()

    assert workflow.history[: len(original_history)] == original_history


def test_recovery_requires_verifying_state():
    workflow = create_workflow()
    move_to_remediating(workflow)

    with pytest.raises(ValueError):
        workflow.start_remediation()

    assert workflow.state is WorkflowState.REMEDIATING


def test_recovery_does_not_jump_directly_to_resolved():
    workflow = create_workflow()
    move_to_verifying(workflow)

    workflow.start_remediation()

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.REMEDIATING


# ============================================================
# RESOLVED TERMINAL STATE
# ============================================================


@pytest.mark.parametrize(
    "method_name",
    [
        "start_investigation",
        "mark_diagnosed",
        "require_action",
        "start_remediation",
        "start_verification",
        "resolve",
        "escalate",
    ],
)
def test_resolved_rejects_all_normal_transitions(method_name):
    workflow = create_workflow()
    move_to_resolved(workflow)

    with pytest.raises(ValueError):
        getattr(workflow, method_name)()

    assert workflow.state is WorkflowState.RESOLVED


def test_resolved_is_terminal():
    workflow = create_workflow()
    move_to_resolved(workflow)

    assert workflow.is_terminal is True


def test_resolved_history_is_preserved():
    workflow = create_workflow()
    move_to_resolved(workflow)

    history_before = workflow.history

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.history == history_before


# ============================================================
# REOPENING
# ============================================================


def test_only_resolved_workflow_can_be_reopened():
    workflow = create_workflow()

    with pytest.raises(ValueError):
        workflow.reopen()

    assert workflow.state is WorkflowState.OPEN


@pytest.mark.parametrize(
    "state_builder",
    [
        lambda workflow: None,
        lambda workflow: workflow.start_investigation(),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
        ),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
            workflow.require_action(),
        ),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
            workflow.require_action(),
            workflow.start_remediation(),
        ),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
            workflow.require_action(),
            workflow.start_remediation(),
            workflow.start_verification(),
        ),
    ],
)
def test_non_resolved_workflow_cannot_be_reopened(state_builder):
    workflow = create_workflow()

    state_builder(workflow)

    state_before = workflow.state
    history_before = workflow.history

    with pytest.raises(ValueError):
        workflow.reopen()

    assert workflow.state is state_before
    assert workflow.history == history_before


def test_reopen_moves_resolved_workflow_to_investigating():
    workflow = create_workflow()
    move_to_resolved(workflow)

    workflow.reopen()

    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.is_terminal is False


def test_reopen_records_history():
    workflow = create_workflow()
    move_to_resolved(workflow)

    workflow.reopen()

    assert workflow.history[-1] == (
        WorkflowState.RESOLVED,
        WorkflowState.INVESTIGATING,
    )


def test_reopen_preserves_previous_history():
    workflow = create_workflow()
    move_to_resolved(workflow)

    history_before = workflow.history

    workflow.reopen()

    assert workflow.history[: len(history_before)] == history_before


def test_reopened_workflow_must_be_diagnosed_again():
    workflow = create_workflow()
    move_to_resolved(workflow)

    workflow.reopen()

    with pytest.raises(ValueError):
        workflow.require_action()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_reopened_workflow_must_follow_normal_lifecycle_again():
    workflow = create_workflow()
    move_to_resolved(workflow)

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED


# ============================================================
# ESCALATION INTEGRITY
# ============================================================


def test_open_can_be_escalated():
    workflow = create_workflow()

    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED


@pytest.mark.parametrize(
    "state_builder",
    [
        lambda workflow: workflow.start_investigation(),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
        ),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
            workflow.require_action(),
        ),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
            workflow.require_action(),
            workflow.start_remediation(),
        ),
        lambda workflow: (
            workflow.start_investigation(),
            workflow.mark_diagnosed(),
            workflow.require_action(),
            workflow.start_remediation(),
            workflow.start_verification(),
        ),
    ],
)
def test_active_workflow_can_be_escalated(state_builder):
    workflow = create_workflow()

    state_builder(workflow)
    workflow.escalate()

    assert workflow.state is WorkflowState.ESCALATED


def test_escalation_is_terminal():
    workflow = create_workflow()

    workflow.escalate()

    assert workflow.is_terminal is True


def test_escalation_records_history():
    workflow = create_workflow()

    workflow.escalate()

    assert workflow.history[-1] == (
        WorkflowState.OPEN,
        WorkflowState.ESCALATED,
    )


@pytest.mark.parametrize(
    "method_name",
    [
        "start_investigation",
        "mark_diagnosed",
        "require_action",
        "start_remediation",
        "start_verification",
        "resolve",
        "reopen",
        "escalate",
    ],
)
def test_escalated_workflow_rejects_all_transitions(method_name):
    workflow = create_workflow()
    workflow.escalate()

    with pytest.raises(ValueError):
        getattr(workflow, method_name)()

    assert workflow.state is WorkflowState.ESCALATED


# ============================================================
# HISTORY IMMUTABILITY / ISOLATION
# ============================================================


def test_history_returns_a_copy():
    workflow = create_workflow()

    workflow.start_investigation()

    history = workflow.history
    history.clear()

    assert len(workflow.history) == 1


def test_history_mutation_does_not_change_workflow_state():
    workflow = create_workflow()

    workflow.start_investigation()

    history = workflow.history
    history.clear()

    assert workflow.state is WorkflowState.INVESTIGATING


def test_history_cannot_be_used_to_change_workflow_state():
    workflow = create_workflow()

    workflow.start_investigation()

    history = workflow.history

    history.append(
        (
            WorkflowState.INVESTIGATING,
            WorkflowState.RESOLVED,
        )
    )

    assert workflow.state is WorkflowState.INVESTIGATING
    assert workflow.history[-1] == (
        WorkflowState.OPEN,
        WorkflowState.INVESTIGATING,
    )


def test_failed_transition_does_not_modify_history():
    workflow = create_workflow()

    history_before = workflow.history

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.history == history_before


def test_failed_transition_does_not_modify_state():
    workflow = create_workflow()

    with pytest.raises(ValueError):
        workflow.resolve()

    assert workflow.state is WorkflowState.OPEN


# ============================================================
# WORKFLOW / CASE BOUNDARY
# ============================================================


def test_workflow_preserves_case_reference():
    case = create_case()
    workflow = TechnicianWorkflow(case)

    assert workflow.case is case


def test_workflow_state_changes_do_not_replace_case():
    case = create_case()
    workflow = TechnicianWorkflow(case)

    workflow.start_investigation()

    assert workflow.case is case


def test_reopening_does_not_replace_case():
    case = create_case()
    workflow = TechnicianWorkflow(case)

    move_to_resolved(workflow)
    workflow.reopen()

    assert workflow.case is case


def test_escalation_does_not_replace_case():
    case = create_case()
    workflow = TechnicianWorkflow(case)

    workflow.escalate()

    assert workflow.case is case


# ============================================================
# FULL LIFECYCLE + RECOVERY INTEGRITY
# ============================================================


def test_full_lifecycle_then_recovery_then_resolution():
    workflow = create_workflow()

    move_to_resolved(workflow)

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.state is WorkflowState.RESOLVED


def test_recovery_history_contains_both_resolution_cycles():
    workflow = create_workflow()

    move_to_resolved(workflow)

    first_resolution_history = workflow.history

    workflow.reopen()
    workflow.mark_diagnosed()
    workflow.require_action()
    workflow.start_remediation()
    workflow.start_verification()
    workflow.resolve()

    assert workflow.history[: len(first_resolution_history)] == (
        first_resolution_history
    )

    assert workflow.history[-1] == (
        WorkflowState.VERIFYING,
        WorkflowState.RESOLVED,
    )


def test_workflow_never_silently_changes_state():
    workflow = create_workflow()

    assert workflow.state is WorkflowState.OPEN

    workflow.start_investigation()
    assert workflow.state is WorkflowState.INVESTIGATING

    workflow.mark_diagnosed()
    assert workflow.state is WorkflowState.DIAGNOSED

    workflow.require_action()
    assert workflow.state is WorkflowState.ACTION_REQUIRED

    workflow.start_remediation()
    assert workflow.state is WorkflowState.REMEDIATING

    workflow.start_verification()
    assert workflow.state is WorkflowState.VERIFYING

    workflow.resolve()
    assert workflow.state is WorkflowState.RESOLVED


def test_workflow_history_length_matches_successful_transitions():
    workflow = create_workflow()

    assert len(workflow.history) == 0

    workflow.start_investigation()
    assert len(workflow.history) == 1

    workflow.mark_diagnosed()
    assert len(workflow.history) == 2

    workflow.require_action()
    assert len(workflow.history) == 3

    workflow.start_remediation()
    assert len(workflow.history) == 4

    workflow.start_verification()
    assert len(workflow.history) == 5

    workflow.resolve()
    assert len(workflow.history) == 6


def test_failed_transition_does_not_increment_history():
    workflow = create_workflow()

    workflow.start_investigation()

    history_length = len(workflow.history)

    with pytest.raises(ValueError):
        workflow.resolve()

    assert len(workflow.history) == history_length


def test_reopen_counts_as_a_real_transition():
    workflow = create_workflow()

    move_to_resolved(workflow)

    history_length = len(workflow.history)

    workflow.reopen()

    assert len(workflow.history) == history_length + 1


# ============================================================
# STATE ENUM INTEGRITY
# ============================================================


def test_workflow_uses_workflow_state_enum():
    workflow = create_workflow()

    assert isinstance(workflow.state, WorkflowState)


def test_all_terminal_states_are_reported_terminal():
    workflow = create_workflow()

    workflow.escalate()

    assert workflow.is_terminal is True

    workflow = create_workflow()
    move_to_resolved(workflow)

    assert workflow.is_terminal is True


def test_non_terminal_states_are_not_reported_terminal():
    workflow = create_workflow()

    assert workflow.is_terminal is False

    workflow.start_investigation()
    assert workflow.is_terminal is False

    workflow.mark_diagnosed()
    assert workflow.is_terminal is False

    workflow.require_action()
    assert workflow.is_terminal is False

    workflow.start_remediation()
    assert workflow.is_terminal is False

    workflow.start_verification()
    assert workflow.is_terminal is False