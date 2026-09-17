from engine.evidence import DiagnosticEvidence
from engine.observation_builder import ObservationBuilder


def test_observation_builder_returns_no_observations_for_empty_evidence():

    evidence = DiagnosticEvidence()

    observations = ObservationBuilder().build(evidence)

    assert observations == []


def test_observation_builder_returns_no_observations_for_empty_cpu_evidence():

    evidence = DiagnosticEvidence(
        {
            "CPU": {}
        }
    )

    observations = ObservationBuilder().build(evidence)

    assert observations == []


def test_observation_builder_returns_no_observations_for_empty_memory_evidence():

    evidence = DiagnosticEvidence(
        {
            "MEMORY": {}
        }
    )

    observations = ObservationBuilder().build(evidence)

    assert observations == []