from engine.network_diagnostic_case_synthesis import (
    NetworkDiagnosticCase,
)
from engine.network_diagnostic_case_adapter import (
    NetworkDiagnosticCaseAdapter,
)


def test_network_case_can_be_adapted_for_application():
    network_case = NetworkDiagnosticCase(
        observations=[],
        signals=[],
        findings=[],
        correlations=[],
        candidates=[],
        evaluations=[],
        primary_cause=None,
        confidences=[],
        explanations=[],
        recommendations=[],
    )

    adapter = NetworkDiagnosticCaseAdapter()

    result = adapter.to_application_result(
        network_case
    )

    assert isinstance(result, dict)
    assert "network_diagnostic_case" in result


def test_network_case_adapter_preserves_case():
    network_case = NetworkDiagnosticCase(
        observations=["observation"],
        signals=["signal"],
        findings=["finding"],
        correlations=[],
        candidates=["candidate"],
        evaluations=["evaluation"],
        primary_cause="primary",
        confidences=["confidence"],
        explanations=["explanation"],
        recommendations=["recommendation"],
    )

    adapter = NetworkDiagnosticCaseAdapter()

    result = adapter.to_application_result(
        network_case
    )

    assert (
        result["network_diagnostic_case"]
        is not network_case
    )

    assert result["network_diagnostic_case"][
        "observations"
    ] == ["observation"]

    assert result["network_diagnostic_case"][
        "signals"
    ] == ["signal"]

    assert result["network_diagnostic_case"][
        "findings"
    ] == ["finding"]

    assert result["network_diagnostic_case"][
        "candidates"
    ] == ["candidate"]

    assert result["network_diagnostic_case"][
        "evaluations"
    ] == ["evaluation"]

    assert result["network_diagnostic_case"][
        "primary_cause"
    ] == "primary"

    assert result["network_diagnostic_case"][
        "confidences"
    ] == ["confidence"]

    assert result["network_diagnostic_case"][
        "explanations"
    ] == ["explanation"]

    assert result["network_diagnostic_case"][
        "recommendations"
    ] == ["recommendation"]

def test_network_case_adapter_rejects_invalid_case():
    adapter = NetworkDiagnosticCaseAdapter()

    try:
        adapter.to_application_result({})
    except ValueError as error:
        assert str(error) == (
            "case must be a NetworkDiagnosticCase."
        )
    else:
        raise AssertionError(
            "Expected ValueError for invalid case."
        )


def test_network_case_adapter_does_not_mutate_case():
    network_case = NetworkDiagnosticCase(
        observations=["observation"],
        signals=["signal"],
        findings=["finding"],
        correlations=[],
        candidates=["candidate"],
        evaluations=["evaluation"],
        primary_cause="primary",
        confidences=["confidence"],
        explanations=["explanation"],
        recommendations=["recommendation"],
    )

    adapter = NetworkDiagnosticCaseAdapter()

    result = adapter.to_application_result(
        network_case
    )

    result["network_diagnostic_case"][
        "observations"
    ].append("changed")

    result["network_diagnostic_case"][
        "recommendations"
    ].append("changed")

    assert network_case.observations == [
        "observation"
    ]

    assert network_case.recommendations == [
        "recommendation"
    ]


def test_network_case_adapter_preserves_empty_case():
    network_case = NetworkDiagnosticCase(
        observations=[],
        signals=[],
        findings=[],
        correlations=[],
        candidates=[],
        evaluations=[],
        primary_cause=None,
        confidences=[],
        explanations=[],
        recommendations=[],
    )

    adapter = NetworkDiagnosticCaseAdapter()

    result = adapter.to_application_result(
        network_case
    )

    application_case = result[
        "network_diagnostic_case"
    ]

    assert application_case["observations"] == []
    assert application_case["signals"] == []
    assert application_case["findings"] == []
    assert application_case["correlations"] == []
    assert application_case["candidates"] == []
    assert application_case["evaluations"] == []
    assert application_case["primary_cause"] is None
    assert application_case["confidences"] == []
    assert application_case["explanations"] == []
    assert application_case["recommendations"] == []

def test_technician_can_expose_network_diagnostic_case():
    from application.technician import Technician

    technician = Technician()

    assert hasattr(
        technician,
        "network_case_synthesizer",
    )

def test_technician_diagnose_exposes_network_diagnostic_case():
    from application.technician import Technician

    technician = Technician()

    result = technician.diagnose()

    assert "network_diagnostic_case" in result

def test_technician_keeps_diagnostic_and_network_cases_separate():
    from application.technician import Technician

    technician = Technician()

    result = technician.diagnose()

    assert "diagnostic_case" in result
    assert "network_diagnostic_case" in result

    assert result["diagnostic_case"] is not result[
        "network_diagnostic_case"
    ]


def test_network_case_result_is_independent_from_internal_case():
    from application.technician import Technician

    technician = Technician()

    result = technician.diagnose()

    network_result = result[
        "network_diagnostic_case"
    ]

    original_observations = list(
        network_result["observations"]
    )

    original_findings = list(
        network_result["findings"]
    )

    network_result[
        "observations"
    ].append("changed")

    network_result[
        "findings"
    ].append("changed")

    fresh_result = technician.diagnose()

    fresh_network_result = fresh_result[
        "network_diagnostic_case"
    ]

    assert fresh_network_result[
        "observations"
    ] == original_observations

    assert fresh_network_result[
        "findings"
    ] == original_findings


def test_network_case_does_not_replace_diagnostic_case():
    from application.technician import Technician

    technician = Technician()

    result = technician.diagnose()

    diagnostic_case = result[
        "diagnostic_case"
    ]

    network_case = result[
        "network_diagnostic_case"
    ]

    assert "root_cause_candidates" in diagnostic_case
    assert "primary_root_cause" in diagnostic_case

    assert "observations" in network_case
    assert "signals" in network_case
    assert "evaluations" in network_case
    assert "confidences" in network_case

def test_technician_diagnose_exposes_network_case_explanation():
    from application.technician import Technician

    technician = Technician()

    result = technician.diagnose()

    assert "network_case_explanation" in result

def test_network_case_explanation_is_user_facing_explanation():
    from application.technician import Technician
    from engine.explanation import Explanation

    technician = Technician()

    result = technician.diagnose()

    explanation = result[
        "network_case_explanation"
    ]

    assert isinstance(
        explanation,
        Explanation,
    )

    assert explanation.subject == (
        "DIAGNOSTIC_CASE"
    )

    assert (
        "technical reasoning chain"
        not in explanation.summary.lower()
    )

def test_network_case_explanation_is_independent_from_internal_case():
    from application.technician import Technician

    technician = Technician()

    result = technician.diagnose()

    explanation = result[
        "network_case_explanation"
    ]

    original_summary = explanation.summary
    original_details = explanation.details

    explanation.summary = "changed"
    explanation.details = "changed"

    fresh_result = technician.diagnose()

    fresh_explanation = fresh_result[
        "network_case_explanation"
    ]

    assert fresh_explanation.summary == (
        original_summary
    )

    assert fresh_explanation.details == (
        original_details
    )

def test_technician_can_request_network_technician_explanation():
    from application.technician import Technician
    from engine.explanation import Explanation

    technician = Technician()

    technician.diagnose()

    explanation = (
        technician.get_network_case_explanation(
            "TECHNICIAN"
        )
    )

    assert isinstance(
        explanation,
        Explanation,
    )

    assert explanation.subject == (
        "DIAGNOSTIC_CASE"
    )

    assert (
        "technical reasoning chain"
        in explanation.summary.lower()
    )

def test_technician_network_case_explanation_rejects_invalid_audience():
    from application.technician import Technician

    technician = Technician()

    technician.diagnose()

    try:
        technician.get_network_case_explanation(
            "INVALID"
        )
    except ValueError:
        return

    assert False, (
        "Invalid explanation audience should "
        "raise ValueError."
    )

def test_technician_diagnose_exposes_complete_network_diagnostic_result():
    from application.technician import Technician

    technician = Technician()

    result = technician.diagnose()

    assert "network_diagnostic_case" in result
    assert "network_case_explanation" in result

    network_case = result[
        "network_diagnostic_case"
    ]

    assert "observations" in network_case
    assert "signals" in network_case
    assert "findings" in network_case
    assert "correlations" in network_case
    assert "candidates" in network_case
    assert "evaluations" in network_case
    assert "primary_cause" in network_case
    assert "confidences" in network_case
    assert "recommendations" in network_case

def test_technician_diagnose_runs_network_pipeline_once():
    from application.technician import Technician

    technician = Technician()

    calls = []

    original_diagnose = (
        technician.network_diagnostic_pipeline.diagnose
    )

    def tracked_diagnose(evidence):
        calls.append(evidence)
        return original_diagnose(evidence)

    technician.network_diagnostic_pipeline.diagnose = (
        tracked_diagnose
    )

    technician.diagnose()

    assert len(calls) == 1

def test_technician_diagnose_does_not_rerun_network_pipeline_for_explanation():
    from application.technician import Technician

    technician = Technician()

    calls = []

    original_diagnose = (
        technician.network_diagnostic_pipeline.diagnose
    )

    def tracked_diagnose(evidence):
        calls.append(evidence)
        return original_diagnose(evidence)

    technician.network_diagnostic_pipeline.diagnose = (
        tracked_diagnose
    )

    result = technician.diagnose()

    assert len(calls) == 1
    assert "network_diagnostic_case" in result
    assert "network_case_explanation" in result
