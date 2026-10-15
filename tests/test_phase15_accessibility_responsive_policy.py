import pytest

from ui.accessibility_responsive_policy import (
    AccessibilityResponsivePolicy,
    ResponsiveBreakpoints,
)


def test_compact_layout_uses_single_column_and_collapsed_navigation():
    result = AccessibilityResponsivePolicy().layout_for_width(600)

    assert result["layout_mode"] == "COMPACT"
    assert result["content_columns"] == 1
    assert result["navigation_mode"] == "COLLAPSED"


def test_standard_layout_uses_two_columns():
    result = AccessibilityResponsivePolicy().layout_for_width(900)

    assert result["layout_mode"] == "STANDARD"
    assert result["content_columns"] == 2


def test_wide_layout_uses_three_columns():
    result = AccessibilityResponsivePolicy().layout_for_width(1440)

    assert result["layout_mode"] == "WIDE"
    assert result["content_columns"] == 3
    assert result["navigation_mode"] == "EXPANDED"


def test_custom_breakpoints_are_supported():
    policy = AccessibilityResponsivePolicy(
        ResponsiveBreakpoints(compact_max=500, wide_min=1200)
    )

    assert policy.layout_for_width(500)["layout_mode"] == "COMPACT"
    assert policy.layout_for_width(501)["layout_mode"] == "STANDARD"
    assert policy.layout_for_width(1200)["layout_mode"] == "WIDE"


def test_invalid_widths_are_rejected():
    policy = AccessibilityResponsivePolicy()

    with pytest.raises(ValueError):
        policy.layout_for_width(0)

    with pytest.raises(ValueError):
        policy.layout_for_width(-100)

    with pytest.raises(TypeError):
        policy.layout_for_width(True)


def test_invalid_breakpoints_are_rejected():
    with pytest.raises(ValueError):
        ResponsiveBreakpoints(compact_max=200, wide_min=1100)

    with pytest.raises(ValueError):
        ResponsiveBreakpoints(compact_max=700, wide_min=700)


def test_accessibility_requirements_cover_keyboard_and_severity():
    result = AccessibilityResponsivePolicy().accessibility_requirements()

    assert result["keyboard_navigation"] is True
    assert result["visible_keyboard_focus"] is True
    assert result["accessible_name_required_for_interactive_controls"] is True
    assert result["color_is_not_the_only_severity_indicator"] is True
    assert result["text_scaling_supported"] is True


def test_interactive_control_requires_accessible_name():
    result = AccessibilityResponsivePolicy().validate_control(
        accessible_name="",
        interactive=True,
    )

    assert result["accessible"] is False
    assert "MISSING_ACCESSIBLE_NAME" in result["issues"]


def test_small_interactive_target_is_reported():
    result = AccessibilityResponsivePolicy().validate_control(
        accessible_name="Open diagnostic case",
        interactive=True,
        width=30,
        height=30,
    )

    assert result["accessible"] is False
    assert "TOUCH_TARGET_TOO_SMALL" in result["issues"]


def test_sufficiently_sized_named_control_passes():
    result = AccessibilityResponsivePolicy().validate_control(
        accessible_name="Open diagnostic case",
        interactive=True,
        width=44,
        height=44,
    )

    assert result["accessible"] is True
    assert result["issues"] == []


def test_noninteractive_control_does_not_require_touch_target():
    result = AccessibilityResponsivePolicy().validate_control(
        accessible_name="",
        interactive=False,
        width=20,
        height=20,
    )

    assert result["accessible"] is True


def test_policy_validation_rejects_invalid_control_dimensions():
    policy = AccessibilityResponsivePolicy()

    with pytest.raises(ValueError):
        policy.validate_control(
            accessible_name="Open case",
            width=0,
        )

    with pytest.raises(TypeError):
        policy.validate_control(
            accessible_name="Open case",
            height=True,
        )


def test_policy_does_not_execute_operations():
    policy = AccessibilityResponsivePolicy()

    layout = policy.layout_for_width(800)
    requirements = policy.accessibility_requirements()

    assert layout["horizontal_overflow_allowed"] is False
    assert requirements["diagnostics_executed"] is False
    assert requirements["remediation_executed"] is False
