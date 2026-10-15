import pytest

from ui.dashboard_information_model import DashboardFinding
from ui.operation_progress_presentation import OperationProgress
from ui.production_ux_projection import ProductionUXProjection


def build_workspace(**overrides):
    values = {
        "system_name": "Test workstation",
        "health_status": "WARNING",
        "dashboard_findings": [
            DashboardFinding(
                title="Memory pressure",
                severity="WARNING",
                explanation="Memory usage is elevated.",
                requires_attention=True,
            )
        ],
        "case_projection": {
            "case_id": "case-100",
            "status": "OPEN",
            "state": "INVESTIGATING",
            "findings": [{"title": "Memory pressure"}],
            "recommendations": ["Review memory-intensive applications"],
        },
        "health_findings": [
            {"title": "Memory pressure", "severity": "WARNING"}
        ],
    }
    values.update(overrides)
    return ProductionUXProjection().build(**values)


def test_workspace_composes_dashboard_case_health_and_accessibility():
    result = build_workspace()

    assert result["dashboard"]["system"]["name"] == "Test workstation"
    assert result["diagnostic_case"]["identity"]["case_id"] == "case-100"
    assert result["system_health"]["highest_severity"] == "warning"
    assert result["accessibility"]["keyboard_navigation"] is True
    assert result["layout"]["layout_mode"] == "WIDE"


def test_workspace_integrates_progress_and_remediation_prompt():
    result = build_workspace(
        operation_progress=OperationProgress(
            operation_id="op-100",
            status="RUNNING",
            message="Collecting system information",
            percentage=40,
        ),
        remediation_action={
            "action_id": "fix-100",
            "title": "Review startup applications",
            "explanation": "Several applications start automatically.",
            "authorization_status": "UNAUTHORIZED",
        },
    )

    assert result["operation_progress"]["percentage"] == 40
    assert result["remediation_prompt"]["authorization_status"] == "UNAUTHORIZED"
    assert result["remediation_prompt"]["execution_status"] == "NOT_EXECUTED"


def test_workspace_integrates_error_empty_and_recovery_states():
    result = build_workspace(
        error={
            "error_code": "CONNECTION_LOST",
            "detail": "Remote machine disconnected.",
        },
        empty_code="NO_HISTORY",
        recovery={
            "recovery_status": "REQUIRES_AUTHORIZATION",
            "detail": "A technician must review the recovery plan.",
        },
    )

    assert result["error_state"]["code"] == "CONNECTION_LOST"
    assert result["empty_state"]["items_available"] is False
    assert result["recovery_state"]["requires_authorization"] is True


def test_workspace_supports_compact_layout():
    result = build_workspace(viewport_width=600)

    assert result["layout"]["layout_mode"] == "COMPACT"
    assert result["layout"]["content_columns"] == 1


def test_workspace_preserves_operation_safety_boundaries():
    result = build_workspace(
        operation_progress=OperationProgress(
            operation_id="op-101",
            status="RUNNING",
            message="Working",
            percentage=10,
        ),
        remediation_action={
            "title": "Restart a service",
            "explanation": "The service may be unresponsive.",
            "authorization_status": "AUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        },
    )

    assert result["diagnostics_executed"] is False
    assert result["remediation_executed"] is False
    assert result["remediation_prompt"]["execution_status"] == "NOT_EXECUTED"


def test_workspace_rejects_invalid_component_input():
    with pytest.raises(TypeError):
        build_workspace(case_projection=None)


def test_workspace_projection_is_detached():
    result = build_workspace()

    result["diagnostic_case"]["findings"][0]["title"] = "Changed presentation"
    result["dashboard"]["system"]["name"] = "Changed name"

    assert result["diagnostic_case"]["findings"][0]["title"] == (
        "Changed presentation"
    )
    assert result["dashboard"]["system"]["name"] == "Changed name"


def test_workspace_does_not_claim_to_execute_work():
    result = build_workspace()

    assert result["diagnostics_executed"] is False
    assert result["remediation_executed"] is False
