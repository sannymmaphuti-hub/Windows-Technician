from engine.case_handoff import CaseHandoff
from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


def create_case_and_workflow():
    case = DiagnosticCase()
    workflow = TechnicianWorkflow(case)
    return case, workflow


def test_handoff_requires_workflow():
    try:
        CaseHandoff(None, "technician-002", "Needs further investigation.")
    except ValueError:
        return

    raise AssertionError(
        "CaseHandoff should reject None workflow."
    )


def test_handoff_requires_technician_workflow():
    try:
        CaseHandoff(
            object(),
            "technician-002",
            "Needs further investigation.",
        )
    except ValueError:
        return

    raise AssertionError(
        "CaseHandoff should require a TechnicianWorkflow."
    )


def test_handoff_requires_recipient():
    _, workflow = create_case_and_workflow()

    try:
        CaseHandoff(
            workflow,
            None,
            "Needs further investigation.",
        )
    except ValueError:
        return

    raise AssertionError(
        "CaseHandoff should require a recipient."
    )


def test_handoff_requires_reason():
    _, workflow = create_case_and_workflow()

    try:
        CaseHandoff(
            workflow,
            "technician-002",
            None,
        )
    except ValueError:
        return

    raise AssertionError(
        "CaseHandoff should require a reason."
    )


def test_handoff_exposes_workflow():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.workflow is workflow


def test_handoff_exposes_case():
    case, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.case is case


def test_handoff_exposes_case_id():
    case, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.case_id == case.case_id


def test_handoff_exposes_machine_id():
    case, workflow = create_case_and_workflow()

    case.machine_id = "machine-001"

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.machine_id == "machine-001"


def test_handoff_exposes_hostname():
    case, workflow = create_case_and_workflow()

    case.hostname = "PC-001"

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.hostname == "PC-001"


def test_handoff_exposes_recipient():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.recipient == "technician-002"


def test_handoff_exposes_reason():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.reason == "Needs further investigation."


def test_handoff_starts_pending():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert handoff.status == "PENDING"


def test_handoff_can_be_accepted():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    handoff.accept()

    assert handoff.status == "ACCEPTED"


def test_handoff_can_be_declined():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    handoff.decline()

    assert handoff.status == "DECLINED"


def test_accepted_handoff_cannot_be_declined():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    handoff.accept()
    handoff.decline()

    assert handoff.status == "ACCEPTED"


def test_declined_handoff_cannot_be_accepted():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    handoff.decline()
    handoff.accept()

    assert handoff.status == "DECLINED"


def test_handoff_does_not_change_workflow_state():
    _, workflow = create_case_and_workflow()

    original_state = workflow.state

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    handoff.accept()

    assert workflow.state == original_state


def test_handoff_does_not_change_case_state():
    case, workflow = create_case_and_workflow()

    original_state = case.lifecycle_state

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    handoff.accept()

    assert case.lifecycle_state == original_state


def test_handoff_does_not_authorize_remediation():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert not hasattr(handoff, "authorize")


def test_handoff_does_not_execute_remediation():
    _, workflow = create_case_and_workflow()

    handoff = CaseHandoff(
        workflow,
        "technician-002",
        "Needs further investigation.",
    )

    assert not hasattr(handoff, "execute")