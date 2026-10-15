from engine.v1_0_investigation_pipeline import V1InvestigationPipeline


class StubSystemIntelligence:
    def analyze(self, domains):
        return {}


class StubInvestigation:
    def investigate(self, system_data):
        return {}


class RecordingRelationships:
    def __init__(self):
        self.received_evidence = None

    def analyze(self, evidence):
        self.received_evidence = evidence
        return {"relationships": []}


class StubRootCause:
    def analyze(self, relationships):
        return {
            "root_causes": [],
            "primary_root_cause": None,
        }


class StubRecommendations:
    def generate(self, system_data):
        return {"recommendations": []}


def test_wrapped_typed_findings_are_unwrapped_with_domain_provenance():
    relationships = RecordingRelationships()

    pipeline = V1InvestigationPipeline(
        system_intelligence=StubSystemIntelligence(),
        investigation=StubInvestigation(),
        relationships=relationships,
        root_cause=StubRootCause(),
        recommendations=StubRecommendations(),
    )

    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "category": "MEMORY",
                "severity": "HIGH",
            },
        }
    ]

    original_evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "category": "MEMORY",
                "severity": "HIGH",
            },
        }
    ]

    pipeline.run(
        domains={"MEMORY": {"findings": []}},
        system_data={"findings": evidence, "patterns": []},
        evidence=evidence,
    )

    assert relationships.received_evidence == [
        {
            "domain": "MEMORY",
            "finding": {
                "finding_type": "MEMORY_PRESSURE",
                "category": "MEMORY",
                "severity": "HIGH",
            },
        }
    ]

    # Normalization must not mutate the caller's original evidence.
    assert evidence == original_evidence



def test_legacy_memory_category_is_normalized_inside_wrapped_evidence():
    relationships = RecordingRelationships()

    pipeline = V1InvestigationPipeline(
        system_intelligence=StubSystemIntelligence(),
        investigation=StubInvestigation(),
        relationships=relationships,
        root_cause=StubRootCause(),
        recommendations=StubRecommendations(),
    )

    evidence = [
        {
            "domain": "MEMORY",
            "finding": {
                "category": "memory",
                "severity": "WARNING",
                "message": "High memory usage.",
            },
        }
    ]

    pipeline.run(
        domains={"MEMORY": {"findings": []}},
        system_data={"findings": evidence, "patterns": []},
        evidence=evidence,
    )

    assert relationships.received_evidence == [
        {
            "domain": "MEMORY",
            "finding": {
                "category": "memory",
                "severity": "WARNING",
                "message": "High memory usage.",
                "finding_type": "MEMORY_PRESSURE",
            },
        }
    ]

    # The caller's original evidence remains unchanged.
    assert "finding_type" not in evidence[0]["finding"]



def test_recommendation_traceability_survives_pipeline_and_case_storage():
    pipeline = V1InvestigationPipeline(
        system_intelligence=StubSystemIntelligence(),
        investigation=StubInvestigation(),
        relationships=RecordingRelationships(),
        root_cause=StubRootCause(),
    )

    finding = {
        "id": "memory-pipeline-001",
        "finding_type": "MEMORY_PRESSURE",
        "severity": "WARNING",
        "evidence": [{"source": "memory_monitor", "value": 92}],
        "provenance": {"collector": "memory_engine"},
    }
    wrapped_evidence = [{"domain": "MEMORY", "finding": finding}]

    result = pipeline.run(
        domains={"MEMORY": {"findings": []}},
        system_data={"findings": wrapped_evidence, "patterns": []},
        evidence=wrapped_evidence,
    )

    recommendations = result["recommendations"]["recommendations"]
    matching = [
        item for item in recommendations
        if item.get("finding_id") == "memory-pipeline-001"
    ]

    assert len(matching) == 1
    recommendation = matching[0]
    assert recommendation["finding"] == finding
    assert recommendation["evidence"] == finding["evidence"]
    assert recommendation["provenance"] == finding["provenance"]
    assert any(
        item.get("finding_id") == "memory-pipeline-001"
        for item in result["case"].recommendations
    )
