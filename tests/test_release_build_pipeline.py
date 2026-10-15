import hashlib
import json
from pathlib import Path

import pytest

from packaging.release_build_pipeline import (
    ReleaseBuildConfig,
    build_command,
    sha256_file,
    write_release_manifest,
)


@pytest.fixture
def project(tmp_path):
    root = tmp_path / "source"
    root.mkdir()
    (root / "main.py").write_text("print('Windows Technician')\n", encoding="utf-8")
    resources = root / "resources"
    resources.mkdir()
    (resources / "README.md").write_text("resources\n", encoding="utf-8")
    return root


def test_release_config_requires_existing_source(tmp_path):
    with pytest.raises(ValueError, match="existing directory"):
        ReleaseBuildConfig(tmp_path / "missing", tmp_path / "dist")


def test_release_config_requires_application_entry_point(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    with pytest.raises(ValueError, match="main.py"):
        ReleaseBuildConfig(source, tmp_path / "dist")


def test_build_command_uses_production_entry_point_and_output(project, tmp_path):
    output = tmp_path / "dist"
    config = ReleaseBuildConfig(project, output, version="1.0.0")

    command = build_command(config, python_executable="python-test")

    assert command[0] == "python-test"
    assert command[1:3] == ["-m", "PyInstaller"]
    assert "--noconfirm" in command
    assert "--clean" in command
    assert "--windowed" in command
    assert "--onedir" in command
    assert "--onefile" not in command
    assert str(project / "main.py") == command[-1]
    assert str(output) in command


def test_build_command_includes_resources_when_present(project, tmp_path):
    command = build_command(
        ReleaseBuildConfig(project, tmp_path / "dist"),
        python_executable="python-test",
    )
    assert "--add-data" in command
    assert f"{project / 'resources'};resources" in command


def test_release_manifest_records_artifact_hash_and_size(tmp_path):
    artifact = tmp_path / "WindowsTechnician.exe"
    content = b"test-build-artifact"
    artifact.write_bytes(content)

    manifest_path = write_release_manifest(
        artifact,
        application_name="WindowsTechnician",
        version="1.0.0",
    )
    data = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert data["application"] == "WindowsTechnician"
    assert data["version"] == "1.0.0"
    assert data["artifact"] == artifact.name
    assert data["size_bytes"] == len(content)
    assert data["sha256"] == hashlib.sha256(content).hexdigest()
    assert data["sha256"] == sha256_file(artifact)
    assert data["integrity_only"] is True
    assert data["signature_verified"] is False


def test_manifest_refuses_missing_artifact(tmp_path):
    with pytest.raises(FileNotFoundError):
        write_release_manifest(
            tmp_path / "missing.exe",
            application_name="WindowsTechnician",
            version="1.0.0",
        )


def test_manifest_can_be_written_to_explicit_destination(tmp_path):
    artifact = tmp_path / "app.exe"
    artifact.write_bytes(b"artifact")
    destination = tmp_path / "metadata" / "release.json"

    result = write_release_manifest(
        artifact,
        application_name="WindowsTechnician",
        version="1.0.0",
        manifest_path=destination,
    )

    assert result == destination
    assert destination.is_file()
