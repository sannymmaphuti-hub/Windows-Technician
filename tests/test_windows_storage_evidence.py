# ==========================================
# Windows Technician v0.9
# WINDOWS STORAGE EVIDENCE
# ==========================================

from engine.windows_storage_evidence import (
    WindowsStorageEvidence,
)


def test_storage_evidence_can_be_created():
    evidence = WindowsStorageEvidence()

    assert evidence is not None


def test_storage_evidence_has_no_volumes_by_default():
    evidence = WindowsStorageEvidence()

    assert evidence.volumes == []


def test_storage_evidence_accepts_volumes():
    volumes = [
        {
            "drive": "C:",
            "filesystem": "NTFS",
            "total_bytes": 1000,
            "free_bytes": 250,
        }
    ]

    evidence = WindowsStorageEvidence(
        volumes=volumes
    )

    assert evidence.volumes == volumes


def test_storage_evidence_defensively_copies_volumes():
    volumes = [
        {
            "drive": "C:",
            "free_bytes": 250,
        }
    ]

    evidence = WindowsStorageEvidence(
        volumes=volumes
    )

    volumes[0]["free_bytes"] = 0
    volumes.append(
        {
            "drive": "D:",
            "free_bytes": 500,
        }
    )

    assert evidence.volumes == [
        {
            "drive": "C:",
            "free_bytes": 250,
        }
    ]


def test_storage_evidence_exposes_volume_count():
    evidence = WindowsStorageEvidence(
        volumes=[
            {"drive": "C:"},
            {"drive": "D:"},
        ]
    )

    assert evidence.volume_count == 2


def test_storage_evidence_calculates_free_space_ratio():
    evidence = WindowsStorageEvidence(
        volumes=[
            {
                "drive": "C:",
                "total_bytes": 1000,
                "free_bytes": 250,
            }
        ]
    )

    assert evidence.free_space_ratio("C:") == 0.25


def test_storage_evidence_returns_none_for_unknown_volume():
    evidence = WindowsStorageEvidence(
        volumes=[
            {
                "drive": "C:",
                "total_bytes": 1000,
                "free_bytes": 250,
            }
        ]
    )

    assert evidence.free_space_ratio("D:") is None


def test_storage_evidence_handles_zero_capacity():
    evidence = WindowsStorageEvidence(
        volumes=[
            {
                "drive": "C:",
                "total_bytes": 0,
                "free_bytes": 0,
            }
        ]
    )

    assert evidence.free_space_ratio("C:") is None


def test_storage_evidence_drive_lookup_is_case_insensitive():
    evidence = WindowsStorageEvidence(
        volumes=[
            {
                "drive": "C:",
                "total_bytes": 1000,
                "free_bytes": 250,
            }
        ]
    )

    assert evidence.free_space_ratio("c:") == 0.25


def test_storage_evidence_does_not_modify_input():
    volumes = [
        {
            "drive": "C:",
            "total_bytes": 1000,
            "free_bytes": 250,
        }
    ]

    original = [
        {
            "drive": "C:",
            "total_bytes": 1000,
            "free_bytes": 250,
        }
    ]

    WindowsStorageEvidence(
        volumes=volumes
    )

    assert volumes == original


def test_storage_evidence_rejects_non_list_volumes():
    try:
        WindowsStorageEvidence(
            volumes="invalid"
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid volumes."
    )


def test_storage_evidence_is_observational_only():
    evidence = WindowsStorageEvidence()

    assert not hasattr(
        evidence,
        "authorize"
    )

    assert not hasattr(
        evidence,
        "execute"
    )

    assert not hasattr(
        evidence,
        "remediate"
    )


def test_storage_evidence_does_not_create_diagnostic_case():
    evidence = WindowsStorageEvidence()

    assert not hasattr(
        evidence,
        "case_id"
    )


def test_storage_evidence_supports_multiple_volumes():
    evidence = WindowsStorageEvidence(
        volumes=[
            {
                "drive": "C:",
                "total_bytes": 1000,
                "free_bytes": 250,
            },
            {
                "drive": "D:",
                "total_bytes": 2000,
                "free_bytes": 1500,
            },
        ]
    )

    assert evidence.volume_count == 2
    assert evidence.free_space_ratio("C:") == 0.25
    assert evidence.free_space_ratio("D:") == 0.75


def test_storage_evidence_can_expose_volume_information():
    evidence = WindowsStorageEvidence(
        volumes=[
            {
                "drive": "C:",
                "filesystem": "NTFS",
                "total_bytes": 1000,
                "free_bytes": 250,
            }
        ]
    )

    volume = evidence.get_volume("C:")

    assert volume["drive"] == "C:"
    assert volume["filesystem"] == "NTFS"
    assert volume["total_bytes"] == 1000
    assert volume["free_bytes"] == 250


def test_storage_evidence_unknown_volume_returns_none():
    evidence = WindowsStorageEvidence()

    assert evidence.get_volume("C:") is None