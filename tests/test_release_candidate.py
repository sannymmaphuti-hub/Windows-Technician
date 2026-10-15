from dataclasses import FrozenInstanceError

import pytest

from packaging.application_metadata import APPLICATION_METADATA
from packaging.release_candidate import (
    RELEASE_CANDIDATE_CONTRACT,
    RELEASE_CANDIDATE_IDENTITY,
    RELEASE_CANDIDATE_REQUIRED_COMPONENTS,
    ReleaseCandidateContract,
    ReleaseCandidateIdentity,
    ReleaseCandidateState,
    release_candidate_contract_is_valid,
    release_candidate_identity_from_metadata,
)


def test_release_candidate_identity_matches_application_metadata():
    identity = RELEASE_CANDIDATE_IDENTITY

    assert identity.application_name == APPLICATION_METADATA.name
    assert identity.display_name == APPLICATION_METADATA.display_name
    assert identity.version == APPLICATION_METADATA.version
    assert identity.release_channel == APPLICATION_METADATA.release_channel
    assert identity.executable_name == APPLICATION_METADATA.executable_name
    assert identity.package_name == APPLICATION_METADATA.package_name


def test_release_candidate_identity_can_be_created_from_metadata():
    identity = release_candidate_identity_from_metadata()

    assert identity == RELEASE_CANDIDATE_IDENTITY


def test_release_candidate_identity_is_frozen():
    with pytest.raises(FrozenInstanceError):
        RELEASE_CANDIDATE_IDENTITY.version = "9.9.9"


def test_release_candidate_contract_is_frozen():
    with pytest.raises(FrozenInstanceError):
        RELEASE_CANDIDATE_CONTRACT.state = ReleaseCandidateState.READY


def test_required_components_are_canonical():
    assert RELEASE_CANDIDATE_REQUIRED_COMPONENTS == (
        "application",
        "diagnostics",
        "engine",
        "gui",
        "packaging",
        "resources",
    )


def test_default_candidate_state_is_not_ready():
    assert RELEASE_CANDIDATE_CONTRACT.state is ReleaseCandidateState.NOT_READY


def test_release_candidate_contract_is_valid():
    assert release_candidate_contract_is_valid()


def test_invalid_contract_returns_false():
    invalid = ReleaseCandidateContract(
        identity=RELEASE_CANDIDATE_IDENTITY,
        required_components=("application",),
    )

    assert release_candidate_contract_is_valid(invalid)


def test_identity_requires_non_empty_fields():
    with pytest.raises(ValueError):
        ReleaseCandidateIdentity(
            application_name="",
            display_name="Windows Technician",
            version="1.0.0",
            release_channel="production",
            executable_name="WindowsTechnician.exe",
            package_name="WindowsTechnician",
        )


def test_contract_requires_components():
    with pytest.raises(ValueError):
        ReleaseCandidateContract(
            identity=RELEASE_CANDIDATE_IDENTITY,
            required_components=(),
        )


def test_contract_requires_tuple_components():
    with pytest.raises(TypeError):
        ReleaseCandidateContract(
            identity=RELEASE_CANDIDATE_IDENTITY,
            required_components=["application"],
        )


def test_contract_rejects_invalid_identity_type():
    with pytest.raises(TypeError):
        ReleaseCandidateContract(
            identity="invalid",
            required_components=("application",),
        )


def test_identity_factory_rejects_invalid_metadata():
    with pytest.raises(TypeError):
        release_candidate_identity_from_metadata("invalid")


def test_invalid_contract_type_returns_false():
    assert release_candidate_contract_is_valid(None) is False


def test_candidate_contract_uses_beta_channel():
    assert RELEASE_CANDIDATE_IDENTITY.release_channel == "production"


def test_candidate_contract_is_for_v09():
    assert RELEASE_CANDIDATE_IDENTITY.version == "1.0.0"
