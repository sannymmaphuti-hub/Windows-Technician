from diagnostics.storage import generate_storage_diagnostics


def test_storage_healthy():
    storage_info = [
        {
            "device": "C:\\",
            "mountpoint": "C:\\",
            "filesystem": "NTFS",
            "total_gb": 1000.0,
            "used_gb": 100.0,
            "free_gb": 900.0,
            "usage_percent": 10.0
        }
    ]

    result = generate_storage_diagnostics(
        storage_info
    )

    assert result[0]["status"] == "HEALTHY"


def test_storage_warning():
    storage_info = [
        {
            "device": "C:\\",
            "mountpoint": "C:\\",
            "filesystem": "NTFS",
            "total_gb": 1000.0,
            "used_gb": 850.0,
            "free_gb": 150.0,
            "usage_percent": 85.0
        }
    ]

    result = generate_storage_diagnostics(
        storage_info
    )

    assert result[0]["status"] == "ATTENTION"


def test_storage_critical():
    storage_info = [
        {
            "device": "C:\\",
            "mountpoint": "C:\\",
            "filesystem": "NTFS",
            "total_gb": 1000.0,
            "used_gb": 950.0,
            "free_gb": 50.0,
            "usage_percent": 95.0
        }
    ]

    result = generate_storage_diagnostics(
        storage_info
    )

    assert result[0]["status"] == "CRITICAL"