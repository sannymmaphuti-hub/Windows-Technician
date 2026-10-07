# ==========================================
# Windows Technician v0.9
# WINDOWS STARTUP EVIDENCE TESTS
# ==========================================

from engine.windows_startup_evidence import (
    WindowsStartupEvidence,
)


def test_empty_evidence_is_valid():
    evidence = WindowsStartupEvidence()

    assert evidence.items == []
    assert evidence.item_count == 0


def test_items_are_stored():
    items = [
        {
            "name": "OneDrive",
            "command": "OneDrive.exe",
            "enabled": True,
        }
    ]

    evidence = WindowsStartupEvidence(
        items=items
    )

    assert evidence.item_count == 1
    assert evidence.items[0]["name"] == "OneDrive"


def test_items_are_deep_copied():
    items = [
        {
            "name": "OneDrive",
            "command": "OneDrive.exe",
            "enabled": True,
        }
    ]

    evidence = WindowsStartupEvidence(
        items=items
    )

    items[0]["name"] = "Changed"

    assert evidence.items[0]["name"] == "OneDrive"


def test_invalid_items_type_is_rejected():
    try:
        WindowsStartupEvidence(
            items="invalid"
        )
    except ValueError:
        return

    raise AssertionError(
        "Expected ValueError for invalid items."
    )


def test_get_item_finds_by_name():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "OneDrive",
                "command": "OneDrive.exe",
                "enabled": True,
            }
        ]
    )

    item = evidence.get_item("onedrive")

    assert item is not None
    assert item["name"] == "OneDrive"


def test_get_item_returns_copy():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "OneDrive",
                "command": "OneDrive.exe",
                "enabled": True,
            }
        ]
    )

    item = evidence.get_item("OneDrive")

    item["name"] = "Changed"

    assert (
        evidence.get_item("OneDrive")["name"]
        == "OneDrive"
    )


def test_get_item_returns_none_for_unknown_item():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "OneDrive",
                "command": "OneDrive.exe",
                "enabled": True,
            }
        ]
    )

    assert (
        evidence.get_item("Unknown") is None
    )


def test_get_item_rejects_invalid_name():
    evidence = WindowsStartupEvidence()

    assert evidence.get_item(None) is None
    assert evidence.get_item("") is None
    assert evidence.get_item("   ") is None


def test_disabled_items_are_still_preserved():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "Example",
                "command": "Example.exe",
                "enabled": False,
            }
        ]
    )

    assert evidence.item_count == 1
    assert (
        evidence.get_item("Example")["enabled"]
        is False
    )


def test_multiple_items_are_preserved():
    evidence = WindowsStartupEvidence(
        items=[
            {
                "name": "One",
                "command": "One.exe",
                "enabled": True,
            },
            {
                "name": "Two",
                "command": "Two.exe",
                "enabled": False,
            },
        ]
    )

    assert evidence.item_count == 2