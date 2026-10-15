"""System-health and severity communication for the production UX."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from ui.design_system import Severity


class SystemHealthPresentation:
    """Translate health findings into consistent user-facing summaries."""

    SCHEMA_VERSION = "1.0"

    _SEVERITY_ORDER = {
        "CRITICAL": 0,
        "WARNING": 1,
        "INFO": 2,
        "HEALTHY": 3,
        "UNKNOWN": 4,
    }

    _MESSAGES = {
        Severity.CRITICAL.value: "Critical issue requiring attention.",
        Severity.WARNING.value: "Potential issue requiring review.",
        Severity.INFO.value: "Information available for review.",
        Severity.HEALTHY.value: "No reported issues requiring attention.",
        Severity.UNKNOWN.value: "System health could not be determined.",
    }

    _CANONICAL_VALUES = {
        name: member.value
        for name, member in Severity.__members__.items()
    }

    def _normalize_severity(self, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            return Severity.UNKNOWN.value

        name = value.strip().upper()
        if name not in self._SEVERITY_ORDER:
            return Severity.UNKNOWN.value

        return self._CANONICAL_VALUES.get(name, Severity.UNKNOWN.value)

    def build(
        self,
        *,
        health_status: str,
        findings: list[Mapping[str, Any]] | tuple[Mapping[str, Any], ...],
    ) -> dict[str, Any]:
        if not isinstance(health_status, str) or not health_status.strip():
            raise ValueError("health_status must be a non-empty string")

        if isinstance(findings, (str, bytes)) or not isinstance(
            findings, (list, tuple)
        ):
            raise TypeError("findings must be a list or tuple")

        normalized = []

        for index, finding in enumerate(findings):
            if not isinstance(finding, Mapping):
                raise TypeError(f"finding at index {index} must be a mapping")

            item = deepcopy(dict(finding))
            item["severity"] = self._normalize_severity(
                item.get("severity", Severity.UNKNOWN.value)
            )
            normalized.append(item)

        normalized.sort(
            key=lambda item: self._SEVERITY_ORDER.get(
                item["severity"].upper(),
                self._SEVERITY_ORDER["UNKNOWN"],
            )
        )

        if normalized:
            highest_severity = normalized[0]["severity"]
        else:
            highest_severity = self._normalize_severity(health_status)

        return {
            "schema_version": self.SCHEMA_VERSION,
            "health_status": health_status.strip(),
            "highest_severity": highest_severity,
            "summary": self._MESSAGES[highest_severity],
            "finding_count": len(normalized),
            "severity_counts": {
                severity.name: sum(
                    1
                    for item in normalized
                    if item["severity"] == severity.value
                )
                for severity in Severity
            },
            "findings": normalized,
            "diagnostics_executed": False,
            "remediation_executed": False,
        }
