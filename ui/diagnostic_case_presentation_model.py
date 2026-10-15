"""Read-only presentation model for canonical diagnostic cases."""
from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


class DiagnosticCasePresentationModel:
    """Project canonical case data into a UI-friendly, read-only structure."""

    SCHEMA_VERSION = "1.0"

    def build(self, case_projection: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(case_projection, Mapping):
            raise TypeError("case_projection must be a mapping")

        source = deepcopy(dict(case_projection))

        case_id = source.get("case_id", source.get("uuid", ""))
        if case_id is None:
            case_id = ""

        status = source.get("status", "UNKNOWN")
        state = source.get("state", "UNKNOWN")

        findings = source.get("findings", [])
        recommendations = source.get("recommendations", [])
        evidence = source.get("evidence", [])
        correlations = source.get("correlations", [])
        root_causes = source.get("root_causes", [])

        for name, value in (
            ("findings", findings),
            ("recommendations", recommendations),
            ("evidence", evidence),
            ("correlations", correlations),
            ("root_causes", root_causes),
        ):
            if not isinstance(value, (list, tuple)):
                raise TypeError(f"{name} must be a list or tuple")

        return {
            "schema_version": self.SCHEMA_VERSION,
            "identity": {"case_id": str(case_id)},
            "lifecycle": {
                "status": str(status),
                "state": str(state),
            },
            "summary": {
                "finding_count": len(findings),
                "recommendation_count": len(recommendations),
                "evidence_count": len(evidence),
                "correlation_count": len(correlations),
                "root_cause_count": len(root_causes),
            },
            "findings": deepcopy(list(findings)),
            "recommendations": deepcopy(list(recommendations)),
            "evidence": deepcopy(list(evidence)),
            "correlations": deepcopy(list(correlations)),
            "root_causes": deepcopy(list(root_causes)),
            "diagnostics_executed": False,
            "remediation_executed": False,
        }
