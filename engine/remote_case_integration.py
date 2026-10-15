# ==========================================
# Windows Technician V1.0
# REMOTE CASE INTEGRATION
# ==========================================

from engine.diagnostic_case import DiagnosticCase
from engine.technician_workflow import TechnicianWorkflow


class RemoteCaseIntegration:
    """
    Integrates a remote DiagnosticCase into the
    canonical technician workflow.

    Remote cases use the same TechnicianWorkflow as
    local cases.

    This class does NOT:
    - create a remote workflow
    - create a second lifecycle
    - authorize remediation
    - execute remediation
    - verify remediation
    - create recovery operations
    """

    def __init__(self, case):
        if not isinstance(
            case,
            DiagnosticCase,
        ):
            raise ValueError(
                "RemoteCaseIntegration requires "
                "a DiagnosticCase."
            )

        if getattr(case, "origin", None) != "REMOTE":
            raise ValueError(
                "RemoteCaseIntegration requires "
                "a case with REMOTE origin."
            )

        self.case = case
        self.workflow = TechnicianWorkflow(
            case
        )

    @property
    def case_id(self):
        return self.case.case_id

    @property
    def machine_id(self):
        return self.case.machine_id

    @property
    def hostname(self):
        return self.case.hostname

    @property
    def session_id(self):
        return self.case.session_id

    @property
    def lifecycle_state(self):
        return self.case.lifecycle_state

    def start_investigation(self):
        """
        Enter the canonical investigation lifecycle.
        """

        self.workflow.start_investigation()

        return self.workflow
