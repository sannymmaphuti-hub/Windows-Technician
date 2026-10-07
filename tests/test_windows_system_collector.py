from engine.windows_system_collector import (
    WindowsSystemCollector,
)
from engine.windows_system_evidence import (
    WindowsSystemEvidence,
)


def test_collector_has_system_domain():
    collector = WindowsSystemCollector()

    assert collector.domain == "SYSTEM"


def test_collector_returns_system_evidence(monkeypatch):
    monkeypatch.setattr(
        "engine.windows_system_collector.platform.system",
        lambda: "Windows",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.platform.version",
        lambda: "10.0.26200",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.platform.machine",
        lambda: "AMD64",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.platform.processor",
        lambda: "AMD Ryzen",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.socket.gethostname",
        lambda: "TEST-PC",
    )

    collector = WindowsSystemCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence,
        WindowsSystemEvidence,
    )

    assert evidence.computer_name == "TEST-PC"
    assert evidence.operating_system == "Windows"
    assert evidence.os_version == "10.0.26200"
    assert evidence.architecture == "AMD64"
    assert evidence.processor == "AMD Ryzen"


def test_collector_normalizes_missing_values(monkeypatch):
    monkeypatch.setattr(
        "engine.windows_system_collector.platform.system",
        lambda: "",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.platform.version",
        lambda: "",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.platform.machine",
        lambda: "",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.platform.processor",
        lambda: "",
    )

    monkeypatch.setattr(
        "engine.windows_system_collector.socket.gethostname",
        lambda: "",
    )

    collector = WindowsSystemCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence,
        WindowsSystemEvidence,
    )

    assert evidence.computer_name == ""
    assert evidence.operating_system == ""
    assert evidence.os_version == ""
    assert evidence.architecture == ""
    assert evidence.processor == ""


def test_collector_handles_collection_failure(monkeypatch):
    def fail():
        raise OSError("system information unavailable")

    monkeypatch.setattr(
        "engine.windows_system_collector.socket.gethostname",
        fail,
    )

    collector = WindowsSystemCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence,
        WindowsSystemEvidence,
    )

    assert evidence.computer_name == ""
    assert evidence.operating_system == ""
    assert evidence.os_version == ""
    assert evidence.architecture == ""
    assert evidence.processor == ""