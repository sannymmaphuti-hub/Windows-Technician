"""Accessibility and responsive-layout policies for Windows Technician."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ResponsiveBreakpoints:
    """Window-width boundaries, expressed in logical pixels."""

    compact_max: int = 640
    wide_min: int = 1100

    def __post_init__(self) -> None:
        if (
            isinstance(self.compact_max, bool)
            or not isinstance(self.compact_max, int)
            or self.compact_max < 320
        ):
            raise ValueError("compact_max must be an integer of at least 320")

        if (
            isinstance(self.wide_min, bool)
            or not isinstance(self.wide_min, int)
            or self.wide_min <= self.compact_max
        ):
            raise ValueError("wide_min must be greater than compact_max")


class AccessibilityResponsivePolicy:
    """Produce deterministic accessibility and layout guidance."""

    SCHEMA_VERSION = "1.0"

    def __init__(
        self,
        breakpoints: ResponsiveBreakpoints | None = None,
    ) -> None:
        self._breakpoints = breakpoints or ResponsiveBreakpoints()

    def layout_for_width(self, width: int) -> dict[str, Any]:
        if isinstance(width, bool) or not isinstance(width, int):
            raise TypeError("width must be an integer")

        if width <= 0:
            raise ValueError("width must be greater than zero")

        if width <= self._breakpoints.compact_max:
            mode = "COMPACT"
            columns = 1
            navigation = "COLLAPSED"
        elif width >= self._breakpoints.wide_min:
            mode = "WIDE"
            columns = 3
            navigation = "EXPANDED"
        else:
            mode = "STANDARD"
            columns = 2
            navigation = "EXPANDED"

        return {
            "schema_version": self.SCHEMA_VERSION,
            "viewport_width": width,
            "layout_mode": mode,
            "content_columns": columns,
            "navigation_mode": navigation,
            "horizontal_overflow_allowed": False,
        }

    def accessibility_requirements(self) -> dict[str, Any]:
        return {
            "schema_version": self.SCHEMA_VERSION,
            "keyboard_navigation": True,
            "visible_keyboard_focus": True,
            "accessible_name_required_for_interactive_controls": True,
            "accessible_description_for_complex_controls": True,
            "minimum_touch_target_width": 44,
            "minimum_touch_target_height": 44,
            "text_scaling_supported": True,
            "color_is_not_the_only_severity_indicator": True,
            "status_changes_should_be_announced": True,
            "focus_order_should_follow_reading_order": True,
            "diagnostics_executed": False,
            "remediation_executed": False,
        }

    def validate_control(
        self,
        *,
        accessible_name: str,
        interactive: bool = True,
        width: int = 44,
        height: int = 44,
    ) -> dict[str, Any]:
        if not isinstance(accessible_name, str):
            raise TypeError("accessible_name must be a string")

        if not isinstance(interactive, bool):
            raise TypeError("interactive must be a boolean")

        for field, value in (("width", width), ("height", height)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{field} must be an integer")
            if value <= 0:
                raise ValueError(f"{field} must be greater than zero")

        has_name = bool(accessible_name.strip())
        meets_target = width >= 44 and height >= 44

        issues = []

        if interactive and not has_name:
            issues.append("MISSING_ACCESSIBLE_NAME")

        if interactive and not meets_target:
            issues.append("TOUCH_TARGET_TOO_SMALL")

        return {
            "accessible_name_present": has_name,
            "interactive": interactive,
            "touch_target_width": width,
            "touch_target_height": height,
            "meets_minimum_touch_target": meets_target,
            "issues": issues,
            "accessible": not issues,
        }
