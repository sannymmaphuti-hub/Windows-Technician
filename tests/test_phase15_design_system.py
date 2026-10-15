import pytest

from ui.design_system import (
    ColorTokens,
    DesignSystem,
    DesignTokens,
    Severity,
)


def test_default_design_system_has_consistent_tokens():
    system = DesignSystem()

    assert system.tokens.colors.surface == "#FFFFFF"
    assert system.tokens.spacing.md == 12
    assert system.tokens.typography.family == "Segoe UI"
    assert system.tokens.shapes.minimum_control_height >= 36


def test_design_tokens_are_immutable():
    system = DesignSystem()

    with pytest.raises(AttributeError):
        system.tokens.colors = ColorTokens()

    with pytest.raises(AttributeError):
        system.tokens.colors.accent = "#000000"


@pytest.mark.parametrize(
    "severity",
    [
        Severity.HEALTHY,
        Severity.INFO,
        Severity.WARNING,
        Severity.CRITICAL,
        Severity.UNKNOWN,
    ],
)
def test_every_severity_has_foreground_and_background(severity):
    result = DesignSystem().severity_colors(severity)

    assert result["foreground"].startswith("#")
    assert result["background"].startswith("#")
    assert result["foreground"] != result["background"]


def test_invalid_severity_type_is_rejected():
    with pytest.raises(TypeError):
        DesignSystem().severity_colors("critical")


def test_stylesheet_contains_shared_widget_rules():
    stylesheet = DesignSystem().stylesheet()

    assert "QMainWindow" in stylesheet
    assert "QPushButton:hover" in stylesheet
    assert "QPushButton:disabled" in stylesheet
    assert "QLineEdit:focus" in stylesheet
    assert "QProgressBar::chunk" in stylesheet
    assert "QTableView" in stylesheet


def test_stylesheet_uses_configured_tokens():
    tokens = DesignTokens(
        colors=ColorTokens(accent="#334455"),
    )
    stylesheet = DesignSystem(tokens).stylesheet()

    assert "#334455" in stylesheet


def test_projection_is_detached():
    system = DesignSystem()

    snapshot = system.projection()
    snapshot["colors"]["accent"] = "#000000"
    snapshot["severity_values"].clear()

    fresh = system.projection()

    assert fresh["colors"]["accent"] != "#000000"
    assert len(fresh["severity_values"]) == 5


def test_projection_identifies_schema_version():
    result = DesignSystem().projection()

    assert result["schema_version"] == "1.0"
    assert "spacing" in result
    assert "typography" in result
    assert "shapes" in result


def test_stylesheet_has_accessible_disabled_and_focus_states():
    stylesheet = DesignSystem().stylesheet()

    assert "QPushButton:disabled" in stylesheet
    assert "QPushButton:focus" in stylesheet
    assert "QLineEdit:focus" in stylesheet
    assert "selection-color:" in stylesheet
