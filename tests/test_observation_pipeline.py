from engine.evidence_builder import EvidenceBuilder
from engine.cpu_observation_builder import CPUObservationBuilder
from engine.memory_observation_builder import MemoryObservationBuilder


def test_cpu_and_memory_evidence_can_be_translated_into_observations():

    builder = EvidenceBuilder()

    builder.add_category(
        "CPU",
        {
            "physical_cores": 2,
            "logical_processors": 4,
            "usage_percent": 25,
            "frequency_mhz": 2400
        }
    )

    builder.add_category(
        "MEMORY",
        {
            "total_gb": 3.87,
            "used_gb": 3.41,
            "available_gb": 0.46,
            "usage_percent": 88
        }
    )

    evidence = builder.build()

    cpu_observations = CPUObservationBuilder().build(
        evidence.get("CPU")
    )

    memory_observations = MemoryObservationBuilder().build(
        evidence.get("MEMORY")
    )

    observations = cpu_observations + memory_observations

    assert len(observations) == 8


def test_cpu_and_memory_observations_remain_distinguishable():

    builder = EvidenceBuilder()

    builder.add_category(
        "CPU",
        {
            "usage_percent": 25
        }
    )

    builder.add_category(
        "MEMORY",
        {
            "usage_percent": 88
        }
    )

    evidence = builder.build()

    cpu_observations = CPUObservationBuilder().build(
        evidence.get("CPU")
    )

    memory_observations = MemoryObservationBuilder().build(
        evidence.get("MEMORY")
    )

    observations = cpu_observations + memory_observations

    assert observations[0].source == "cpu"
    assert observations[0].subject == "system_cpu"

    assert observations[1].source == "memory"
    assert observations[1].subject == "system_memory"


def test_cpu_and_memory_observations_preserve_their_values():

    builder = EvidenceBuilder()

    builder.add_category(
        "CPU",
        {
            "usage_percent": 25
        }
    )

    builder.add_category(
        "MEMORY",
        {
            "usage_percent": 88
        }
    )

    evidence = builder.build()

    observations = (
        CPUObservationBuilder().build(evidence.get("CPU"))
        + MemoryObservationBuilder().build(evidence.get("MEMORY"))
    )

    values = {
        observation.source: observation.value
        for observation in observations
    }

    assert values == {
        "cpu": 25,
        "memory": 88
    }