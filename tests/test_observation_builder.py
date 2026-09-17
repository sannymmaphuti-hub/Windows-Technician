from engine.evidence import DiagnosticEvidence
from engine.observation import Observation
from engine.observation_builder import ObservationBuilder


def test_observation_builder_creates_observations_from_memory_evidence():

    evidence = DiagnosticEvidence(
        {
            "MEMORY": {
                "usage_percent": 88
            }
        }
    )

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 1

    observation = observations[0]

    assert isinstance(observation, Observation)
    assert observation.source == "memory"
    assert observation.subject == "system_memory"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88


def test_observation_builder_creates_observations_from_cpu_evidence():

    evidence = DiagnosticEvidence(
        {
            "CPU": {
                "usage_percent": 25
            }
        }
    )

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 1

    observation = observations[0]

    assert observation.source == "cpu"
    assert observation.subject == "system_cpu"
    assert observation.attribute == "usage_percent"
    assert observation.value == 25


def test_observation_builder_combines_multiple_categories():

    evidence = DiagnosticEvidence(
        {
            "CPU": {
                "usage_percent": 25
            },
            "MEMORY": {
                "usage_percent": 88
            }
        }
    )

    observations = ObservationBuilder().build(evidence)

    assert len(observations) == 2

    sources = {
        observation.source
        for observation in observations
    }

    assert sources == {
        "cpu",
        "memory"
    }


def test_observation_builder_handles_missing_categories():

    evidence = DiagnosticEvidence()

    observations = ObservationBuilder().build(evidence)

    assert observations == []