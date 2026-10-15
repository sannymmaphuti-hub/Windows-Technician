from engine.diagnostic_case import DiagnosticCase
from engine.system_wide_intelligence_integration import (
    SystemWideIntelligenceIntegration,
)


def test_investigation_is_not_run_during_construction():
    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(case)

    assert integration.investigation_result() is None


def test_investigate_uses_canonical_investigation_engine():
    class Investigation:
        def __init__(self):
            self.received = None

        def investigate(self, system_data=None):
            self.received = system_data
            return {"status": "INVESTIGATED"}

    case = DiagnosticCase()
    investigation = Investigation()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=investigation,
    )

    system_data = {
        "cpu": {"usage": 87},
        "memory": {"usage": 91},
    }

    result = integration.investigate(system_data)

    assert result == {"status": "INVESTIGATED"}
    assert investigation.received == system_data


def test_investigation_result_is_defensive():
    class Investigation:
        def investigate(self, system_data=None):
            return {"findings": ["memory_pressure"]}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
    )

    result = integration.investigate()

    result["findings"].append("tampered")

    assert integration.investigation_result() == {
        "findings": ["memory_pressure"]
    }


def test_investigation_result_is_available_in_intelligence_projection():
    class Investigation:
        def investigate(self, system_data=None):
            return {
                "status": "INVESTIGATED",
                "scope": "SYSTEM",
            }

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
    )

    integration.investigate()

    projection = integration.intelligence_projection()

    assert projection["investigation"] == {
        "status": "INVESTIGATED",
        "scope": "SYSTEM",
    }


def test_latest_investigation_replaces_previous_result():
    class Investigation:
        def investigate(self, system_data=None):
            return {"value": system_data}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
    )

    integration.investigate({"run": 1})
    integration.investigate({"run": 2})

    assert integration.investigation_result() == {
        "value": {"run": 2}
    }


def test_investigation_does_not_replace_canonical_case():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
    )

    integration.investigate()

    assert integration.case is case
    assert integration.case.case_id == case.case_id


def test_projection_preserves_existing_case_surface_after_investigation():
    class Investigation:
        def investigate(self, system_data=None):
            return {"status": "INVESTIGATED"}

    case = DiagnosticCase()

    integration = SystemWideIntelligenceIntegration(
        case,
        investigation=Investigation(),
    )

    integration.investigate()

    projection = integration.projection()

    assert set(projection) == {
        "case",
        "intelligence",
    }

    assert projection["case"]["case_id"] == case.case_id
    assert projection["intelligence"]["investigation"] == {
        "status": "INVESTIGATED"
    }
