import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from packaging.authenticode_verification import verify_authenticode_signature, write_verified_release_manifest
def test_signature_verification_uses_trusted_authenticode_policy(tmp_path):
    artifact = tmp_path / "app.exe"; artifact.write_bytes(b"artifact")
    tool = tmp_path / "signtool.exe"; tool.write_bytes(b"tool")
    calls = []
    def runner(command, **kwargs):
        calls.append((command, kwargs)); return SimpleNamespace(returncode=0, stdout="Successfully verified", stderr="")
    assert verify_authenticode_signature(artifact, signtool_path=tool, runner=runner) is True
    assert calls[0][0][1:5] == ["verify", "/pa", "/all", "/v"]
    assert calls[0][1]["check"] is False
def test_signature_verification_rejects_failed_verification(tmp_path):
    artifact = tmp_path / "app.exe"; artifact.write_bytes(b"unsigned")
    tool = tmp_path / "signtool.exe"; tool.write_bytes(b"tool")
    runner = lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="No signature")
    assert verify_authenticode_signature(artifact, signtool_path=tool, runner=runner) is False
def test_signature_verification_rejects_missing_artifact(tmp_path):
    assert verify_authenticode_signature(tmp_path / "missing.exe", signtool_path=tmp_path / "missing-tool.exe") is False
def test_verified_manifest_requires_successful_signature(tmp_path):
    artifact = tmp_path / "app.exe"; artifact.write_bytes(b"unsigned")
    tool = tmp_path / "signtool.exe"; tool.write_bytes(b"tool")
    runner = lambda *args, **kwargs: SimpleNamespace(returncode=1, stdout="", stderr="No signature")
    with pytest.raises(RuntimeError, match="verification failed"):
        write_verified_release_manifest(artifact, application_name="WindowsTechnician", version="1.0.0", signtool_path=tool, runner=runner)
    assert not artifact.with_suffix(".manifest.json").exists()
def test_verified_manifest_records_successful_verification(tmp_path):
    artifact = tmp_path / "app.exe"; artifact.write_bytes(b"signed-artifact")
    tool = tmp_path / "signtool.exe"; tool.write_bytes(b"tool")
    runner = lambda *args, **kwargs: SimpleNamespace(returncode=0, stdout="Successfully verified", stderr="")
    manifest = write_verified_release_manifest(artifact, application_name="WindowsTechnician", version="1.0.0", signtool_path=tool, runner=runner)
    data = json.loads(manifest.read_text(encoding="utf-8"))
    assert data["signature_verified"] is True
    assert data["integrity_only"] is False
    assert data["signature_verification"]["method"] == "SignTool verify /pa /all /v"
    assert data["sha256"]
