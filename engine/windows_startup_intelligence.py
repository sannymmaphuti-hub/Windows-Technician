# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP INTELLIGENCE
# ==========================================

from engine.finding import Finding
from engine.recommendation import Recommendation
from engine.signal import Signal
from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)


class WindowsStartupIntelligence:
    domain = "STARTUP"

    def analyze(self, evidence):
        if not isinstance(
            evidence,
            WindowsStartupEvidence,
        ):
            raise ValueError(
                "Startup intelligence requires "
                "WindowsStartupEvidence."
            )

        signals = []
        findings = []
        recommendations = []

        for item in evidence.items:
            if not isinstance(item, dict):
                continue

            name = item.get("name")
            command = item.get("command")
            enabled = item.get("enabled")

            if not self._valid_item(
                name,
                command,
                enabled,
            ):
                continue

            if enabled is not True:
                continue

            if not command.strip():
                signal = Signal(
                    signal_type=(
                        "STARTUP_COMMAND_MISSING"
                    ),
                    source="STARTUP",
                    subject=name,
                    attribute="command",
                    value=command,
                    strength="MEDIUM",
                    quality="HIGH",
                )

                finding = Finding(
                    finding_type=(
                        "STARTUP_COMMAND_MISSING"
                    ),
                    category="STARTUP",
                    severity="MEDIUM",
                    description=(
                        f"Startup entry {name} "
                        "does not contain a command."
                    ),
                    supporting_signals=[
                        signal
                    ],
                )

                recommendation = Recommendation(
                    recommendation_type=(
                        "REVIEW_STARTUP_ENTRY"
                    ),
                    category="STARTUP",
                    priority="MEDIUM",
                    description=(
                        f"Review startup entry "
                        f"{name}."
                    ),
                    rationale=(
                        f"Startup entry {name} "
                        "is enabled but its command "
                        "is missing, so Windows may "
                        "not be able to launch the "
                        "expected startup component."
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
    def _valid_item(
        name,
        command,
        enabled,
    ):
        if not isinstance(name, str):
            return False

        if not name.strip():
            return False

        if not isinstance(command, str):
            return False

        if not isinstance(enabled, bool):
            return False

        return True