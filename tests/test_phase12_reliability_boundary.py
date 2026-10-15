from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


def make_workflow():
    case = DiagnosticCase()
    return TechnicianWorkflow(case)


def test_reliability_boundary_requires_canonical_workflow():
    from engine.reliability_boundary import ReliabilityBoundary

    workflow = make_workflow()
    boundary = ReliabilityBoundary(workflow)

    assert boundary.workflow is workflow


def test_reliability_boundary_rejects_missing_workflow():
    import pytest
    from engine.reliability_boundary import ReliabilityBoundary

    with pytest.raises((TypeError, ValueError)):
        ReliabilityBoundary(None)


def test_reliability_boundary_does_not_replace_workflow():
    from engine.reliability_boundary import ReliabilityBoundary

    workflow = make_workflow()
    boundary = ReliabilityBoundary(workflow)

    assert boundary.workflow is workflow
    assert hasattr(workflow, "reopen")
    assert hasattr(workflow, "resolve")


def test_reliability_boundary_exposes_no_remediation_executor():
    from engine.reliability_boundary import ReliabilityBoundary

    boundary = ReliabilityBoundary(make_workflow())

    assert not hasattr(boundary, "execute_remediation")
    assert not hasattr(boundary, "authorize_remediation")


def test_reliability_boundary_rejects_unrelated_objects():
    import pytest
    from engine.reliability_boundary import ReliabilityBoundary

    with pytest.raises((TypeError, ValueError)):
        ReliabilityBoundary(object())
