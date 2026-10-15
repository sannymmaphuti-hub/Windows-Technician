from engine.diagnostic_case import DiagnosticCase
from engine.machine_overview import MachineOverview
from engine.managed_machine import ManagedMachine
from engine.proactive_alert import ProactiveAlert


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="TEST-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_case(machine_id="machine-001", hostname="TEST-PC", state="OPEN"):
    case = DiagnosticCase()
    case.machine_id = machine_id
    case.hostname = hostname
    case.lifecycle_state = state
    return case


def test_machine_overview_exposes_canonical_machine_identity():
    overview = MachineOverview(build_machine())

    assert overview.machine_id == "machine-001"
    assert overview.hostname == "TEST-PC"


def test_machine_overview_exposes_machine_state():
    overview = MachineOverview(build_machine())

    assert overview.platform == overview.machine.platform
    assert overview.operating_system == overview.machine.operating_system
    assert overview.connection_state == overview.machine.connection_state
    assert overview.health_state == overview.machine.health_state
    assert overview.last_seen == overview.machine.last_seen


def test_machine_overview_rejects_alert_for_different_machine():
    overview = MachineOverview(build_machine())

    other_machine = ManagedMachine(
        machine_id="machine-999",
        hostname="OTHER-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    alert = ProactiveAlert(
        machine=other_machine,
        alert_type="CPU",
        metric="usage",
        message="CPU usage is elevated.",
    )

    try:
        overview.add_alert(alert)
    except ValueError as exc:
        assert "different machine" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_machine_overview_rejects_case_for_different_machine():
    overview = MachineOverview(build_machine())

    case = build_case(
        machine_id="machine-999",
        hostname="OTHER-PC",
    )

    try:
        overview.add_case(case)
    except ValueError as exc:
        assert "different machine" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_machine_overview_projects_active_cases():
    overview = MachineOverview(build_machine())

    active = build_case(state="INVESTIGATING")
    resolved = build_case(state="RESOLVED")

    overview.add_case(active)
    overview.add_case(resolved)

    cases = overview.active_cases()

    assert len(cases) == 1
    assert cases[0]["case_id"] == active.case_id
    assert cases[0]["lifecycle_state"] == "INVESTIGATING"


def test_machine_overview_projects_unresolved_problems():
    overview = MachineOverview(build_machine())

    open_case = build_case(state="OPEN")
    closed_case = build_case(state="CLOSED")

    overview.add_case(open_case)
    overview.add_case(closed_case)

    problems = overview.unresolved_problems()

    assert len(problems) == 1
    assert problems[0]["case_id"] == open_case.case_id


def test_machine_overview_aggregates_case_evidence():
    overview = MachineOverview(build_machine())

    case_one = build_case()
    case_two = build_case()

    case_one.findings.append({"finding": "memory pressure"})
    case_two.findings.append({"finding": "disk pressure"})

    case_one.root_causes.append({"cause": "high memory usage"})
    case_two.root_causes.append({"cause": "low disk space"})

    case_one.recommendations.append({"action": "review memory"})
    case_two.recommendations.append({"action": "review storage"})

    overview.add_case(case_one)
    overview.add_case(case_two)

    assert len(overview.findings()) == 2
    assert len(overview.root_causes()) == 2
    assert len(overview.recommendations()) == 2


def test_machine_workspace_projection_has_complete_surface():
    overview = MachineOverview(build_machine())

    projection = overview.workspace_projection()

    assert set(projection) == {
    "machine",
    "alerts",
    "active_cases",
    "unresolved_problems",
    "findings",
    "root_causes",
    "recommendations",
    "remediation_status",
    "verification_status",
    "escalation_status",
    "decisions",
}

    assert projection["machine"]["machine_id"] == "machine-001"
    assert projection["machine"]["hostname"] == "TEST-PC"


def test_machine_workspace_projection_is_defensive():
    overview = MachineOverview(build_machine())

    case = build_case()
    case.findings.append({"finding": "memory pressure"})
    overview.add_case(case)

    projection = overview.workspace_projection()
    projection["machine"]["hostname"] = "CORRUPTED"
    projection["findings"][0]["finding"] = "CORRUPTED"

    fresh = overview.workspace_projection()

    assert fresh["machine"]["hostname"] == "TEST-PC"
    assert fresh["findings"][0]["finding"] == "memory pressure"


def test_machine_overview_remains_presentation_only():
    forbidden = {
        "diagnose",
        "analyze",
        "reason",
        "generate_recommendations",
        "authorize",
        "execute",
        "remediate",
        "verify",
    }

    public_methods = {
        name
        for name in dir(MachineOverview)
        if not name.startswith("_")
    }

    assert forbidden.isdisjoint(public_methods)


def build_workflow(case):
    from engine.technician_workflow import TechnicianWorkflow
    return TechnicianWorkflow(case)


def test_machine_overview_accepts_case_summary_for_same_machine():
    from engine.technician_case_summary import TechnicianCaseSummary

    overview = MachineOverview(build_machine())
    case = build_case()
    workflow = build_workflow(case)
    summary = TechnicianCaseSummary(workflow)

    overview.add_case_summary(summary)

    assert overview.case_summary_count == 1


def test_machine_overview_rejects_case_summary_for_different_machine():
    from engine.technician_case_summary import TechnicianCaseSummary

    overview = MachineOverview(build_machine())

    other_case = build_case(
        machine_id="machine-999",
        hostname="OTHER-PC",
    )
    workflow = build_workflow(other_case)
    summary = TechnicianCaseSummary(workflow)

    try:
        overview.add_case_summary(summary)
    except ValueError as exc:
        assert "different machine" in str(exc)
    else:
        raise AssertionError("Expected ValueError.")


def test_machine_overview_projects_case_summary_operational_status():
    from engine.technician_case_summary import TechnicianCaseSummary

    overview = MachineOverview(build_machine())

    case = build_case()
    workflow = build_workflow(case)
    summary = TechnicianCaseSummary(workflow)

    summary.set_remediation_status("AUTHORIZED")
    summary.set_verification_status("PENDING")
    summary.set_escalation_status("NOT_ESCALATED")
    summary.set_decision("REMEDIATE")

    overview.add_case_summary(summary)

    assert overview.remediation_status() == [
        {
            "case_id": summary.case_id,
            "status": "AUTHORIZED",
        }
    ]

    assert overview.verification_status() == [
        {
            "case_id": summary.case_id,
            "status": "PENDING",
        }
    ]

    assert overview.escalation_status() == [
        {
            "case_id": summary.case_id,
            "status": "NOT_ESCALATED",
        }
    ]

    assert overview.decisions() == [
        {
            "case_id": summary.case_id,
            "decision": "REMEDIATE",
        }
    ]


def test_machine_workspace_projection_contains_operational_surfaces():
    from engine.technician_case_summary import TechnicianCaseSummary

    overview = MachineOverview(build_machine())

    case = build_case()
    workflow = build_workflow(case)
    summary = TechnicianCaseSummary(workflow)

    summary.set_remediation_status("EXECUTED")
    summary.set_verification_status("VERIFIED")

    overview.add_case(case)
    overview.add_case_summary(summary)

    projection = overview.workspace_projection()

    assert projection["remediation_status"][0]["status"] == "EXECUTED"
    assert projection["verification_status"][0]["status"] == "VERIFIED"
    assert projection["remediation_status"][0]["case_id"] == case.case_id


def test_machine_workspace_operational_projection_is_defensive():
    from engine.technician_case_summary import TechnicianCaseSummary

    overview = MachineOverview(build_machine())

    case = build_case()
    workflow = build_workflow(case)
    summary = TechnicianCaseSummary(workflow)

    decision = {
        "action": "review",
        "authorized": False,
    }

    summary.set_decision(decision)
    overview.add_case_summary(summary)

    projection = overview.workspace_projection()
    projection["decisions"][0]["decision"]["authorized"] = True

    fresh = overview.workspace_projection()

    assert fresh["decisions"][0]["decision"]["authorized"] is False
