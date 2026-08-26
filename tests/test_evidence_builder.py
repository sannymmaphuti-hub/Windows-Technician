from engine.evidence_builder import EvidenceBuilder


def test_builder_starts_empty():

    builder = EvidenceBuilder()

    evidence = builder.build()

    assert evidence.get_all() == {}


def test_builder_can_add_category():

    builder = EvidenceBuilder()

    builder.add_category(
        "CPU",
        {
            "usage_percent": 90
        }
    )

    evidence = builder.build()

    assert evidence.has("CPU")


def test_builder_preserves_category_data():

    builder = EvidenceBuilder()

    cpu_data = {
        "usage_percent": 90,
        "frequency_mhz": 2208
    }

    builder.add_category(
        "CPU",
        cpu_data
    )

    evidence = builder.build()

    assert evidence.get("CPU") == cpu_data


def test_builder_can_add_multiple_categories():

    builder = EvidenceBuilder()

    builder.add_category(
        "CPU",
        {
            "usage_percent": 90
        }
    )

    builder.add_category(
        "MEMORY",
        {
            "usage_percent": 80
        }
    )

    evidence = builder.build()

    assert evidence.has("CPU")
    assert evidence.has("MEMORY")

from engine.collectors.cpu_collector import CPUCollector


def test_builder_can_add_collector():

    builder = EvidenceBuilder()

    collector = CPUCollector()

    builder.add_collector(collector)

    evidence = builder.build()

    assert evidence.has("CPU")

    cpu_data = evidence.get("CPU")

    assert "usage_percent" in cpu_data
    assert "physical_cores" in cpu_data
    assert "logical_processors" in cpu_data
    assert "top_processes" in cpu_data