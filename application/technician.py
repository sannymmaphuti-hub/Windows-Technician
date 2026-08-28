# ==========================================
# WINDOWS TECHNICIAN v0.2
# APPLICATION SERVICE
# ==========================================

from engine.factory import create_diagnostic_engine

class Technician:

    def __init__(self):

        self.diagnostic_engine = create_diagnostic_engine()
        

        self.last_result = None

    def diagnose(self):

        self.last_result = self.diagnostic_engine.analyze()

        return self.last_result

    def get_status(self):

        if self.last_result is None:

            self.diagnose()

        return self.last_result["diagnosis"]["status"]

    def get_primary_issue(self):

        if self.last_result is None:

            self.diagnose()

        diagnosis = self.last_result["diagnosis"]

        findings = diagnosis.get(
            "findings",
            []
        )

        if not findings:

            return {
                "status": "HEALTHY",
                "category": "SYSTEM",
                "issue": "No significant system issue detected.",
                "severity": "INFO",
                "priority_score": 0,
                "reason": (
                    "No significant diagnostic issue "
                    "was detected."
                )
            }

        highest_priority = max(
            findings,
            key=lambda finding: (
                finding.get("priority_score", 0)
            )
        )

        return {
            "status": highest_priority.get(
                "severity",
                "INFO"
            ),

            "category": highest_priority.get(
                "category",
                "SYSTEM"
            ),

            "issue": highest_priority.get(
                "issue",
                highest_priority.get(
                    "message",
                    "Unknown issue"
                )
            ),

            "severity": highest_priority.get(
                "severity",
                "INFO"
            ),

            "priority_score": highest_priority.get(
                "priority_score",
                0
            ),

            "reason": highest_priority.get(
                "reason",
                highest_priority.get(
                    "message",
                    "No diagnostic explanation available."
                )
            )
        }

    def get_report(self):

        if self.last_result is None:

            self.diagnose()

        diagnosis = self.last_result["diagnosis"]

        report = []

        report.append(
            "WINDOWS TECHNICIAN v0.2"
        )

        report.append(
            "=========================================="
        )

        report.append(
            f"Status: {diagnosis['status']}"
        )

        report.append(
            f"Total Findings: "
            f"{diagnosis['total_findings']}"
        )

        report.append("")

        report.append("FINDINGS")
        report.append("------------------------------------------")

        for number, finding in enumerate(
            diagnosis.get("findings", []),
            start=1
        ):

            report.append(
                f"{number}. "
                f"{finding.get('category', 'SYSTEM')}"
            )

            report.append(
                f"   Severity: "
                f"{finding.get('severity', 'INFO')}"
            )

            report.append(
                f"   Message: "
                f"{finding.get('message', '')}"
            )

        report.append("")

        report.append("RECOMMENDATIONS")
        report.append("------------------------------------------")

        for number, recommendation in enumerate(
            diagnosis.get("recommendations", []),
            start=1
        ):

            report.append(
                f"{number}. "
                f"{recommendation.get('category', 'SYSTEM')}"
            )

            report.append(
                f"   Recommendation: "
                f"{recommendation.get('recommendation', '')}"
            )

        return "\n".join(report)
