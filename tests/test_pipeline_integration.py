from engine.diagnostic_orchestrator import DiagnosticOrchestrator
from engine.diagnostic_case import DiagnosticCase
from engine.report import generate_case_report


def test_complete_diagnostic_pipeline_produces_complete_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()

    assert isinstance(result, dict)

    case = orchestrator.get_case()

    assert isinstance(case, DiagnosticCase)

    assert case.evidence is not None
    assert case.findings is not None
    assert case.correlations is not None
    assert case.root_causes is not None
    assert case.recommendations is not None

def test_pipeline_data_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.evidence == result["evidence"]
    assert case.findings == result["diagnosis"]["findings"]
    assert case.correlations == result["correlations"]
    assert case.root_causes == result["diagnosis"]["root_causes"]
    assert case.recommendations == result["diagnosis"]["recommendations"]
    assert case.status == result["diagnosis"]["status"]


def test_pipeline_intelligence_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.process_intelligence == result[
        "process_intelligence"
    ]

    assert case.memory_intelligence == result[
        "memory_intelligence"
    ]

    assert case.memory_history == result[
        "memory_history"
    ]

    assert case.memory_trend_intelligence == result[
        "memory_trend_intelligence"
    ]

    assert case.memory_temporal_intelligence == result[
        "memory_temporal_intelligence"
    ]

    assert case.memory_diagnostic_intelligence == result[
        "memory_diagnostic_intelligence"
    ]

    assert case.root_cause_candidates == result[
        "root_cause_candidates"
    ]

    assert case.primary_root_cause == result[
        "primary_root_cause"
    ]


def test_case_does_not_share_intelligence_data_with_result():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    if isinstance(case.process_intelligence, dict):

        case.process_intelligence[
            "test_mutation"
        ] = True

        assert (
            "test_mutation"
            not in result["process_intelligence"]
        )

    if isinstance(case.memory_intelligence, dict):

        case.memory_intelligence[
            "test_mutation"
        ] = True

        assert (
            "test_mutation"
            not in result["memory_intelligence"]
        )

    if isinstance(case.memory_trend_intelligence, dict):

        case.memory_trend_intelligence[
            "test_mutation"
        ] = True

        assert (
            "test_mutation"
            not in result["memory_trend_intelligence"]
        )

    if isinstance(case.memory_temporal_intelligence, dict):

        case.memory_temporal_intelligence[
            "test_mutation"
        ] = True

        assert (
            "test_mutation"
            not in result["memory_temporal_intelligence"]
        )

    if isinstance(case.memory_diagnostic_intelligence, dict):

        case.memory_diagnostic_intelligence[
            "test_mutation"
        ] = True

        assert (
            "test_mutation"
            not in result["memory_diagnostic_intelligence"]
        )

    if isinstance(case.primary_root_cause, dict):

        case.primary_root_cause[
            "test_mutation"
        ] = True

        assert (
            "test_mutation"
            not in result["primary_root_cause"]
        )

def test_memory_intelligence_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.memory_intelligence == result[
        "memory_intelligence"
    ]


def test_memory_history_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.memory_history == result[
        "memory_history"
    ]


def test_memory_trend_intelligence_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.memory_trend_intelligence == result[
        "memory_trend_intelligence"
    ]

def test_memory_temporal_intelligence_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.memory_temporal_intelligence == result[
        "memory_temporal_intelligence"
    ]


def test_memory_diagnostic_intelligence_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.memory_diagnostic_intelligence == result[
        "memory_diagnostic_intelligence"
    ]


def test_root_cause_candidates_flow_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.root_cause_candidates == result[
        "root_cause_candidates"
    ]


def test_primary_root_cause_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.primary_root_cause == result[
        "primary_root_cause"
    ]

def test_recommendations_flow_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.recommendations == result[
        "diagnosis"
    ]["recommendations"]


def test_status_flows_into_diagnostic_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()
    case = orchestrator.get_case()

    assert case.status == result[
        "diagnosis"
    ]["status"]

def test_complete_pipeline_can_generate_report_from_case():

    orchestrator = DiagnosticOrchestrator()

    result = orchestrator.run()

    assert isinstance(result, dict)

    case = orchestrator.get_case()

    report = generate_case_report(case)

    assert isinstance(report, str)
    assert len(report) > 0

    assert "Windows Technician v0.5" in report
    assert "DIAGNOSTIC STATUS" in report
    assert "DIAGNOSTIC FINDINGS" in report
    assert "ROOT-CAUSE ANALYSIS" in report
    assert "SYSTEM RECOMMENDATIONS" in report

