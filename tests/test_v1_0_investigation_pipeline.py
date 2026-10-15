from engine.diagnostic_case import DiagnosticCase
from engine.system_level_investigation import SystemLevelInvestigation
from engine.system_level_recommendations import SystemLevelRecommendations
from engine.system_problem_relationships import SystemProblemRelationships
from engine.system_root_cause_reasoning import SystemRootCauseReasoning
from engine.system_wide_intelligence import SystemWideIntelligence
from engine.v1_0_investigation_pipeline import V1InvestigationPipeline


def test_pipeline_uses_existing_canonical_engines():
    pipeline = V1InvestigationPipeline()

    assert isinstance(
        pipeline.system_intelligence,
        SystemWideIntelligence,
    )
    assert isinstance(
        pipeline.investigation,
        SystemLevelInvestigation,
    )
    assert isinstance(
        pipeline.relationships,
        SystemProblemRelationships,
    )
    assert isinstance(
        pipeline.root_cause,
        SystemRootCauseReasoning,
    )
    assert isinstance(
        pipeline.recommendations,
        SystemLevelRecommendations,
    )


def test_pipeline_runs_complete_canonical_sequence():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run()

    assert set(result) == {
        "case",
        "system_intelligence",
        "investigation",
        "relationships",
        "root_cause",
        "recommendations",
    }


def test_pipeline_creates_canonical_diagnostic_case():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run()

    assert isinstance(result["case"], DiagnosticCase)
    assert type(result["case"]) is DiagnosticCase


def test_pipeline_preserves_system_intelligence_context():
    pipeline = V1InvestigationPipeline()

    domains = {
        "MEMORY": {
            "findings": [
                {
                    "type": "MEMORY",
                    "severity": "WARNING",
                }
            ]
        },
        "PROCESS": {
            "findings": [
                {
                    "type": "PROCESS",
                    "severity": "INFO",
                }
            ]
        },
    }

    result = pipeline.run(domains=domains)

    context = result["system_intelligence"]

    assert context["domain_count"] == 2
    assert context["domains"] == [
        "MEMORY",
        "PROCESS",
    ]
    assert context["domain_data"] == domains


def test_pipeline_passes_system_data_to_investigation():
    pipeline = V1InvestigationPipeline()

    system_data = {
        "findings": [
            {
                "domain": "MEMORY", "finding": { "finding_type": "MEMORY_EXHAUSTION", "severity": "CRITICAL" },
            }
        ],
        "patterns": [],
    }

    result = pipeline.run(system_data=system_data)

    assert result["investigation"]["target_count"] >= 1


def test_pipeline_passes_evidence_to_relationship_analysis():
    pipeline = V1InvestigationPipeline()

    evidence = [
        {
            "type": "MEMORY",
            "severity": "WARNING",
        },
        {
            "type": "PROCESS",
            "severity": "WARNING",
        },
    ]

    result = pipeline.run(evidence=evidence)

    assert result["case"].evidence == evidence


def test_pipeline_connects_relationships_to_root_cause_reasoning():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run(
        evidence=[
            {
                "type": "MEMORY",
                "severity": "WARNING",
            },
            {
                "type": "PROCESS",
                "severity": "WARNING",
            },
        ]
    )

    relationships = result["relationships"]["relationships"]
    root_cause_input = result["root_cause"]

    assert isinstance(relationships, list)
    assert isinstance(root_cause_input, dict)
    assert "root_causes" in root_cause_input
    assert "primary_root_cause" in root_cause_input


def test_pipeline_connects_system_data_to_recommendations():
    pipeline = V1InvestigationPipeline()

    system_data = {
        "findings": [
            {
                "domain": "MEMORY", "finding": { "finding_type": "MEMORY_EXHAUSTION", "severity": "CRITICAL" },
            }
        ],
        "patterns": [],
    }

    result = pipeline.run(system_data=system_data)

    assert "recommendations" in result["recommendations"]
    assert "recommendation_count" in result["recommendations"]


def test_pipeline_populates_case_findings():
    pipeline = V1InvestigationPipeline()

    findings = [
        {
            "domain": "MEMORY", "finding": { "finding_type": "MEMORY_EXHAUSTION", "severity": "CRITICAL" },
        }
    ]

    result = pipeline.run(
        system_data={
            "findings": findings,
            "patterns": [],
        }
    )

    assert result["case"].findings == findings


def test_pipeline_populates_case_correlations():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run(
        evidence=[
            {
                "type": "MEMORY",
                "severity": "WARNING",
            },
            {
                "type": "PROCESS",
                "severity": "WARNING",
            },
        ]
    )

    assert (
        result["case"].correlations
        == result["relationships"]["relationships"]
    )


def test_pipeline_populates_case_root_causes():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run(
        evidence=[
            {
                "type": "MEMORY",
                "severity": "WARNING",
            },
            {
                "type": "PROCESS",
                "severity": "WARNING",
            },
        ]
    )

    assert (
        result["case"].root_causes
        == result["root_cause"]["root_causes"]
    )


def test_pipeline_populates_case_recommendations():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run(
        system_data={
            "findings": [
                {
                    "domain": "MEMORY", "finding": { "finding_type": "MEMORY_EXHAUSTION", "severity": "CRITICAL" },
                }
            ],
            "patterns": [],
        }
    )

    assert (
        result["case"].recommendations
        == result["recommendations"]["recommendations"]
    )


def test_pipeline_can_populate_existing_case():
    pipeline = V1InvestigationPipeline()
    existing_case = DiagnosticCase()

    result = pipeline.run(
        case=existing_case,
        evidence=[
            {
                "type": "MEMORY",
                "severity": "WARNING",
            }
        ],
    )

    assert result["case"] is existing_case


def test_pipeline_does_not_create_fleet_intelligence():
    pipeline = V1InvestigationPipeline()

    assert not hasattr(
        pipeline,
        "fleet_intelligence",
    )


def test_pipeline_does_not_execute_remediation():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run()

    assert result["system_intelligence"]["remediation"] is None


def test_pipeline_preserves_empty_stage_contracts():
    pipeline = V1InvestigationPipeline()

    result = pipeline.run()

    assert result["relationships"]["relationships"] == []
    assert result["root_cause"]["root_causes"] == []
    assert result["root_cause"]["primary_root_cause"] is None
    assert result["recommendations"]["recommendations"] == []


def test_pipeline_accepts_custom_canonical_components():
    system_intelligence = SystemWideIntelligence()
    investigation = SystemLevelInvestigation()
    relationships = SystemProblemRelationships()
    root_cause = SystemRootCauseReasoning()
    recommendations = SystemLevelRecommendations()

    pipeline = V1InvestigationPipeline(
        system_intelligence=system_intelligence,
        investigation=investigation,
        relationships=relationships,
        root_cause=root_cause,
        recommendations=recommendations,
    )

    assert pipeline.system_intelligence is system_intelligence
    assert pipeline.investigation is investigation
    assert pipeline.relationships is relationships
    assert pipeline.root_cause is root_cause
    assert pipeline.recommendations is recommendations


def test_pipeline_preserves_distinct_evidence_into_root_cause():
    pipeline = V1InvestigationPipeline()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "finding_id": "memory-01",
            },
        },
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "finding_id": "memory-02",
            },
        },
        {
            "domain": "PROCESS",
            "finding": {
                "finding_type": "HIGH_PROCESS_MEMORY",
                "finding_id": "process-01",
            },
        },
    ]

    result = pipeline.run(evidence=evidence)

    relationships = result["relationships"]["relationships"]
    candidates = result["root_cause"]["root_causes"]

    assert len(relationships) == 1
    assert candidates

    supporting_relationships = candidates[0][
        "supporting_relationships"
    ]
    assert relationships[0] in supporting_relationships

    preserved_ids = {
        finding["finding_id"]
        for finding in supporting_relationships[0]["findings"]
    }

    assert preserved_ids == {
        "memory-01",
        "memory-02",
        "process-01",
    }


def test_pipeline_uses_system_data_findings_when_evidence_is_empty():
    pipeline = V1InvestigationPipeline()

    finding = {
        "domain": "MEMORY",
        "finding": {
            "finding_type": "MEMORY_EXHAUSTION",
            "severity": "CRITICAL",
            "finding_id": "memory-system-data-01",
            "evidence": ["memory pressure detected"],
            "provenance": {"source": "system_data"},
        },
    }
    system_data = {
        "findings": [finding],
        "patterns": [],
    }

    result = pipeline.run(system_data=system_data)

    recommendations = result["recommendations"]["recommendations"]

    assert any(
        recommendation.get("finding_id") == "memory-system-data-01"
        for recommendation in recommendations
    ), recommendations

    assert system_data["findings"] == [finding]


def test_pipeline_merges_evidence_and_system_data_findings_for_recommendations():
    pipeline = V1InvestigationPipeline()

    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_EXHAUSTION",
                "severity": "CRITICAL",
                "finding_id": "memory-evidence-01",
                "evidence": ["Critical memory exhaustion"],
                "provenance": {"source": "diagnostic_evidence"},
            },
        },
    ]

    system_data_finding = {
        "domain": "PROCESS",
        "finding": {
            "finding_type": "HIGH_PROCESS_MEMORY",
            "severity": "HIGH",
            "finding_id": "process-system-data-01",
            "evidence": ["Process memory consumption is high"],
            "provenance": {"source": "system_data"},
        },
    }

    system_data = {
        "findings": [system_data_finding],
        "patterns": [],
    }

    result = pipeline.run(
        evidence=evidence,
        system_data=system_data,
    )

    recommendations = result["recommendations"]["recommendations"]

    recommendation_ids = {
        recommendation.get("finding_id")
        for recommendation in recommendations
    }

    assert "memory-evidence-01" in recommendation_ids, recommendations
    assert "process-system-data-01" in recommendation_ids, recommendations

    # Neither caller-owned input may be modified by the pipeline.
    assert evidence[0]["finding"]["finding_id"] == "memory-evidence-01"
    assert system_data["findings"] == [system_data_finding]
