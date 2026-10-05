from engine.case_timeline import CaseTimeline
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


def create_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return case, workflow


def test_timeline_requires_workflow():
    try:
        CaseTimeline(None)
    except ValueError:
        return

    raise AssertionError("CaseTimeline should reject None workflow.")


def test_timeline_requires_technician_workflow():
    try:
        CaseTimeline(object())
    except ValueError:
        return

    raise AssertionError(
        "CaseTimeline should require a TechnicianWorkflow."
    )


def test_timeline_exposes_case():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.case is case


def test_timeline_exposes_case_id():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.case_id == case.case_id


def test_timeline_exposes_machine_id():
    case, workflow = create_workflow()

    case.machine_id = "machine-001"

    timeline = CaseTimeline(workflow)

    assert timeline.machine_id == "machine-001"


def test_timeline_exposes_hostname():
    case, workflow = create_workflow()

    case.hostname = "PC-001"

    timeline = CaseTimeline(workflow)

    assert timeline.hostname == "PC-001"


def test_timeline_exposes_workflow_history():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.history == workflow.history


def test_timeline_does_not_create_a_separate_history():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    workflow.start_investigation()

    assert timeline.history == workflow.history


def test_timeline_reflects_initial_workflow_history():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.history == workflow.history


def test_timeline_reflects_workflow_changes():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    workflow.start_investigation()

    assert timeline.history == workflow.history
    assert len(timeline.history) == len(workflow.history)


def test_timeline_preserves_history_order():
    case, workflow = create_workflow()

    workflow.start_investigation()

    timeline = CaseTimeline(workflow)

    assert timeline.history == workflow.history
    assert len(timeline.history) >= 1


def test_timeline_exposes_current_state():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.state == workflow.state


def test_timeline_reflects_current_state_changes():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    workflow.start_investigation()

    assert timeline.state == workflow.state


def test_timeline_is_terminal_matches_workflow():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.is_terminal == workflow.is_terminal


def test_timeline_does_not_create_workflow():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.workflow is workflow


def test_timeline_does_not_execute_remediation():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert not hasattr(timeline, "execute")
    assert not hasattr(timeline, "authorize")


def test_timeline_preserves_workflow_identity():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.workflow is workflow


def test_timeline_history_updates_after_transition():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    workflow.start_investigation()

    assert timeline.history == workflow.history
    assert len(timeline.history) >= 1


def test_timeline_has_no_duplicate_case_history():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    if hasattr(case, "history"):
        assert timeline.history == workflow.history


def test_timeline_is_read_oriented():
    case, workflow = create_workflow()

    timeline = CaseTimeline(workflow)

    assert timeline.workflow is workflow
    assert timeline.case is case
    assert timeline.history == workflow.history