from engine.observation import Observation


def test_observation_collection_can_store_multiple_observations():

    observations = []

    observations.append(
        Observation(
            source="memory",
            subject="system_memory",
            attribute="usage_percent",
            value=88
        )
    )

    observations.append(
        Observation(
            source="memory",
            subject="system_memory",
            attribute="available_mb",
            value=470
        )
    )

    assert len(observations) == 2
    assert observations[0].attribute == "usage_percent"
    assert observations[1].attribute == "available_mb"