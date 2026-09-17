from engine.observation import Observation


def test_observation_can_represent_a_directly_observed_fact():
    observation = Observation(
        source="memory",
        subject="system",
        attribute="usage_percent",
        value=88,
    )

    assert observation.source == "memory"
    assert observation.subject == "system"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88


def test_observation_requires_source():
    try:
        Observation(
            source="",
            subject="system",
            attribute="usage_percent",
            value=88,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Observation should reject an empty source")


def test_observation_requires_subject():
    try:
        Observation(
            source="memory",
            subject="",
            attribute="usage_percent",
            value=88,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Observation should reject an empty subject")


def test_observation_requires_attribute():
    try:
        Observation(
            source="memory",
            subject="system",
            attribute="",
            value=88,
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Observation should reject an empty attribute")


def test_observation_can_contain_different_value_types():
    numeric = Observation(
        source="memory",
        subject="system",
        attribute="usage_percent",
        value=88,
    )

    text = Observation(
        source="network",
        subject="wifi",
        attribute="connection_state",
        value="connected",
    )

    boolean = Observation(
        source="network",
        subject="gateway",
        attribute="reachable",
        value=True,
    )

    assert numeric.value == 88
    assert text.value == "connected"
    assert boolean.value is True

def test_observation_preserves_its_semantic_identity():

    observation = Observation(
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88
    )

    assert observation.source == "memory"
    assert observation.subject == "system_memory"
    assert observation.attribute == "usage_percent"
    assert observation.value == 88