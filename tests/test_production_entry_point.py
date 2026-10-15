"""Production entry-point contract tests."""

import importlib
from pathlib import Path


def test_production_entry_point_exists():
    entry_point = Path(__file__).resolve().parents[1] / "main.py"

    assert entry_point.is_file()


def test_production_entry_point_is_importable():
    module = importlib.import_module("main")

    assert module is not None


def test_entry_point_exposes_application_metadata():
    module = importlib.import_module("main")

    assert module.APP_NAME == "Windows Technician"
    assert module.APP_VERSION.startswith("1.0.")


def test_entry_point_defines_main_callable():
    module = importlib.import_module("main")

    assert callable(module.main)


def test_importing_entry_point_does_not_start_application():
    module = importlib.import_module("main")

    assert callable(module.main)
