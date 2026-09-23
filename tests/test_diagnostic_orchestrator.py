# ==========================================
# Windows Technician v0.6
# DIAGNOSTIC ORCHESTRATOR TESTS
# ==========================================

import pytest
from engine.observation import Observation
from engine.signal import Signal

from engine.diagnostic_orchestrator import DiagnosticOrchestrator


class FakeDiagnosticPipeline:

    def analyze(self):

        return {
            "status": "NORMAL",
            "findings": [],
            "recommendations": []
        }


def test_orchestrator_can_be_created():

    orchestrator = DiagnosticOrchestrator()

    assert orchestrator is not None


def test_orchestrator_starts_with_empty_state():

    orchestrator = DiagnosticOrchestrator()

    assert orchestrator.get_state() == {}


def test_orchestrator_can_run_diagnostic_pipeline():

    pipeline = FakeDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    assert result["status"] == "NORMAL"
    assert result["findings"] == []
    assert result["recommendations"] == []

def test_orchestrator_records_pipeline_failure():

    class FailingDiagnosticPipeline:

        def analyze(self):

            raise RuntimeError(
                "Diagnostic pipeline failed."
            )

    pipeline = FailingDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    try:

        orchestrator.run()

        assert False

    except RuntimeError as error:

        assert str(error) == (
            "Diagnostic pipeline failed."
        )

    state = orchestrator.get_state()

    assert state["status"] == "FAILED"
    assert state["error"] == (
        "Diagnostic pipeline failed."
    )


def test_orchestrator_stores_pipeline_result_in_diagnostic_case():

    pipeline = FakeDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert case is not None
    assert case.status == "NORMAL"
    assert case.findings == []
    assert case.recommendations == []

    assert result == {
        "status": "NORMAL",
        "findings": [],
        "recommendations": []
    }

def test_orchestrator_stores_complete_pipeline_result_in_case():

    class CompleteDiagnosticPipeline:

        def analyze(self):

            return {
                "status": "CRITICAL",

                "evidence": {
                    "CPU": {
                        "usage_percent": 97
                    }
                },

                "findings": [
                    {
                        "category": "CPU",
                        "severity": "CRITICAL",
                        "message": "High CPU usage."
                    }
                ],

                "correlations": [
                    {
                        "relationship": "CPU + MEMORY"
                    }
                ],

                "root_causes": [
                    {
                        "category": "CPU",
                        "cause": "CPU pressure"
                    }
                ],

                "recommendations": [
                    {
                        "category": "CPU",
                        "severity": "CRITICAL",
                        "message": "Investigate CPU usage."
                    }
                ]
            }

    pipeline = CompleteDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert result["status"] == "CRITICAL"

    assert case.status == "CRITICAL"

    assert case.evidence == {
        "CPU": {
            "usage_percent": 97
        }
    }

    assert case.findings == [
        {
            "category": "CPU",
            "severity": "CRITICAL",
            "message": "High CPU usage."
        }
    ]

    assert case.correlations == [
        {
            "relationship": "CPU + MEMORY"
        }
    ]

    assert case.root_causes == [
        {
            "category": "CPU",
            "cause": "CPU pressure"
        }
    ]

    assert case.recommendations == [
        {
            "category": "CPU",
            "severity": "CRITICAL",
            "message": "Investigate CPU usage."
        }
    ]

def test_orchestrator_handles_missing_optional_sections():

    class PartialDiagnosticPipeline:

        def analyze(self):

            return {
                "status": "WARNING",
                "findings": [
                    {
                        "category": "MEMORY",
                        "severity": "WARNING",
                        "message": "High memory usage."
                    }
                ]
            }

    pipeline = PartialDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert result["status"] == "WARNING"

    assert case.status == "WARNING"

    assert case.findings == [
        {
            "category": "MEMORY",
            "severity": "WARNING",
            "message": "High memory usage."
        }
    ]

    assert case.evidence == {}
    assert case.correlations == []
    assert case.root_causes == []
    assert case.recommendations == []

def test_orchestrator_replaces_previous_case_on_new_run():

    class ChangingDiagnosticPipeline:

        def __init__(self):

            self.run_count = 0

        def analyze(self):

            self.run_count += 1

            if self.run_count == 1:

                return {
                    "status": "WARNING",
                    "findings": [
                        {
                            "category": "CPU",
                            "severity": "WARNING",
                            "message": "First diagnosis."
                        }
                    ],
                    "recommendations": []
                }

            return {
                "status": "CRITICAL",
                "findings": [
                    {
                        "category": "MEMORY",
                        "severity": "CRITICAL",
                        "message": "Second diagnosis."
                    }
                ],
                "recommendations": []
            }

    pipeline = ChangingDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    first_result = orchestrator.run()

    first_case = orchestrator.get_case()

    assert first_result["status"] == "WARNING"
    assert first_case.status == "WARNING"

    assert first_case.findings == [
        {
            "category": "CPU",
            "severity": "WARNING",
            "message": "First diagnosis."
        }
    ]

    second_result = orchestrator.run()

    second_case = orchestrator.get_case()

    assert second_result["status"] == "CRITICAL"
    assert second_case.status == "CRITICAL"

    assert second_case.findings == [
        {
            "category": "MEMORY",
            "severity": "CRITICAL",
            "message": "Second diagnosis."
        }
    ]

    assert second_case is not first_case

def test_orchestrator_preserves_last_successful_case_when_next_run_fails():

    class FailingAfterSuccessPipeline:

        def __init__(self):

            self.run_count = 0

        def analyze(self):

            self.run_count += 1

            if self.run_count == 1:

                return {
                    "status": "WARNING",
                    "findings": [
                        {
                            "category": "CPU",
                            "severity": "WARNING",
                            "message": "Previous successful diagnosis."
                        }
                    ],
                    "recommendations": []
                }

            raise RuntimeError(
                "Second diagnostic run failed."
            )

    pipeline = FailingAfterSuccessPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    orchestrator.run()

    successful_case = orchestrator.get_case()

    try:

        orchestrator.run()

        assert False

    except RuntimeError as error:

        assert str(error) == (
            "Second diagnostic run failed."
        )

    current_case = orchestrator.get_case()

    assert current_case.status == successful_case.status
    assert current_case.findings == successful_case.findings

    assert current_case.status == "WARNING"

    assert current_case.findings == [
        {
            "category": "CPU",
            "severity": "WARNING",
            "message": "Previous successful diagnosis."
        }
    ]

    state = orchestrator.get_state()

    assert state["status"] == "FAILED"

    assert state["error"] == (
        "Second diagnostic run failed."
    )

def test_orchestrator_handles_pipeline_returning_none():

    class EmptyDiagnosticPipeline:

        def analyze(self):

            return None

    pipeline = EmptyDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    assert result == {}

    assert orchestrator.get_state() == {}

    case = orchestrator.get_case()

    assert case is not None
    assert case.status == "NORMAL"
    assert case.findings == []
    assert case.recommendations == []

def test_orchestrator_handles_pipeline_returning_non_dict():

    class InvalidDiagnosticPipeline:

        def analyze(self):

            return "invalid diagnostic result"

    pipeline = InvalidDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    assert result == {}

    assert orchestrator.get_state() == {}

    case = orchestrator.get_case()

    assert case is not None
    assert case.status == "NORMAL"
    assert case.findings == []
    assert case.recommendations == []

def test_orchestrator_preserves_complete_pipeline_result_in_state():

    complete_result = {
        "status": "CRITICAL",
        "evidence": {
            "cpu": 95.0,
            "memory": 91.0
        },
        "findings": [
            {
                "category": "CPU",
                "severity": "CRITICAL",
                "message": "CPU pressure detected."
            }
        ],
        "correlations": [
            {
                "relationship": "CPU + MEMORY",
                "confidence": 0.90
            }
        ],
        "root_causes": [
            {
                "cause": "High resource usage",
                "confidence": 0.85
            }
        ],
        "recommendations": [
            "Investigate high CPU usage."
        ]
    }

    class CompleteDiagnosticPipeline:

        def analyze(self):

            return complete_result

    pipeline = CompleteDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    assert result == complete_result

    assert orchestrator.get_state() == complete_result

    assert orchestrator.get_state()["evidence"] == {
        "cpu": 95.0,
        "memory": 91.0
    }

    assert orchestrator.get_state()["correlations"] == [
        {
            "relationship": "CPU + MEMORY",
            "confidence": 0.90
        }
    ]

    assert orchestrator.get_state()["root_causes"] == [
        {
            "cause": "High resource usage",
            "confidence": 0.85
        }
    ]

def test_orchestrator_maps_missing_sections_to_case_defaults():

    class MinimalDiagnosticPipeline:

        def analyze(self):

            return {
                "status": "WARNING"
            }

    pipeline = MinimalDiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert result == {
        "status": "WARNING"
    }

    assert case.status == "WARNING"
    assert case.evidence == {}
    assert case.findings == []
    assert case.correlations == []
    assert case.root_causes == []
    assert case.recommendations == []

def test_orchestrator_case_does_not_share_mutable_collections_with_result():

    pipeline_result = {
        "status": "WARNING",
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "recommendations": [
            "Investigate CPU usage."
        ]
    }

    class DiagnosticPipeline:

        def analyze(self):

            return pipeline_result

    pipeline = DiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    # The case should contain the same diagnostic content.
    assert case.findings == result["findings"]
    assert case.recommendations == result["recommendations"]

    # But the case should own its collections.
    assert case.findings is not result["findings"]
    assert case.recommendations is not result["recommendations"]

def test_orchestrator_case_does_not_share_nested_finding_data():

    pipeline_result = {
        "status": "WARNING",
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "recommendations": [
            {
                "action": "Investigate CPU usage."
            }
        ]
    }

    class DiagnosticPipeline:

        def analyze(self):

            return pipeline_result

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert case.findings == result["findings"]
    assert case.recommendations == result["recommendations"]

    # Nested objects should be independently owned.
    assert case.findings[0] is not result["findings"][0]
    assert case.recommendations[0] is not result["recommendations"][0]

def test_orchestrator_maps_complete_engine_result_into_case():

    pipeline_result = {
        "evidence": {
            "CPU": {
                "usage_percent": 95
            }
        },
        "status": "CRITICAL",
        "total_findings": 1,
        "findings": [
            {
                "category": "CPU",
                "severity": "CRITICAL",
                "message": "Critical CPU utilization."
            }
        ],
        "correlations": [
            {
                "categories": ["CPU", "PROCESS"],
                "message": "CPU pressure is associated with process activity."
            }
        ],
        "root_causes": [
            {
                "category": "PROCESS",
                "message": "A process is contributing significantly to CPU usage."
            }
        ],
        "recommendations": [
            {
                "category": "CPU",
                "severity": "CRITICAL",
                "action": "Investigate high CPU usage."
            }
        ]
    }

    class DiagnosticPipeline:

        def analyze(self):

            return pipeline_result

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert case.evidence == pipeline_result["evidence"]
    assert case.status == pipeline_result["status"]
    assert case.findings == pipeline_result["findings"]
    assert case.correlations == pipeline_result["correlations"]
    assert case.root_causes == pipeline_result["root_causes"]
    assert case.recommendations == pipeline_result["recommendations"]

def test_orchestrator_does_not_share_nested_correlations_or_root_causes_with_result():

    pipeline_result = {
        "status": "WARNING",
        "evidence": {
            "CPU": {
                "usage_percent": 90
            }
        },
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "correlations": [
            {
                "type": "CPU_MEMORY",
                "strength": "HIGH",
                "details": {
                    "cpu": 90,
                    "memory": 85
                }
            }
        ],
        "root_causes": [
            {
                "category": "SYSTEM",
                "severity": "WARNING",
                "details": {
                    "source": "resource_pressure"
                }
            }
        ],
        "recommendations": []
    }

    class DiagnosticPipeline:

        def analyze(self):

            return pipeline_result

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert case.correlations == result["correlations"]
    assert case.root_causes == result["root_causes"]

    assert case.correlations is not result["correlations"]
    assert case.root_causes is not result["root_causes"]

    assert (
        case.correlations[0]
        is not result["correlations"][0]
    )

    assert (
        case.root_causes[0]
        is not result["root_causes"][0]
    )

    assert (
        case.correlations[0]["details"]
        is not result["correlations"][0]["details"]
    )

    assert (
        case.root_causes[0]["details"]
        is not result["root_causes"][0]["details"]
    )

def test_orchestrator_case_mutation_does_not_modify_pipeline_result():

    pipeline_result = {
        "status": "WARNING",
        "evidence": {
            "CPU": {
                "usage_percent": 90
            }
        },
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "correlations": [
            {
                "type": "CPU_MEMORY",
                "strength": "HIGH",
                "details": {
                    "cpu": 90
                }
            }
        ],
        "root_causes": [
            {
                "category": "SYSTEM",
                "severity": "WARNING",
                "details": {
                    "source": "resource_pressure"
                }
            }
        ],
        "recommendations": []
    }

    class DiagnosticPipeline:

        def analyze(self):

            return pipeline_result

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    case = orchestrator.get_case()

    case.correlations[0]["details"]["cpu"] = 100
    case.root_causes[0]["details"]["source"] = "modified"

    assert (
        pipeline_result["correlations"][0]["details"]["cpu"]
        == 90
    )

    assert (
        pipeline_result["root_causes"][0]["details"]["source"]
        == "resource_pressure"
    )

def test_orchestrator_new_run_creates_independent_case_data():

    first_result = {
        "status": "WARNING",
        "evidence": {
            "CPU": {
                "usage_percent": 90
            }
        },
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "correlations": [
            {
                "type": "CPU_MEMORY",
                "strength": "HIGH"
            }
        ],
        "root_causes": [
            {
                "category": "SYSTEM",
                "severity": "WARNING"
            }
        ],
        "recommendations": []
    }

    second_result = {
        "status": "NORMAL",
        "evidence": {
            "CPU": {
                "usage_percent": 30
            }
        },
        "findings": [],
        "correlations": [],
        "root_causes": [],
        "recommendations": []
    }

    class DiagnosticPipeline:

        def __init__(self):
            self.results = [
                first_result,
                second_result
            ]

        def analyze(self):

            return self.results.pop(0)

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    first_case = orchestrator.get_case()

    orchestrator.run()

    second_case = orchestrator.get_case()

    assert first_case is not second_case

    assert first_case.findings != second_case.findings
    assert first_case.correlations != second_case.correlations
    assert first_case.root_causes != second_case.root_causes

    assert second_case.findings == []
    assert second_case.correlations == []
    assert second_case.root_causes == []

def test_orchestrator_failed_run_preserves_previous_case_data():

    successful_result = {
        "status": "WARNING",
        "evidence": {
            "CPU": {
                "usage_percent": 90
            }
        },
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "correlations": [
            {
                "type": "CPU_MEMORY",
                "strength": "HIGH"
            }
        ],
        "root_causes": [
            {
                "category": "SYSTEM",
                "severity": "WARNING"
            }
        ],
        "recommendations": [
            {
                "action": "Investigate CPU usage."
            }
        ]
    }

    class DiagnosticPipeline:

        def __init__(self):
            self.run_count = 0

        def analyze(self):

            self.run_count += 1

            if self.run_count == 1:
                return successful_result

            raise RuntimeError("Pipeline failure.")

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    case_before_failure = orchestrator.get_case()

    evidence_before = case_before_failure.evidence
    findings_before = case_before_failure.findings
    correlations_before = case_before_failure.correlations
    root_causes_before = case_before_failure.root_causes
    recommendations_before = case_before_failure.recommendations
    status_before = case_before_failure.status

    with pytest.raises(RuntimeError):
        orchestrator.run()

    case_after_failure = orchestrator.get_case()

    assert case_after_failure.evidence == evidence_before
    assert case_after_failure.findings == findings_before
    assert case_after_failure.correlations == correlations_before
    assert case_after_failure.root_causes == root_causes_before
    assert case_after_failure.recommendations == recommendations_before
    assert case_after_failure.status == status_before

def test_orchestrator_state_does_not_share_mutable_data_with_pipeline_result():

    pipeline_result = {
        "status": "WARNING",
        "evidence": {
            "CPU": {
                "usage_percent": 90
            }
        },
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "correlations": [
            {
                "type": "CPU_MEMORY",
                "details": {
                    "cpu": 90
                }
            }
        ],
        "root_causes": [
            {
                "category": "SYSTEM",
                "details": {
                    "source": "resource_pressure"
                }
            }
        ],
        "recommendations": []
    }

    class DiagnosticPipeline:

        def analyze(self):

            return pipeline_result

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    result = orchestrator.run()

    state = orchestrator.get_state()

    assert state == result

    assert state is not result

    # Mutate the pipeline result after the run.

    result["evidence"]["CPU"]["usage_percent"] = 100

    result["findings"][0]["message"] = "Modified finding."

    result["correlations"][0]["details"]["cpu"] = 100

    result["root_causes"][0]["details"]["source"] = "modified"

    # Orchestrator state must remain unchanged.

    assert state["evidence"]["CPU"]["usage_percent"] == 90

    assert (
        state["findings"][0]["message"]
        == "CPU pressure detected."
    )

    assert (
        state["correlations"][0]["details"]["cpu"]
        == 90
    )

    assert (
        state["root_causes"][0]["details"]["source"]
        == "resource_pressure"
    )

def test_orchestrator_state_mutation_does_not_modify_case():

    pipeline_result = {
        "status": "WARNING",
        "evidence": {
            "CPU": {
                "usage_percent": 90
            }
        },
        "findings": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "CPU pressure detected."
            }
        ],
        "correlations": [
            {
                "type": "CPU_MEMORY",
                "details": {
                    "strength": "HIGH"
                }
            }
        ],
        "root_causes": [
            {
                "category": "SYSTEM",
                "message": "Resource pressure detected."
            }
        ],
        "recommendations": [
            {
                "category": "CPU",
                "severity": "WARNING",
                "message": "Investigate CPU utilization."
            }
        ]
    }

    class DiagnosticPipeline:

        def analyze(self):
            return pipeline_result

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    state = orchestrator.get_state()
    case = orchestrator.get_case()

    # Mutate orchestrator state.

    state["evidence"]["CPU"]["usage_percent"] = 100

    state["findings"][0]["message"] = "Modified state finding."

    state["correlations"][0]["details"]["strength"] = "CRITICAL"

    state["root_causes"][0]["message"] = "Modified state root cause."

    state["recommendations"][0]["message"] = "Modified state recommendation."

    # DiagnosticCase must remain unchanged.

    assert (
        case.evidence["CPU"]["usage_percent"]
        == 90
    )

    assert (
        case.findings[0]["message"]
        == "CPU pressure detected."
    )

    assert (
        case.correlations[0]["details"]["strength"]
        == "HIGH"
    )

    assert (
        case.root_causes[0]["message"]
        == "Resource pressure detected."
    )

    assert (
        case.recommendations[0]["message"]
        == "Investigate CPU utilization."
    )

def test_orchestrator_get_state_returns_independent_snapshot():

    class DiagnosticPipeline:

        def analyze(self):

            return {
                "status": "WARNING",
                "evidence": {
                    "CPU": {
                        "usage_percent": 90
                    }
                },
                "findings": [],
                "correlations": [],
                "root_causes": [],
                "recommendations": []
            }

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    state = orchestrator.get_state()

    state["status"] = "CRITICAL"

    state["evidence"]["CPU"]["usage_percent"] = 100

    internal_state = orchestrator.get_state()

    assert internal_state["status"] == "WARNING"

    assert (
        internal_state["evidence"]["CPU"]["usage_percent"]
        == 90
    )

def test_orchestrator_get_case_returns_independent_snapshot():

    class DiagnosticPipeline:

        def analyze(self):

            return {
                "status": "WARNING",
                "evidence": {
                    "CPU": {
                        "usage_percent": 90
                    }
                },
                "findings": [
                    {
                        "category": "CPU",
                        "severity": "WARNING",
                        "message": "CPU pressure detected."
                    }
                ],
                "correlations": [],
                "root_causes": [],
                "recommendations": []
            }

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    case = orchestrator.get_case()

    case.evidence["CPU"]["usage_percent"] = 100
    case.findings[0]["message"] = "Modified case."

    internal_case = orchestrator.get_case()

    assert (
        internal_case.evidence["CPU"]["usage_percent"]
        == 90
    )

    assert (
        internal_case.findings[0]["message"]
        == "CPU pressure detected."
    )

def test_orchestrator_case_does_not_share_nested_data_with_state():

    class DiagnosticPipeline:

        def analyze(self):

            return {
                "status": "WARNING",
                "evidence": {
                    "CPU": {
                        "usage_percent": 90
                    }
                },
                "findings": [
                    {
                        "category": "CPU",
                        "severity": "WARNING",
                        "message": "CPU pressure detected."
                    }
                ],
                "correlations": [],
                "root_causes": [],
                "recommendations": []
            }

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    state = orchestrator.get_state()

    state["evidence"]["CPU"]["usage_percent"] = 100
    state["findings"][0]["message"] = "Modified state."

    case = orchestrator.get_case()

    assert (
        case.evidence["CPU"]["usage_percent"]
        == 90
    )

    assert (
        case.findings[0]["message"]
        == "CPU pressure detected."
    )

def test_orchestrator_failed_run_records_failure_state():

    class DiagnosticPipeline:

        def __init__(self):
            self.fail = False

        def analyze(self):

            if self.fail:
                raise RuntimeError("Pipeline failure.")

            return {
                "status": "WARNING",
                "evidence": {
                    "CPU": {
                        "usage_percent": 90
                    }
                },
                "findings": [],
                "correlations": [],
                "root_causes": [],
                "recommendations": []
            }

    pipeline = DiagnosticPipeline()

    orchestrator = DiagnosticOrchestrator(
        pipeline=pipeline
    )

    orchestrator.run()

    previous_case = orchestrator.get_case()

    pipeline.fail = True

    with pytest.raises(RuntimeError) as error:
        orchestrator.run()

    assert str(error.value) == "Pipeline failure."

    current_state = orchestrator.get_state()

    assert current_state["status"] == "FAILED"
    assert current_state["error"] == "Pipeline failure."

    current_case = orchestrator.get_case()

    assert current_case.status == previous_case.status
    assert current_case.evidence == previous_case.evidence
    assert current_case.findings == previous_case.findings
    assert current_case.correlations == previous_case.correlations
    assert current_case.root_causes == previous_case.root_causes
    assert current_case.recommendations == previous_case.recommendations

def test_orchestrator_maps_observations_and_signals_into_case():

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    class DiagnosticPipeline:

        def analyze(self):

            return {
                "status": "WARNING",
                "observations": [observation],
                "signals": [signal],
                "findings": [],
                "recommendations": [],
            }

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    result = orchestrator.run()

    case = orchestrator.get_case()

    assert len(result["observations"]) == 1
    assert result["observations"][0].source == "memory"
    assert result["observations"][0].subject == "system_memory"
    assert result["observations"][0].attribute == "usage_percent"
    assert result["observations"][0].value == 88

    assert len(result["signals"]) == 1
    assert result["signals"][0].signal_type == "HIGH_MEMORY_USAGE"
    assert result["signals"][0].source == "memory"
    assert result["signals"][0].subject == "system_memory"
    assert result["signals"][0].attribute == "usage_percent"
    assert result["signals"][0].value == 88

    assert len(case.observations) == 1
    assert case.observations[0].source == "memory"
    assert case.observations[0].subject == "system_memory"
    assert case.observations[0].attribute == "usage_percent"
    assert case.observations[0].value == 88

    assert len(case.signals) == 1
    assert case.signals[0].signal_type == "HIGH_MEMORY_USAGE"
    assert case.signals[0].source == "memory"
    assert case.signals[0].subject == "system_memory"
    assert case.signals[0].attribute == "usage_percent"
    assert case.signals[0].value == 88


def test_orchestrator_case_does_not_share_observations_or_signals_with_pipeline_result():

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    pipeline_result = {
        "status": "WARNING",
        "observations": [observation],
        "signals": [signal],
        "findings": [],
        "recommendations": [],
    }

    class DiagnosticPipeline:

        def analyze(self):

            return pipeline_result

    orchestrator = DiagnosticOrchestrator(
        pipeline=DiagnosticPipeline()
    )

    orchestrator.run()

    case = orchestrator.get_case()

    assert case.observations[0] is not pipeline_result["observations"][0]
    assert case.signals[0] is not pipeline_result["signals"][0]

    assert case.observations[0].value == 88
    assert case.signals[0].value == 88
