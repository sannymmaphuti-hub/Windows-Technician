"""Shared visual design system for Windows Technician.

This module defines presentation tokens and Qt stylesheet generation.
It contains no diagnostic, authorization, or remediation logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Final


class Severity(str, Enum):
    """Semantic severity states shared by the application UI."""

    HEALTHY = "healthy"
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ColorTokens:
    """Semantic colors used throughout the interface."""

    app_background: str = "#F4F7FB"
    surface: str = "#FFFFFF"
    surface_subtle: str = "#EAF0F7"
    border: str = "#D5DEEA"

    text_primary: str = "#172334"
    text_secondary: str = "#526176"
    text_muted: str = "#65758B"
    text_on_accent: str = "#FFFFFF"

    accent: str = "#2457C5"
    accent_hover: str = "#1947A8"
    accent_pressed: str = "#12377F"
    focus: str = "#2457C5"

    healthy: str = "#18794E"
    healthy_background: str = "#E7F5ED"

    info: str = "#2457C5"
    info_background: str = "#EAF1FF"

    warning: str = "#8A5200"
    warning_background: str = "#FFF3D6"

    critical: str = "#B42318"
    critical_background: str = "#FDECEA"

    unknown: str = "#526176"
    unknown_background: str = "#E9EDF2"

    disabled_background: str = "#E7EBF1"
    disabled_text: str = "#65758B"


@dataclass(frozen=True, slots=True)
class SpacingTokens:
    """Spacing values are expressed in Qt stylesheet pixels."""

    xs: int = 4
    sm: int = 8
    md: int = 12
    lg: int = 16
    xl: int = 24
    xxl: int = 32


@dataclass(frozen=True, slots=True)
class TypographyTokens:
    """Typography sizes are expressed in points."""

    family: str = "Segoe UI"
    small: int = 9
    body: int = 10
    subtitle: int = 12
    heading: int = 16
    display: int = 22


@dataclass(frozen=True, slots=True)
class ShapeTokens:
    """Shared corner radii and control sizing."""

    radius_small: int = 4
    radius_medium: int = 8
    radius_large: int = 12
    minimum_control_height: int = 36
    minimum_touch_target: int = 44


@dataclass(frozen=True, slots=True)
class DesignTokens:
    """Complete immutable visual configuration."""

    colors: ColorTokens = ColorTokens()
    spacing: SpacingTokens = SpacingTokens()
    typography: TypographyTokens = TypographyTokens()
    shapes: ShapeTokens = ShapeTokens()


DEFAULT_TOKENS: Final[DesignTokens] = DesignTokens()


class DesignSystem:
    """Provides semantic presentation values and a shared Qt stylesheet."""

    SCHEMA_VERSION: Final[str] = "1.0"

    def __init__(self, tokens: DesignTokens | None = None) -> None:
        self._tokens = tokens if tokens is not None else DEFAULT_TOKENS

    @property
    def tokens(self) -> DesignTokens:
        return self._tokens

    def severity_colors(self, severity: Severity) -> dict[str, str]:
        if not isinstance(severity, Severity):
            raise TypeError("severity must be a Severity value")

        colors = self._tokens.colors

        mapping = {
            Severity.HEALTHY: (
                colors.healthy,
                colors.healthy_background,
            ),
            Severity.INFO: (
                colors.info,
                colors.info_background,
            ),
            Severity.WARNING: (
                colors.warning,
                colors.warning_background,
            ),
            Severity.CRITICAL: (
                colors.critical,
                colors.critical_background,
            ),
            Severity.UNKNOWN: (
                colors.unknown,
                colors.unknown_background,
            ),
        }

        foreground, background = mapping[severity]
        return {
            "foreground": foreground,
            "background": background,
        }

    def stylesheet(self) -> str:
        """Generate a consistent stylesheet for standard Qt widgets."""
        tokens = self._tokens
        colors = tokens.colors
        spacing = tokens.spacing
        typography = tokens.typography
        shapes = tokens.shapes

        return f"""
QWidget {{
    color: {colors.text_primary};
    font-family: "{typography.family}";
    font-size: {typography.body}pt;
}}

QMainWindow, QDialog {{
    background-color: {colors.app_background};
}}

QFrame#Card, QGroupBox {{
    background-color: {colors.surface};
    border: 1px solid {colors.border};
    border-radius: {shapes.radius_medium}px;
}}

QGroupBox {{
    margin-top: {spacing.lg}px;
    padding: {spacing.lg}px;
    padding-top: {spacing.xl}px;
    font-weight: 600;
}}

QLabel#PageTitle {{
    color: {colors.text_primary};
    font-size: {typography.display}pt;
    font-weight: 700;
}}

QLabel#SectionTitle {{
    color: {colors.text_primary};
    font-size: {typography.heading}pt;
    font-weight: 600;
}}

QLabel#SecondaryText {{
    color: {colors.text_secondary};
}}

QLabel#MutedText {{
    color: {colors.text_muted};
}}

QPushButton {{
    background-color: {colors.accent};
    color: {colors.text_on_accent};
    border: 1px solid {colors.accent};
    border-radius: {shapes.radius_small}px;
    min-height: {shapes.minimum_control_height}px;
    padding: 0 {spacing.lg}px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {colors.accent_hover};
    border-color: {colors.accent_hover};
}}

QPushButton:pressed {{
    background-color: {colors.accent_pressed};
    border-color: {colors.accent_pressed};
}}

QPushButton:disabled {{
    background-color: {colors.disabled_background};
    color: {colors.disabled_text};
    border-color: {colors.disabled_background};
}}

QPushButton:focus,
QLineEdit:focus,
QComboBox:focus,
QTextEdit:focus,
QPlainTextEdit:focus {{
    border: 2px solid {colors.focus};
}}

QPushButton#SecondaryButton {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
}}

QLineEdit, QComboBox, QTextEdit, QPlainTextEdit {{
    background-color: {colors.surface};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    border-radius: {shapes.radius_small}px;
    padding: {spacing.sm}px;
    selection-background-color: {colors.accent};
    selection-color: {colors.text_on_accent};
}}

QScrollArea {{
    background-color: transparent;
    border: none;
}}

QToolTip {{
    background-color: {colors.text_primary};
    color: {colors.text_on_accent};
    border: 1px solid {colors.border};
    padding: {spacing.sm}px;
}}

QProgressBar {{
    background-color: {colors.surface_subtle};
    color: {colors.text_primary};
    border: 1px solid {colors.border};
    border-radius: {shapes.radius_small}px;
    min-height: 12px;
    text-align: center;
}}

QProgressBar::chunk {{
    background-color: {colors.accent};
    border-radius: {shapes.radius_small}px;
}}

QTableView {{
    background-color: {colors.surface};
    alternate-background-color: {colors.surface_subtle};
    color: {colors.text_primary};
    gridline-color: {colors.border};
    selection-background-color: {colors.info_background};
    selection-color: {colors.text_primary};
}}

QTableView::item {{
    padding: {spacing.sm}px;
}}

QCheckBox, QRadioButton {{
    spacing: {spacing.sm}px;
}}

QCheckBox:focus, QRadioButton:focus {{
    outline: 2px solid {colors.focus};
}}
""".strip()

    def projection(self) -> dict[str, object]:
        """Return a detached, serializable description of the design system."""
        tokens = self._tokens
        colors = tokens.colors

        return {
            "schema_version": self.SCHEMA_VERSION,
            "colors": {
                name: getattr(colors, name)
                for name in colors.__dataclass_fields__
            },
            "spacing": {
                name: getattr(tokens.spacing, name)
                for name in tokens.spacing.__dataclass_fields__
            },
            "typography": {
                name: getattr(tokens.typography, name)
                for name in tokens.typography.__dataclass_fields__
            },
            "shapes": {
                name: getattr(tokens.shapes, name)
                for name in tokens.shapes.__dataclass_fields__
            },
            "severity_values": [severity.value for severity in Severity],
        }
