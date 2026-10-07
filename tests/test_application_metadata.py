from packaging.application_metadata import (
    APPLICATION_METADATA,
    ApplicationMetadata,
)


def test_application_metadata_has_canonical_identity():
    metadata = APPLICATION_METADATA

    assert metadata.name == "windows-technician"
    assert metadata.display_name == "Windows Technician"
    assert metadata.version == "0.9.0"


def test_application_metadata_targets_beta_release():
    assert APPLICATION_METADATA.release_channel == "beta"


def test_application_metadata_defines_production_package_identity():
    metadata = APPLICATION_METADATA

    assert metadata.executable_name == "WindowsTechnician.exe"
    assert metadata.package_name == "WindowsTechnician"


def test_application_metadata_version_tuple():
    assert APPLICATION_METADATA.version_tuple == (0, 9, 0)


def test_application_metadata_full_display_name():
    assert (
        APPLICATION_METADATA.full_display_name
        == "Windows Technician 0.9.0"
    )


def test_application_metadata_is_immutable():
    metadata = APPLICATION_METADATA

    try:
        metadata.version = "0.9.1"
    except AttributeError:
        pass
    else:
        raise AssertionError(
            "Application metadata must be immutable."
        )


def test_application_metadata_rejects_empty_identity():
    try:
        ApplicationMetadata(
            name="",
            display_name="Windows Technician",
            version="0.9.0",
            release_channel="beta",
            executable_name="WindowsTechnician.exe",
            package_name="WindowsTechnician",
        )
    except ValueError:
        pass
    else:
        raise AssertionError("Empty application identity must fail.")


def test_application_metadata_rejects_non_v09_version():
    try:
        ApplicationMetadata(
            name="windows-technician",
            display_name="Windows Technician",
            version="0.8.0",
            release_channel="release",
            executable_name="WindowsTechnician.exe",
            package_name="WindowsTechnician",
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Packaging metadata must reject non-v0.9 versions."
        )
