# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE INTELLIGENCE
# ==========================================

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.signal import Signal
from engine.windows_storage_evidence import (
    WindowsStorageEvidence,
)


class WindowsStorageIntelligence:
    """
    Interpret Windows storage evidence into canonical
    Signals, Findings, and Recommendations.

    This class performs intelligence only.

    It does NOT:
    - collect storage information
    - modify storage
    - delete files
    - repair volumes
    - authorize remediation
    - execute remediation
    - verify remediation
    - create DiagnosticCase objects
    - manage technician workflow
    """

    domain = "STORAGE"

    WARNING_FREE_SPACE_RATIO = 0.15
    CRITICAL_FREE_SPACE_RATIO = 0.05

    def analyze(self, evidence):
        """
        Analyze storage evidence.

        Returns a dictionary containing canonical Signal,
        Finding, and Recommendation objects.
        """

        if not isinstance(
            evidence,
            WindowsStorageEvidence,
        ):
            raise ValueError(
                "Storage intelligence requires "
                "WindowsStorageEvidence."
            )

        signals = []
        findings = []
        recommendations = []

        for volume in evidence.volumes:

            if not isinstance(volume, dict):
                continue

            drive = volume.get("drive")
            total_bytes = volume.get("total_bytes")
            free_bytes = volume.get("free_bytes")

            if not self._valid_volume(
                drive,
                total_bytes,
                free_bytes,
            ):
                continue

            free_space_ratio = (
                free_bytes / total_bytes
            )

            if (
                free_space_ratio
                >= self.WARNING_FREE_SPACE_RATIO
            ):
                continue

            severity = self._severity(
                free_space_ratio
            )

            strength = self._signal_strength(
                severity
            )

            signal = Signal(
                signal_type="LOW_FREE_SPACE",
                source="STORAGE",
                subject=drive,
                attribute="free_space_ratio",
                value=free_space_ratio,
                strength=strength,
                quality="HIGH",
            )

            finding = Finding(
                finding_type="STORAGE_PRESSURE",
                category="STORAGE",
                severity=severity,
                description=(
                    f"{drive} has low available storage "
                    f"space ({free_space_ratio:.2%} free)."
                ),
                supporting_signals=[signal],
            )

            recommendation = Recommendation(
                recommendation_type=(
                    "REVIEW_STORAGE_USAGE"
                ),
                category="STORAGE",
                priority=severity,
                description=(
                    f"Review storage usage on {drive} "
                    "and identify unnecessary data."
                ),
                rationale=(
                    f"{drive} has only "
                    f"{free_space_ratio:.2%} free space, "
                    "which may reduce available capacity "
                    "for normal Windows operation."
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

    @classmethod
    def _severity(cls, free_space_ratio):
        if (
            free_space_ratio
            < cls.CRITICAL_FREE_SPACE_RATIO
        ):
            return "CRITICAL"

        return "HIGH"

    @staticmethod
    def _signal_strength(severity):
        if severity == "CRITICAL":
            return "HIGH"

        return "MEDIUM"

    @staticmethod
    def _valid_volume(
        drive,
        total_bytes,
        free_bytes,
    ):
        if not isinstance(drive, str):
            return False

        if not drive.strip():
            return False

        if not isinstance(
            total_bytes,
            (int, float),
        ):
            return False

        if not isinstance(
            free_bytes,
            (int, float),
        ):
            return False

        if total_bytes <= 0:
            return False

        if free_bytes < 0:
            return False

        return True