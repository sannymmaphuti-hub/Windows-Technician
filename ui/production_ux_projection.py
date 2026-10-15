"""Composition boundary for Windows Technician production UX."""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from ui.accessibility_responsive_policy import AccessibilityResponsivePolicy
from ui.dashboard_information_model import (
    DashboardFinding,
    DashboardInformationModel,
)
from ui.diagnostic_case_presentation_model import DiagnosticCasePresentationModel
from ui.error_recovery_presentation import ErrorRecoveryPresentation
from ui.operation_progress_presentation import (
    OperationProgress,
    OperationProgressPresentation,
)
from ui.remediation_prompt_presentation import RemediationPromptPresentation
from ui.system_health_presentation import SystemHealthPresentation


class ProductionUXProjection:
    """Compose the canonical presentation models into one workspace projection."""

    SCHEMA_VERSION = "1.0"

    def __init__(self) -> None:
        self._dashboard = DashboardInformationModel()
        self._case = DiagnosticCasePresentationModel()
        self._health = SystemHealthPresentation()
        self._progress = OperationProgressPresentation()
        self._remediation = RemediationPromptPresentation()
        self._error_recovery = ErrorRecoveryPresentation()
        self._accessibility = AccessibilityResponsivePolicy()

    def build(
        self,
        *,
        system_name: str,
        health_status: str,
        dashboard_findings: Sequence[DashboardFinding],
        case_projection: Mapping[str, Any],
        health_findings: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
        activity: str = "Idle",
        next_steps: Sequence[str] = (),
        operation_progress: OperationProgress | None = None,
        remediation_action: Mapping[str, Any] | None = None,
        error: Mapping[str, Any] | None = None,
        empty_code: str | None = None,
        recovery: Mapping[str, Any] | None = None,
        viewport_width: int = 1280,
    ) -> dict[str, Any]:
        """Build a detached presentation projection without executing operations."""
        dashboard = self._dashboard.build(
            system_name=system_name,
            health_status=health_status,
            findings=dashboard_findings,
            activity=activity,
            next_steps=next_steps,
        )

        case = self._case.build(case_projection)
        health = self._health.build(
            health_status=health_status,
            findings=health_findings,
        )
        layout = self._accessibility.layout_for_width(viewport_width)
        accessibility = self._accessibility.accessibility_requirements()

        result: dict[str, Any] = {
            "schema_version": self.SCHEMA_VERSION,
            "dashboard": dashboard,
            "diagnostic_case": case,
            "system_health": health,
            "layout": layout,
            "accessibility": accessibility,
            "operation_progress": None,
            "remediation_prompt": None,
            "error_state": None,
            "empty_state": None,
            "recovery_state": None,
            "diagnostics_executed": False,
            "remediation_executed": False,
        }

        if operation_progress is not None:
            result["operation_progress"] = self._progress.build(
                operation_progress
            )

        if remediation_action is not None:
            result["remediation_prompt"] = self._remediation.build(
                remediation_action
            )

        if error is not None:
            result["error_state"] = self._error_recovery.build_error(
                error_code=error.get("error_code", "UNKNOWN"),
                detail=error.get("detail", ""),
            )

        if empty_code is not None:
            result["empty_state"] = self._error_recovery.build_empty(
                empty_code=empty_code
            )

        if recovery is not None:
            result["recovery_state"] = self._error_recovery.build_recovery(
                recovery_status=recovery.get("recovery_status", ""),
                detail=recovery.get("detail", ""),
            )

        return result
