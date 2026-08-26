# ==========================================
# WINDOWS TECHNICIAN v0.1
# APPLICATION ENTRY POINT
# ==========================================

from pathlib import Path

from application.technician import Technician

class TechnicianApp:

    def __init__(self):

        self.technician = Technician()

    def run_diagnostics(self):

        return self.technician.diagnose()

    def get_status(self):

        return self.technician.get_status()
    
    def get_primary_issue(self):

        return self.technician.get_primary_issue()

    def get_report(self):

        return self.technician.get_report()

    def save_report(self):

        report = self.get_report()

        reports_directory = Path("reports")

        reports_directory.mkdir(
            exist_ok=True
        )

        report_path = reports_directory / "technician_report.txt"

        report_path.write_text(
            report,
            encoding="utf-8"
        )

        return str(report_path)


def main():

    app = TechnicianApp()

    print("==========================================")
    print("       WINDOWS TECHNICIAN v0.1")
    print("==========================================")
    print()

    print("Running system diagnostics...")
    print("Please wait...")
    print()

    result = app.run_diagnostics()

    diagnosis = result["diagnosis"]

    # ==================================================
    # DIAGNOSTIC SUMMARY
    # ==================================================

    print("DIAGNOSTIC RESULT")
    print("------------------------------------------")

    print(
        f"Status         : "
        f"{diagnosis['status']}"
    )

    print(
        f"Total Findings : "
        f"{diagnosis['total_findings']}"
    )

    print(
        f"Recommendations: "
        f"{len(diagnosis['recommendations'])}"
    )

    # ==================================================
    # FINDINGS
    # ==================================================

    if diagnosis["findings"]:

        print()
        print("FINDINGS")
        print("------------------------------------------")

        for number, finding in enumerate(
            diagnosis["findings"],
            start=1
        ):

            print(
                f"{number}. "
                f"{finding['category']}"
            )

            print(
                f"   Severity   : "
                f"{finding['severity']}"
            )

            print(
                f"   Confidence : "
                f"{finding.get('confidence_level', 'N/A')}"
            )

            print(
                f"   Message    : "
                f"{finding['message']}"
            )

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    if diagnosis["recommendations"]:

        print()
        print("RECOMMENDATIONS")
        print("------------------------------------------")

        for number, recommendation in enumerate(
            diagnosis["recommendations"],
            start=1
        ):

            print(
                f"{number}. "
                f"{recommendation['category']}"
            )

            print(
                f"   Severity      : "
                f"{recommendation['severity']}"
            )

            print(
                f"   Recommendation: "
                f"{recommendation['recommendation']}"
            )

    print()
    print("==========================================")
    print("Diagnostic complete.")
    print("==========================================")

if __name__ == "__main__":
    main()