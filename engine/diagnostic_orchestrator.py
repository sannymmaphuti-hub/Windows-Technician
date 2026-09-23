# ==========================================
# Windows Technician v0.6
# DIAGNOSTIC ORCHESTRATOR
# ==========================================

import copy

from engine.diagnostic_case import DiagnosticCase
from engine.factory import create_diagnostic_engine


class DiagnosticOrchestrator:

    def __init__(self, pipeline=None):

        self.pipeline = (
            pipeline
            if pipeline is not None
            else create_diagnostic_engine()
        )

        self.state = {}
        self.case = DiagnosticCase()

    def get_state(self):

        return copy.deepcopy(self.state)

    def get_case(self):

        return copy.deepcopy(self.case)

    def run(self):

        if self.pipeline is None:

            raise ValueError(
                "Diagnostic pipeline is required."
            )

        try:

            result = self.pipeline.analyze()

            # --------------------------------------------------
            # Invalid pipeline results
            #
            # Preserve the existing contract:
            # None / non-dict results produce an empty result.
            # --------------------------------------------------

            if not isinstance(result, dict):

                return {}

            # --------------------------------------------------
            # Preserve the pipeline result exactly.
            #
            # The returned result and orchestrator state must
            # represent the pipeline's original output.
            #
            # Do NOT normalize or restructure this dictionary.
            # --------------------------------------------------

            pipeline_result = copy.deepcopy(result)

            # --------------------------------------------------
            # Support both:
            #
            # 1. Current v0.6 top-level sections
            #
            # 2. Older nested "diagnosis" sections
            #
            # DiagnosticCase receives whichever representation
            # is available.
            # --------------------------------------------------

            diagnosis = result.get(
                "diagnosis",
                {}
            )

            if not isinstance(diagnosis, dict):

                diagnosis = {}

            def get_section(
                name,
                default
            ):

                # Prefer the current top-level structure.

                if name in result:

                    return copy.deepcopy(
                        result[name]
                    )

                # Fall back to nested diagnosis.

                if name in diagnosis:

                    return copy.deepcopy(
                        diagnosis[name]
                    )

                # Otherwise use the DiagnosticCase default.

                return copy.deepcopy(
                    default
                )

            # --------------------------------------------------
            # Build a completely independent DiagnosticCase.
            # --------------------------------------------------

            new_case = DiagnosticCase()

            new_case.set_observations(
                get_section("observations", [])
            )

            new_case.set_signals(
                get_section("signals", [])
            )

            new_case.set_evidence(get_section("evidence", {}))

            new_case.set_findings(
                get_section(
                    "findings",
                    []
                )
            )

            new_case.set_correlations(
                get_section(
                    "correlations",
                    []
                )
            )

            new_case.set_root_causes(
                get_section(
                    "root_causes",
                    []
                )
            )

            new_case.set_recommendations(
                get_section(
                    "recommendations",
                    []
                )
            )

            # --------------------------------------------------
            # v0.6 INTELLIGENCE DATA
            # --------------------------------------------------

            new_case.set_process_intelligence(
                copy.deepcopy(
                    result.get(
                        "process_intelligence"
                    )
                )
            )

            new_case.set_memory_intelligence(
                copy.deepcopy(
                    result.get(
                        "memory_intelligence"
                    )
                )
            )

            new_case.set_memory_history(
                copy.deepcopy(
                    result.get(
                        "memory_history",
                        []
                    )
                )
            )

            new_case.set_memory_trend_intelligence(
                copy.deepcopy(
                    result.get(
                        "memory_trend_intelligence"
                    )
                )
            )

            new_case.set_memory_temporal_intelligence(
                copy.deepcopy(
                    result.get(
                        "memory_temporal_intelligence"
                    )
                )
            )

            new_case.set_memory_diagnostic_intelligence(
                copy.deepcopy(
                    result.get(
                        "memory_diagnostic_intelligence"
                    )
                )
            )

            new_case.set_root_cause_candidates(
                copy.deepcopy(
                    result.get(
                        "root_cause_candidates",
                        []
                    )
                )
            )

            new_case.set_primary_root_cause(
                copy.deepcopy(
                    result.get(
                        "primary_root_cause"
                    )
                )
            )

            # --------------------------------------------------
            # Status
            #
            # Current v0.6:
            #     result["status"]
            #
            # Older nested structure:
            #     result["diagnosis"]["status"]
            # --------------------------------------------------

            if "status" in result:

                new_case.status = copy.deepcopy(
                    result["status"]
                )

            elif "status" in diagnosis:

                new_case.status = copy.deepcopy(
                    diagnosis["status"]
                )

            else:

                new_case.status = "NORMAL"

            # --------------------------------------------------
            # Commit successful run.
            #
            # State and case are only replaced after the entire
            # pipeline-to-case transformation succeeds.
            # --------------------------------------------------

            new_state = copy.deepcopy(
                pipeline_result
            )

            self.state = new_state
            self.case = new_case

            return copy.deepcopy(
                pipeline_result
            )

        except Exception as error:

            # --------------------------------------------------
            # Failed run behavior
            #
            # IMPORTANT:
            #
            # - Preserve the previous successful DiagnosticCase.
            # - Record the failure in orchestrator state.
            # - Re-raise the original exception unchanged.
            #
            # This means:
            #
            #       state.status == "FAILED"
            #
            # while:
            #
            #       case
            #
            # still represents the last successful diagnosis.
            # --------------------------------------------------

            self.state = {
                "status": "FAILED",
                "error": str(error)
            }

            raise
