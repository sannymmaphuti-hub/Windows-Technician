from copy import deepcopy

from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
)


class NetworkDiagnosticCaseAdapter:
    """
    Converts a NetworkDiagnosticCase into an application-facing
    result section.

    This adapter does not perform diagnostic reasoning.

    It does not create:
    - observations
    - signals
    - findings
    - correlations
    - root-cause candidates
    - evaluations
    - confidences
    - explanations
    - recommendations

    It only translates the already-computed case into an
    application result representation.
    """

    def to_application_result(self, case):
        if not isinstance(
            case,
            NetworkDiagnosticCase,
        ):
            raise ValueError(
                "case must be a NetworkDiagnosticCase."
            )

        return {
            "network_diagnostic_case": {
                "observations": deepcopy(
                    case.observations
                ),
                "signals": deepcopy(
                    case.signals
                ),
                "findings": deepcopy(
                    case.findings
                ),
                "correlations": deepcopy(
                    case.correlations
                ),
                "candidates": deepcopy(
                    case.candidates
                ),
                "evaluations": deepcopy(
                    case.evaluations
                ),
                "primary_cause": deepcopy(
                    case.primary_cause
                ),
                "confidences": deepcopy(
                    case.confidences
                ),
                "explanations": deepcopy(
                    case.explanations
                ),
                "recommendations": deepcopy(
                    case.recommendations
                ),
            }
        }