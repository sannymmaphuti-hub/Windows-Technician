from main import APP_NAME, APP_VERSION
from packaging.application_metadata import APPLICATION_METADATA


def test_main_uses_canonical_application_name():
    assert APP_NAME == APPLICATION_METADATA.display_name


def test_main_uses_canonical_application_version():
    assert APP_VERSION == APPLICATION_METADATA.version


def test_main_application_identity_is_v09_beta():
    assert APP_NAME == "Windows Technician"
    assert APP_VERSION.startswith("0.9.")
