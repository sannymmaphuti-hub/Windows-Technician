import pytest

from PySide6.QtWidgets import QApplication, QPushButton

from engine.accessibility import AccessibilityHelper
from engine.application_state import ApplicationState
from engine.dashboard_view_model import DashboardViewModel
from engine.dashboard_widget import DashboardWidget
from engine.diagnostic_card_model import DiagnosticCardModel
from engine.diagnostic_card_widget import DiagnosticCardWidget
from engine.remediation_confirmation_dialog import (
    RemediationConfirmationDialog,
)
from engine.remediation_presentation_model import (
    RemediationPresentationModel,
)
from engine.remediation_action_card_widget import (
    RemediationActionCardWidget,
)


@pytest.fixture
def qapp():
    application = QApplication.instance()

    if application is None:
        application = QApplication([])

    return application


def make_model():
    return RemediationPresentationModel(
        {
            "action_id": "A-001",
            "action_type": "memory_review",
            "title": "Review memory usage",
            "explanation": "Memory pressure should be reviewed.",
            "risk": "LOW",
            "authorization_status": "UNAUTHORIZED",
            "execution_status": "NOT_EXECUTED",
        }
    )


def test_dynamic_description_requires_widget():
    with pytest.raises(ValueError):
        AccessibilityHelper.set_dynamic_description(
            None,
            "state",
        )


def test_dynamic_description_requires_description(qapp):
    button = QPushButton()

    with pytest.raises(ValueError):
        AccessibilityHelper.set_dynamic_description(
            button,
            None,
        )


def test_dynamic_description_updates_accessible_description(qapp):
    button = QPushButton()

    AccessibilityHelper.describe(
        button,
        "Action",
        "Initial state.",
    )

    AccessibilityHelper.set_dynamic_description(
        button,
        "Updated state.",
    )

    assert button.accessibleName() == "Action"
    assert button.accessibleDescription() == "Updated state."


def test_set_state_requires_widget():
    with pytest.raises(ValueError):
        AccessibilityHelper.set_state(
            None,
            "State",
            "Description",
        )


def test_set_state_requires_name(qapp):
    button = QPushButton()

    with pytest.raises(ValueError):
        AccessibilityHelper.set_state(
            button,
            "",
            "Description",
        )


def test_set_state_requires_description(qapp):
    button = QPushButton()

    with pytest.raises(ValueError):
        AccessibilityHelper.set_state(
            button,
            "State",
            None,
        )


def test_set_state_updates_name_and_description(qapp):
    button = QPushButton()

    AccessibilityHelper.set_state(
        button,
        "System health",
        "System health is warning with a score of 74.",
    )

    assert button.accessibleName() == "System health"
    assert (
        button.accessibleDescription()
        == "System health is warning with a score of 74."
    )


def test_dashboard_health_has_dynamic_accessible_state(qapp):
    state = ApplicationState()

    view_model = DashboardViewModel(
        state,
        {
            "health": {
                "status": "WARNING",
                "score": 74,
            },
            "system_findings": [],
            "relationships": [],
            "root_causes": [],
            "recommendations": [],
        },
    )

    dashboard = DashboardWidget(view_model)

    assert dashboard.health_status_label.accessibleName()
    assert dashboard.health_status_label.accessibleDescription()


def test_dashboard_health_accessible_state_contains_status(qapp):
    state = ApplicationState()

    view_model = DashboardViewModel(
        state,
        {
            "health": {
                "status": "WARNING",
                "score": 74,
            },
        },
    )

    dashboard = DashboardWidget(view_model)

    description = (
        dashboard.health_status_label.accessibleDescription()
    )

    assert "WARNING" in description
    assert "74" in description


def test_dashboard_health_accessible_state_updates_after_refresh(qapp):
    state = ApplicationState()

    view_model = DashboardViewModel(
        state,
        {
            "health": {
                "status": "NORMAL",
                "score": 92,
            },
        },
    )

    dashboard = DashboardWidget(view_model)

    view_model.update_intelligence(
        {
            "health": {
                "status": "CRITICAL",
                "score": 31,
            },
        }
    )

    dashboard.refresh()

    description = (
        dashboard.health_status_label.accessibleDescription()
    )

    assert "CRITICAL" in description
    assert "31" in description


def test_dashboard_counts_have_accessible_descriptions(qapp):
    state = ApplicationState()

    view_model = DashboardViewModel(
        state,
        {
            "health": {
                "status": "NORMAL",
                "score": 95,
            },
            "system_findings": [
                {"title": "Finding one"},
                {"title": "Finding two"},
            ],
            "relationships": [
                {"source": "A", "target": "B"},
            ],
            "root_causes": [
                {"cause": "Memory pressure"},
            ],
            "recommendations": [
                {"action": "Review memory"},
            ],
        },
    )

    dashboard = DashboardWidget(view_model)

    assert (
        dashboard.findings_label.accessibleDescription()
    )
    assert (
        dashboard.relationships_label.accessibleDescription()
    )
    assert (
        dashboard.root_causes_label.accessibleDescription()
    )
    assert (
        dashboard.recommendations_label.accessibleDescription()
    )


def test_diagnostic_card_exposes_dynamic_finding_state(qapp):
    model = DiagnosticCardModel(
        {
            "finding_id": "F-001",
            "severity": "HIGH",
            "category": "MEMORY",
            "title": "High memory usage",
            "explanation": "Memory pressure detected.",
            "evidence": [
                {"usage": "88%"},
            ],
            "next_step": "Review memory usage.",
        }
    )

    card = DiagnosticCardWidget(model)

    assert card.accessibleName()
    assert card.accessibleDescription()


def test_diagnostic_card_accessible_description_contains_severity(qapp):
    model = DiagnosticCardModel(
        {
            "severity": "CRITICAL",
            "category": "SYSTEM",
            "title": "Critical finding",
            "explanation": "Immediate attention is required.",
        }
    )

    card = DiagnosticCardWidget(model)

    assert "CRITICAL" in card.accessibleDescription()


def test_diagnostic_card_accessible_description_contains_title(qapp):
    model = DiagnosticCardModel(
        {
            "severity": "HIGH",
            "title": "High memory usage",
            "explanation": "Memory pressure detected.",
        }
    )

    card = DiagnosticCardWidget(model)

    assert "High memory usage" in card.accessibleDescription()


def test_remediation_card_exposes_current_state(qapp):
    card = RemediationActionCardWidget(
        make_model()
    )

    description = card.accessibleDescription()

    assert "UNAUTHORIZED" in description
    assert "NOT_EXECUTED" in description


def test_remediation_card_state_updates_after_model_refresh(qapp):
    model = make_model()
    card = RemediationActionCardWidget(model)

    model._action["authorization_status"] = "AUTHORIZED"
    model._action["execution_status"] = "EXECUTED"

    card.refresh()

    description = card.accessibleDescription()

    assert "AUTHORIZED" in description
    assert "EXECUTED" in description


def test_remediation_review_button_has_action_description(qapp):
    card = RemediationActionCardWidget(
        make_model()
    )

    assert card.review_button.accessibleName()
    assert card.review_button.accessibleDescription()


def test_confirmation_dialog_exposes_current_authorization(qapp):
    dialog = RemediationConfirmationDialog(
        make_model()
    )

    assert dialog.accessibleName()
    assert dialog.accessibleDescription()

    assert "UNAUTHORIZED" in (
        dialog.authorization_label.accessibleDescription()
    )


def test_confirmation_dialog_action_is_accessibly_described(qapp):
    dialog = RemediationConfirmationDialog(
        make_model()
    )

    description = (
        dialog.action_label.accessibleDescription()
    )

    assert "memory_review" in description


def test_confirmation_dialog_warning_is_accessibly_described(qapp):
    dialog = RemediationConfirmationDialog(
        make_model()
    )

    description = (
        dialog.warning_label.accessibleDescription()
    )

    assert "approval" in description.lower()


def test_accessibility_layer_remains_presentation_only():
    public_names = {
        name
        for name in dir(AccessibilityHelper)
        if not name.startswith("_")
    }

    forbidden = {
        "diagnose",
        "analyze",
        "recommend",
        "authorize",
        "remediate",
        "execute",
        "retry",
        "verify",
    }

    assert public_names.isdisjoint(forbidden)
