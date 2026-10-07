from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.signal import Signal
from engine.windows_system_evidence import (
    WindowsSystemEvidence,
)


class WindowsSystemIntelligence:
    domain = "SYSTEM"

    def analyze(self, evidence):
        if not isinstance(
            evidence,
            WindowsSystemEvidence,
        ):
            raise ValueError(
                "System intelligence requires "
                "WindowsSystemEvidence."
            )

        missing_fields = []

        if not evidence.operating_system.strip():
            missing_fields.append(
                "operating_system"
            )

        if not evidence.os_version.strip():
            missing_fields.append(
                "os_version"
            )

        if not evidence.architecture.strip():
            missing_fields.append(
                "architecture"
            )

        if not missing_fields:
            return {
                "signals": [],
                "findings": [],
                "recommendations": [],
            }

        signals = []
        findings = []
        recommendations = []

        signal = Signal(
            signal_type=(
                "SYSTEM_OS_INFORMATION_MISSING"
            ),
            source="SYSTEM",
            subject="Windows",
            attribute="system_information",
            value=missing_fields,
            strength="MEDIUM",
            quality="HIGH",
        )

        finding = Finding(
            finding_type=(
                "SYSTEM_OS_INFORMATION_MISSING"
            ),
            category="SYSTEM",
            severity="MEDIUM",
            description=(
                "Required Windows operating-system "
                "information could not be determined."
            ),
            supporting_signals=[signal],
        )

        recommendation = Recommendation(
            recommendation_type=(
                "REVIEW_SYSTEM_INFORMATION"
            ),
            category="SYSTEM",
            priority="MEDIUM",
            description=(
                "Review Windows operating-system "
                "information and verify that the "
                "system can report its OS details."
            ),
            rationale=(
                "The diagnostic system could not "
                "determine one or more required "
                "Windows operating-system fields: "
                f"{', '.join(missing_fields)}."
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