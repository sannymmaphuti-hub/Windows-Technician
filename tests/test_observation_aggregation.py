from engine.observation import Observation


def test_observations_can_be_combined_into_one_observation_set():

    memory_observations = [
        Observation(
            source="memory",
            subject="system_memory",
            attribute="usage_percent",
            value=88
        )
    ]

    cpu_observations = [
        Observation(
            source="cpu",
            subject="system_cpu",
            attribute="usage_percent",
            value=25
        )
    ]

    observations = memory_observations + cpu_observations

    assert len(observations) == 2

    assert observations[0].source == "memory"
    assert observations[1].source == "cpu"

def test_combined_observations_preserve_each_observation_identity():

    memory_observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88
    )

    cpu_observation = Observation(
        source="cpu",
        subject="system_cpu",
        attribute="usage_percent",
        value=25
    )

    observations = [
        memory_observation,
        cpu_observation
    ]

    assert observations[0] is memory_observation
    assert observations[1] is cpu_observation

    assert observations[0].to_evidence() == {
        "source": "memory",
        "subject": "system_memory",
        "attribute": "usage_percent",
        "value": 88
    }

    assert observations[1].to_evidence() == {
        "source": "cpu",
        "subject": "system_cpu",
        "attribute": "usage_percent",
        "value": 25
    }