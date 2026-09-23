# ==========================================
# WINDOWS TECHNICIAN v0.6
# APPLICATION ENTRY POINT
# ==========================================
from copy import deepcopy
from pathlib import Path

from application.technician import Technician
from application.diagnostic_view import DiagnosticView
from application.dashboard_view_model import DashboardViewModel


class TechnicianApp:
    def __init__(self):
        self.technician = Technician()
        self._execution_state = "READY"

    def get_execution_state(self):
        return self._execution_state

    def run_diagnostics(self):
        self._execution_state = "RUNNING"

        try:
            result = self.technician.diagnose()
            self._execution_state = "COMPLETED"
            return deepcopy(result)

        except Exception:
            self._execution_state = "ERROR"
            raise

    def get_status(self):
        return self.technician.get_status()

    def get_primary_issue(self):
        return self.technician.get_primary_issue()

    def get_report(self):
        return self.technician.get_report()

    def get_dashboard_view_model(self):
        if self.technician.last_result is None:
            self.technician.diagnose()

        dashboard_result = deepcopy(
            self.technician.last_result
        )

        dashboard_result["remediation_audit"] = (
            self.get_remediation_audit()
        )

        diagnostic_view = DiagnosticView(
            dashboard_result
        )

        return DashboardViewModel(
            diagnostic_view,
            execution_state=self._execution_state
        )

    def save_report(self):
        
        report = self.get_report()
        reports_directory = Path("reports")
        reports_directory.mkdir(exist_ok=True)
        report_path = reports_directory / "technician_report.txt"
        report_path.write_text(report, encoding="utf-8")

        return str(report_path)

    def get_remediation_audit(self):
        return self.technician.get_remediation_audit()


def print_section(title):

    print()
    print(title)
    print("------------------------------------------")


def print_findings(diagnosis):

    findings = diagnosis.get(
        "findings",
        []
    )

    if not findings:

        print_section("FINDINGS")
        print("No significant findings detected.")
        return

    print_section("FINDINGS")

    for number, finding in enumerate(
        findings,
        start=1
    ):

        print(
            f"{number}. "
            f"{finding.get('category', 'SYSTEM')}"
        )

        print(
            f"   Severity   : "
            f"{finding.get('severity', 'INFO')}"
        )

        print(
            f"   Confidence : "
            f"{finding.get('confidence_level', 'N/A')}"
        )

        print(
            f"   Message    : "
            f"{finding.get('message', '')}"
        )

        if finding.get("reason"):

            print(
                f"   Reason     : "
                f"{finding['reason']}"
            )


def print_correlations(result):

    correlations = result.get(
        "correlations",
        []
    )

    print_section("DIAGNOSTIC CORRELATIONS")

    if not correlations:

        print(
            "No significant correlations "
            "identified."
        )

        return

    for number, correlation in enumerate(
        correlations,
        start=1
    ):

        print(
            f"{number}. {correlation}"
        )


def print_root_causes(result):

    candidates = result.get(
        "root_cause_candidates",
        []
    )

    primary = result.get(
        "primary_root_cause"
    )

    print_section("ROOT-CAUSE ANALYSIS")

    if not candidates:

        print(
            "No root-cause candidate meets "
            "the current evidence threshold."
        )

        print(
            "The system detected findings, "
            "but will not guess a root cause "
            "without sufficient evidence."
        )

        return

    for number, candidate in enumerate(
        candidates,
        start=1
    ):

        print(
            f"{number}. "
            f"{candidate.get('cause', 'Unknown cause')}"
        )

        print(
            f"   Category          : "
            f"{candidate.get('category', 'SYSTEM')}"
        )

        print(
            f"   Confidence        : "
            f"{candidate.get('confidence', 'N/A')}"
        )

        print(
            f"   Confidence Level  : "
            f"{candidate.get('confidence_level', 'N/A')}"
        )

        print(
            f"   Reason            : "
            f"{candidate.get('reason', '')}"
        )

        evidence = candidate.get(
            "evidence",
            []
        )

        if evidence:

            print(
                "   Evidence:"
            )

            for item in evidence:

                print(
                    f"      - {item}"
                )

    print()

    print("PRIMARY ROOT CAUSE")
    print("------------------------------------------")

    if primary:

        print(
            f"Cause      : "
            f"{primary.get('cause', 'Unknown')}"
        )

        print(
            f"Category   : "
            f"{primary.get('category', 'SYSTEM')}"
        )

        print(
            f"Confidence : "
            f"{primary.get('confidence', 'N/A')}"
        )

        print(
            f"Level      : "
            f"{primary.get('confidence_level', 'N/A')}"
        )

        print(
            f"Reason     : "
            f"{primary.get('reason', '')}"
        )

    else:

        print(
            "No primary root cause selected."
        )


def print_recommendations(diagnosis):

    recommendations = diagnosis.get(
        "recommendations",
        []
    )

    print_section("RECOMMENDATIONS")

    if not recommendations:

        print(
            "No recommendations generated."
        )

        return

    for number, recommendation in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"{number}. "
            f"{recommendation.get('category', 'SYSTEM')}"
        )

        print(
            f"   Severity      : "
            f"{recommendation.get('severity', 'INFO')}"
        )

        print(
            f"   Recommendation: "
            f"{recommendation.get('recommendation', '')}"
        )


def main():

    app = TechnicianApp()

    print("==========================================")
    print("       WINDOWS TECHNICIAN v0.6")
    print("       INTELLIGENT DIAGNOSTICS")
    print("==========================================")
    print()

    print("Running system diagnostics...")
    print("Collecting evidence...")
    print("Analyzing system state...")
    print("Evaluating diagnostic intelligence...")
    print("Please wait...")

    result = app.run_diagnostics()

    diagnosis = result["diagnosis"]

    # ==================================================
    # DIAGNOSTIC SUMMARY
    # ==================================================

    print_section("DIAGNOSTIC SUMMARY")

    print(
        f"Status          : "
        f"{diagnosis.get('status', 'UNKNOWN')}"
    )

    print(
        f"Total Findings  : "
        f"{diagnosis.get('total_findings', 0)}"
    )

    print(
        f"Recommendations : "
        f"{len(diagnosis.get('recommendations', []))}"
    )

    # ==================================================
    # FINDINGS
    # ==================================================

    print_findings(diagnosis)

    # ==================================================
    # CORRELATION
    # ==================================================

    print_correlations(result)

    # ==================================================
    # ROOT CAUSE
    # ==================================================

    print_root_causes(result)

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    print_recommendations(diagnosis)

    # ==================================================
    # COMPLETE
    # ==================================================

    print()
    print("==========================================")
    print("Diagnostic complete.")
    print("==========================================")


if __name__ == "__main__":

    main()
