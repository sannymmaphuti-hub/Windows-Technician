from engine.observation import Observation


def test_observation_can_be_converted_to_evidence_record():

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88
    )

    record = observation.to_evidence()

    assert record == {
        "source": "memory",
        "subject": "system_memory",
        "attribute": "usage_percent",
        "value": 88
    }