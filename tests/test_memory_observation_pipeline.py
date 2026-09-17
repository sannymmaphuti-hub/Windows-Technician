from engine.evidence_builder import EvidenceBuilder
from engine.memory_observation_builder import MemoryObservationBuilder
from engine.observation import Observation


def test_memory_evidence_can_be_translated_into_observations():

    builder = EvidenceBuilder()

    evidence = {
        "total_gb": 3.87,
        "used_gb": 3.41,
        "available_gb": 0.46,
        "usage_percent": 88
    }

    builder.add_category("MEMORY", evidence)

    diagnostic_evidence = builder.build()

    memory_evidence = diagnostic_evidence.get("MEMORY")

    observation_builder = MemoryObservationBuilder()

    observations = observation_builder.build(memory_evidence)

    assert len(observations) == 4
    assert all(isinstance(observation, Observation) for observation in observations)


def test_memory_observation_pipeline_preserves_evidence_values():

    builder = EvidenceBuilder()

    builder.add_category(
        "MEMORY",
        {
            "total_gb": 3.87,
            "used_gb": 3.41,
            "available_gb": 0.46,
            "usage_percent": 88
        }
    )

    diagnostic_evidence = builder.build()

    observations = MemoryObservationBuilder().build(
        diagnostic_evidence.get("MEMORY")
    )

    values = {
        observation.attribute: observation.value
        for observation in observations
    }

    assert values == {
        "total_gb": 3.87,
        "used_gb": 3.41,
        "available_gb": 0.46,
        "usage_percent": 88
    }


def test_memory_observation_pipeline_preserves_observation_identity():

    builder = EvidenceBuilder()

    builder.add_category(
        "MEMORY",
        {
            "usage_percent": 88
        }
    )

    diagnostic_evidence = builder.build()

    observations = MemoryObservationBuilder().build(
        diagnostic_evidence.get("MEMORY")
    )

    observation = observations[0]

    assert observation.source == "memory"
    assert observation.subject == "system_memory"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88