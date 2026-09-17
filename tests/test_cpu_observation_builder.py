from engine.observation import Observation
from engine.cpu_observation_builder import CPUObservationBuilder


def test_cpu_observation_builder_creates_cpu_observations():

    builder = CPUObservationBuilder()

    observations = builder.build(
        {
            "physical_cores": 2,
            "logical_processors": 4,
            "usage_percent": 25,
            "frequency_mhz": 2400
        }
    )

    assert len(observations) == 4

    assert all(
        isinstance(observation, Observation)
        for observation in observations
    )


def test_cpu_observation_builder_preserves_cpu_values():

    builder = CPUObservationBuilder()

    observations = builder.build(
        {
            "physical_cores": 2,
            "logical_processors": 4,
            "usage_percent": 25,
            "frequency_mhz": 2400
        }
    )

    values = {
        observation.attribute: observation.value
        for observation in observations
    }

    assert values == {
        "physical_cores": 2,
        "logical_processors": 4,
        "usage_percent": 25,
        "frequency_mhz": 2400
    }


def test_cpu_observation_builder_uses_consistent_source_and_subject():

    builder = CPUObservationBuilder()

    observations = builder.build(
        {
            "usage_percent": 25
        }
    )

    assert len(observations) == 1

    observation = observations[0]

    assert observation.source == "cpu"
    assert observation.subject == "system_cpu"


def test_cpu_observation_builder_handles_partial_cpu_evidence():

    builder = CPUObservationBuilder()

    observations = builder.build(
        {
            "usage_percent": 25,
            "frequency_mhz": 2400
        }
    )

    attributes = [
        observation.attribute
        for observation in observations
    ]

    assert attributes == [
        "usage_percent",
        "frequency_mhz"
    ]