# ==========================================
# Windows Technician v0.9
# WINDOWS SERVICES INTELLIGENCE
# ==========================================

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.signal import Signal

from engine.windows_services_evidence import (
    WindowsServicesEvidence,
)


class WindowsServicesIntelligence:
    """
    Interpret Windows service evidence into canonical
    Signals, Findings, and Recommendations.

    Only services explicitly marked as required are treated
    as service-health problems.

    This prevents normal Windows behavior, such as an
    on-demand service being stopped, from being incorrectly
    reported as a problem.

    This class does NOT:
    - collect services
    - start services
    - stop services
    - enable services
    - disable services
    - authorize remediation
    - execute remediation
    - verify remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    domain = "SERVICES"

    def analyze(self, evidence):
        """
        Analyze Windows service evidence.

        Returns canonical Signal, Finding, and
        Recommendation objects.
        """

        if not isinstance(
            evidence,
            WindowsServicesEvidence,
        ):
            raise ValueError(
                "Services intelligence requires "
                "WindowsServicesEvidence."
            )

        signals = []
        findings = []
        recommendations = []

        for service in evidence.services:
            if not isinstance(service, dict):
                continue

            name = service.get("name")
            status = service.get("status")
            start_type = service.get(
                "start_type"
            )
            required = service.get(
                "required",
                False,
            )

            if not self._valid_service(
                name,
                status,
                start_type,
            ):
                continue

            if required is not True:
                continue

            if start_type == "DISABLED":
                signal = Signal(
                    signal_type="SERVICE_DISABLED",
                    source="SERVICES",
                    subject=name,
                    attribute="start_type",
                    value=start_type,
                    strength="HIGH",
                    quality="HIGH",
                )

                finding = Finding(
                    finding_type="SERVICE_DISABLED",
                    category="SERVICES",
                    severity="HIGH",
                    description=(
                        f"Required service {name} "
                        "is disabled."
                    ),
                    supporting_signals=[signal],
                )

                recommendation = Recommendation(
                    recommendation_type=(
                        "REVIEW_SERVICE_STATE"
                    ),
                    category="SERVICES",
                    priority="HIGH",
                    description=(
                        f"Review the startup configuration "
                        f"of required service {name}."
                    ),
                    rationale=(
                        f"Required service {name} is "
                        "configured as disabled and may "
                        "be unavailable when Windows or "
                        "an application needs it."
                    ),
                )

                signals.append(signal)
                findings.append(finding)
                recommendations.append(
                    recommendation
                )

                continue

            if status == "STOPPED":
                signal = Signal(
                    signal_type="SERVICE_STOPPED",
                    source="SERVICES",
                    subject=name,
                    attribute="status",
                    value=status,
                    strength="MEDIUM",
                    quality="HIGH",
                )

                finding = Finding(
                    finding_type="SERVICE_UNAVAILABLE",
                    category="SERVICES",
                    severity="HIGH",
                    description=(
                        f"Required service {name} "
                        "is stopped."
                    ),
                    supporting_signals=[signal],
                )

                recommendation = Recommendation(
                    recommendation_type=(
                        "REVIEW_SERVICE_STATE"
                    ),
                    category="SERVICES",
                    priority="HIGH",
                    description=(
                        f"Review the state of required "
                        f"service {name}."
                    ),
                    rationale=(
                        f"Required service {name} is "
                        "stopped and may prevent Windows "
                        "or an application from performing "
                        "its expected function."
                    ),
                )

                signals.append(signal)
                findings.append(finding)
                recommendations.append(
                    recommendation
                )

        return {
            "signals": signals,
            "findings": findings,
            "recommendations": recommendations,
        }

    @staticmethod
    def _valid_service(
        name,
        status,
        start_type,
    ):
        if not isinstance(name, str):
            return False

        if not name.strip():
            return False

        valid_statuses = {
            "RUNNING",
            "STOPPED",
            "UNKNOWN",
        }

        valid_start_types = {
            "AUTO",
            "MANUAL",
            "DISABLED",
            "UNKNOWN",
        }

        if status not in valid_statuses:
            return False

        if start_type not in valid_start_types:
            return False

        return True