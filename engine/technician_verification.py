from engine.remediation_verifier import RemediationVerifier
from engine.remediation_result import RemediationResult
from engine.technician_workflow import (
    TechnicianWorkflow,
    WorkflowState,
)


class TechnicianVerification:

    def __init__(self, workflow, verifier=None):
        if not isinstance(workflow, TechnicianWorkflow):
            raise ValueError(
                "TechnicianVerification requires a TechnicianWorkflow."
            )

        self._workflow = workflow
        self._verifier = verifier or RemediationVerifier()

        self._result = None
        self._verification_result = None
        self._active = False
        self._complete = False

    @property
    def workflow(self):
        return self._workflow

    @property
    def result(self):
        return self._result

    @property
    def verification_result(self):
        return self._verification_result

    @property
    def is_active(self):
        return self._active

    @property
    def is_complete(self):
        return self._complete

    def start(self):
        if self._complete:
            raise ValueError(
                "Completed verification cannot be restarted."
            )

        if self._active:
            raise ValueError(
                "Verification is already active."
            )

        if self._workflow.state is not WorkflowState.VERIFYING:
            raise ValueError(
                "Verification can only start while workflow is VERIFYING."
            )

        self._active = True

    def verify(self, result, expected, observed=None):
        if not self._active:
            raise ValueError(
                "Verification must be active before verification."
            )

        if not isinstance(result, RemediationResult):
            raise ValueError(
                "Verification requires a RemediationResult."
            )

        if result.execution_status != "EXECUTED":
            raise ValueError(
                "Only successfully executed remediation can be verified."
            )

        if observed is None:
            raise ValueError(
                "Observed condition is required for verification."
            )

        verification_result = self._verifier.verify(
            expected=expected,
            observed=observed,
            action_id=result.action_id,
        )

        self._result = result
        self._verification_result = verification_result
        self._active = False

        if verification_result.verification_result["verified"]:
            self._complete = True
            self._workflow.resolve()
            return True

        self._workflow.start_remediation()
        return False