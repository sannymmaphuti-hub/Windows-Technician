from engine.observation import Observation
from engine.memory_observation_builder import MemoryObservationBuilder


def test_memory_observation_builder_creates_usage_observation():

    builder = MemoryObservationBuilder()

    observations = builder.build(
        {
            "usage_percent": 88
        }
    )

    assert len(observations) == 1

    observation = observations[0]

    assert isinstance(observation, Observation)
    assert observation.source == "memory"
    assert observation.subject == "system_memory"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88

def test_memory_observation_builder_returns_no_observations_when_usage_is_missing():

    builder = MemoryObservationBuilder()

    observations = builder.build({})

    assert observations == []

def test_memory_observation_builder_creates_observations_for_memory_metrics():

    builder = MemoryObservationBuilder()

    observations = builder.build(
        {
            "total_gb": 3.87,
            "used_gb": 3.41,
            "available_gb": 0.46,
            "usage_percent": 88
        }
    )

    assert len(observations) == 4

    attributes = {
        observation.attribute
        for observation in observations
    }

    assert attributes == {
        "total_gb",
        "used_gb",
        "available_gb",
        "usage_percent"
    }

def test_memory_observation_builder_preserves_memory_values():

    builder = MemoryObservationBuilder()

    observations = builder.build(
        {
            "total_gb": 3.87,
            "used_gb": 3.41,
            "available_gb": 0.46,
            "usage_percent": 88
        }
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

def test_memory_observation_builder_preserves_zero_values():

    builder = MemoryObservationBuilder()

    observations = builder.build(
        {
            "usage_percent": 0
        }
    )

    assert len(observations) == 1

    observation = observations[0]

    assert observation.attribute == "usage_percent"
    assert observation.value == 0

def test_memory_observation_builder_returns_observations_in_metric_order():

    builder = MemoryObservationBuilder()

    observations = builder.build(
        {
            "usage_percent": 88,
            "available_gb": 0.46,
            "total_gb": 3.87,
            "used_gb": 3.41
        }
    )

    attributes = [
        observation.attribute
        for observation in observations
    ]

    assert attributes == [
        "total_gb",
        "used_gb",
        "available_gb",
        "usage_percent"
    ]

def test_memory_observation_builder_accepts_memory_evidence_payload():

    builder = MemoryObservationBuilder()

    memory_evidence = {
        "total_gb": 3.87,
        "used_gb": 3.41,
        "available_gb": 0.46,
        "usage_percent": 88
    }

    observations = builder.build(memory_evidence)

    assert len(observations) == 4

def test_memory_observation_builder_uses_consistent_source_and_subject():

    builder = MemoryObservationBuilder()

    observations = builder.build(
        {
            "total_gb": 3.87,
            "used_gb": 3.41,
            "available_gb": 0.46,
            "usage_percent": 88
        }
    )

    for observation in observations:

        assert observation.source == "memory"
        assert observation.subject == "system_memory"

def test_memory_observation_builder_handles_partial_memory_evidence():

    builder = MemoryObservationBuilder()

    observations = builder.build(
        {
            "used_gb": 3.41,
            "usage_percent": 88
        }
    )

    attributes = [
        observation.attribute
        for observation in observations
    ]

    assert attributes == [
        "used_gb",
        "usage_percent"
    ]