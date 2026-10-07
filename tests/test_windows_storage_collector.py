# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE COLLECTOR
# ==========================================

from engine.windows_storage_collector import (
    WindowsStorageCollector,
)
from engine.windows_storage_evidence import (
    WindowsStorageEvidence,
)


def test_collector_can_be_created():
    collector = WindowsStorageCollector()

    assert collector is not None


def test_collector_returns_storage_evidence():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence,
        WindowsStorageEvidence,
    )


def test_collector_returns_volume_collection():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence.volumes,
        list,
    )


def test_collected_volumes_have_expected_shape():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    for volume in evidence.volumes:
        assert isinstance(volume, dict)

        assert "drive" in volume
        assert "total_bytes" in volume
        assert "free_bytes" in volume


def test_collected_drive_is_string():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    for volume in evidence.volumes:
        assert isinstance(
            volume["drive"],
            str,
        )


def test_collected_capacity_values_are_numeric():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    for volume in evidence.volumes:
        assert isinstance(
            volume["total_bytes"],
            int,
        )

        assert isinstance(
            volume["free_bytes"],
            int,
        )


def test_free_space_cannot_exceed_total_space():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    for volume in evidence.volumes:
        assert volume["free_bytes"] <= volume["total_bytes"]


def test_collector_does_not_modify_storage():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence,
        WindowsStorageEvidence,
    )


def test_collector_does_not_create_diagnostic_case():
    collector = WindowsStorageCollector()

    evidence = collector.collect()

    assert not hasattr(
        evidence,
        "case_id",
    )


def test_collector_is_observational_only():
    collector = WindowsStorageCollector()

    assert not hasattr(
        collector,
        "authorize",
    )

    assert not hasattr(
        collector,
        "execute",
    )

    assert not hasattr(
        collector,
        "remediate",
    )


def test_each_collection_returns_independent_evidence():
    collector = WindowsStorageCollector()

    first = collector.collect()
    second = collector.collect()

    assert first is not second
    assert first.volumes is not second.volumes


def test_collector_does_not_share_volume_objects():
    collector = WindowsStorageCollector()

    first = collector.collect()
    second = collector.collect()

    if first.volumes and second.volumes:
        assert first.volumes[0] is not second.volumes[0]


def test_collector_exposes_domain():
    collector = WindowsStorageCollector()

    assert collector.domain == "STORAGE"


def test_collector_is_read_only():
    collector = WindowsStorageCollector()

    assert not hasattr(
        collector,
        "delete",
    )

    assert not hasattr(
        collector,
        "format",
    )

    assert not hasattr(
        collector,
        "repair",
    )