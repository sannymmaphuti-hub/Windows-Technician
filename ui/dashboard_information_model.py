"""Dashboard information hierarchy and presentation projection."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


@dataclass(frozen=True, slots=True)
class DashboardFinding:
    title: str
    severity: str
    explanation: str
    requires_attention: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must be a non-empty string")
        if not isinstance(self.severity, str) or not self.severity.strip():
            raise ValueError("severity must be a non-empty string")
        if not isinstance(self.explanation, str):
            raise TypeError("explanation must be a string")
        if not isinstance(self.requires_attention, bool):
            raise TypeError("requires_attention must be a boolean")

    def projection(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "severity": self.severity,
            "explanation": self.explanation,
            "requires_attention": self.requires_attention,
        }


class DashboardInformationModel:
    """Organizes supplied system information without diagnosing the machine."""

    SCHEMA_VERSION = "1.0"

    def build(
        self,
        *,
        system_name: str,
        health_status: str,
        findings: Sequence[DashboardFinding],
        activity: str = "Idle",
        next_steps: Sequence[str] = (),
    ) -> dict[str, Any]:
        if not isinstance(system_name, str) or not system_name.strip():
            raise ValueError("system_name must be a non-empty string")

        if not isinstance(health_status, str) or not health_status.strip():
            raise ValueError("health_status must be a non-empty string")

        if not isinstance(activity, str) or not activity.strip():
            raise ValueError("activity must be a non-empty string")

        if isinstance(findings, (str, bytes)) or not isinstance(
            findings, Sequence
        ):
            raise TypeError("findings must be a sequence of DashboardFinding")

        if any(not isinstance(item, DashboardFinding) for item in findings):
            raise TypeError("every finding must be a DashboardFinding")

        if isinstance(next_steps, (str, bytes)) or not isinstance(
            next_steps, Sequence
        ):
            raise TypeError("next_steps must be a sequence of strings")

        if any(
            not isinstance(step, str) or not step.strip()
            for step in next_steps
        ):
            raise ValueError("every next step must be a non-empty string")

        finding_projections = [item.projection() for item in findings]
        attention_count = sum(
            1 for item in findings if item.requires_attention
        )

        return {
            "schema_version": self.SCHEMA_VERSION,
            "system": {"name": system_name},
            "health": {
                "status": health_status,
                "finding_count": len(findings),
                "attention_count": attention_count,
            },
            "priority_findings": [
                item
                for item in finding_projections
                if item["requires_attention"]
            ],
            "findings": finding_projections,
            "activity": {"status": activity},
            "next_steps": list(next_steps),
            "diagnostics_executed": False,
            "remediation_executed": False,
        }
