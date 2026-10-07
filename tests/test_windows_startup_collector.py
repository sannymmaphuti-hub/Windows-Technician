# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP COLLECTOR TESTS
# ==========================================

import json
import subprocess

from engine.windows_startup_collector import (
    WindowsStartupCollector,
)
from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)


def test_collector_has_startup_domain():
    collector = WindowsStartupCollector()

    assert collector.domain == "STARTUP"


def test_collect_returns_startup_evidence(monkeypatch):
    payload = json.dumps(
        [
            {
                "Name": "OneDrive",
                "Command": "OneDrive.exe",
                "Location": "HKCU\\Run",
                "User": "User",
            }
        ]
    )

    class Result:
        stdout = payload

    def fake_run(*args, **kwargs):
        return Result()

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    collector = WindowsStartupCollector()

    evidence = collector.collect()

    assert isinstance(
        evidence,
        WindowsStartupEvidence,
    )

    assert evidence.item_count == 1


def test_collect_normalizes_startup_record(monkeypatch):
    payload = json.dumps(
        [
            {
                "Name": "OneDrive",
                "Command": "OneDrive.exe",
                "Location": "HKCU\\Run",
                "User": "User",
            }
        ]
    )

    class Result:
        stdout = payload

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    evidence = WindowsStartupCollector().collect()

    item = evidence.get_item("OneDrive")

    assert item["name"] == "OneDrive"
    assert item["command"] == "OneDrive.exe"
    assert item["location"] == "HKCU\\Run"
    assert item["user"] == "User"


def test_collect_marks_discovered_startup_item_enabled(
    monkeypatch,
):
    payload = json.dumps(
        [
            {
                "Name": "OneDrive",
                "Command": "OneDrive.exe",
                "Location": "HKCU\\Run",
                "User": "User",
            }
        ]
    )

    class Result:
        stdout = payload

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    evidence = WindowsStartupCollector().collect()

    item = evidence.get_item("OneDrive")

    assert item["enabled"] is True


def test_collect_handles_empty_output(monkeypatch):
    class Result:
        stdout = ""

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    evidence = WindowsStartupCollector().collect()

    assert isinstance(
        evidence,
        WindowsStartupEvidence,
    )

    assert evidence.items == []


def test_collect_handles_invalid_json(monkeypatch):
    class Result:
        stdout = "not valid json"

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    evidence = WindowsStartupCollector().collect()

    assert evidence.items == []


def test_collect_handles_single_json_record(monkeypatch):
    payload = json.dumps(
        {
            "Name": "OneDrive",
            "Command": "OneDrive.exe",
            "Location": "HKCU\\Run",
            "User": "User",
        }
    )

    class Result:
        stdout = payload

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    evidence = WindowsStartupCollector().collect()

    assert evidence.item_count == 1


def test_collect_ignores_records_without_name(
    monkeypatch,
):
    payload = json.dumps(
        [
            {
                "Command": "Broken.exe",
                "Location": "HKCU\\Run",
            },
            {
                "Name": "Valid",
                "Command": "Valid.exe",
                "Location": "HKCU\\Run",
            },
        ]
    )

    class Result:
        stdout = payload

    monkeypatch.setattr(
        subprocess,
        "run",
        lambda *args, **kwargs: Result(),
    )

    evidence = WindowsStartupCollector().collect()

    assert evidence.item_count == 1
    assert evidence.get_item("Valid") is not None


def test_collect_handles_subprocess_failure(
    monkeypatch,
):
    def fake_run(*args, **kwargs):
        raise subprocess.SubprocessError(
            "PowerShell failed"
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    evidence = WindowsStartupCollector().collect()

    assert isinstance(
        evidence,
        WindowsStartupEvidence,
    )

    assert evidence.items == []


def test_collect_handles_os_failure(monkeypatch):
    def fake_run(*args, **kwargs):
        raise OSError(
            "PowerShell unavailable"
        )

    monkeypatch.setattr(
        subprocess,
        "run",
        fake_run,
    )

    evidence = WindowsStartupCollector().collect()

    assert isinstance(
        evidence,
        WindowsStartupEvidence,
    )

    assert evidence.items == []


def test_parser_ignores_non_dictionary_records():
    output = json.dumps(
        [
            "invalid",
            123,
            None,
            {
                "Name": "Valid",
                "Command": "Valid.exe",
            },
        ]
    )

    items = (
        WindowsStartupCollector._parse_result(
            output
        )
    )

    assert len(items) == 1
    assert items[0]["name"] == "Valid"


def test_parser_normalizes_missing_optional_values():
    output = json.dumps(
        [
            {
                "Name": "Example",
            }
        ]
    )

    items = (
        WindowsStartupCollector._parse_result(
            output
        )
    )

    assert len(items) == 1

    item = items[0]

    assert item["name"] == "Example"
    assert item["command"] == ""
    assert item["location"] == ""
    assert item["user"] == ""
    assert item["enabled"] is True