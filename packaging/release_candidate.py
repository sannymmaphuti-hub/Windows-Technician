"""Release candidate identity and contract."""

from dataclasses import dataclass
from enum import Enum

from packaging.application_metadata import APPLICATION_METADATA, ApplicationMetadata


class ReleaseCandidateState(str, Enum):
    NOT_READY = "NOT_READY"
    READY = "READY"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True)
class ReleaseCandidateIdentity:
    application_name: str
    display_name: str
    version: str
    release_channel: str
    executable_name: str
    package_name: str

    def __post_init__(self) -> None:
        fields = (
            self.application_name,
            self.display_name,
            self.version,
            self.release_channel,
            self.executable_name,
            self.package_name,
        )

        if any(not isinstance(value, str) or not value.strip() for value in fields):
            raise ValueError("All release candidate identity fields must be non-empty strings.")


@dataclass(frozen=True)
class ReleaseCandidateContract:
    identity: ReleaseCandidateIdentity
    required_components: tuple[str, ...]
    state: ReleaseCandidateState = ReleaseCandidateState.NOT_READY

    def __post_init__(self) -> None:
        if not isinstance(self.identity, ReleaseCandidateIdentity):
            raise TypeError("identity must be a ReleaseCandidateIdentity.")

        if not isinstance(self.required_components, tuple):
            raise TypeError("required_components must be a tuple.")

        if not self.required_components:
            raise ValueError("required_components must not be empty.")

        if any(
            not isinstance(component, str) or not component.strip()
            for component in self.required_components
        ):
            raise ValueError("required_components must contain non-empty strings.")

        if not isinstance(self.state, ReleaseCandidateState):
            raise TypeError("state must be a ReleaseCandidateState.")


def release_candidate_identity_from_metadata(
    metadata: ApplicationMetadata = APPLICATION_METADATA,
) -> ReleaseCandidateIdentity:
    if not isinstance(metadata, ApplicationMetadata):
        raise TypeError("metadata must be an ApplicationMetadata.")

    return ReleaseCandidateIdentity(
        application_name=metadata.name,
        display_name=metadata.display_name,
        version=metadata.version,
        release_channel=metadata.release_channel,
        executable_name=metadata.executable_name,
        package_name=metadata.package_name,
    )


RELEASE_CANDIDATE_IDENTITY = release_candidate_identity_from_metadata()

RELEASE_CANDIDATE_REQUIRED_COMPONENTS = (
    "application",
    "diagnostics",
    "engine",
    "gui",
    "packaging",
    "resources",
)

RELEASE_CANDIDATE_CONTRACT = ReleaseCandidateContract(
    identity=RELEASE_CANDIDATE_IDENTITY,
    required_components=RELEASE_CANDIDATE_REQUIRED_COMPONENTS,
)


def release_candidate_contract_is_valid(
    contract: ReleaseCandidateContract = RELEASE_CANDIDATE_CONTRACT,
) -> bool:
    if not isinstance(contract, ReleaseCandidateContract):
        return False

    identity = contract.identity

    return (
        identity.application_name == APPLICATION_METADATA.name
        and identity.display_name == APPLICATION_METADATA.display_name
        and identity.version == APPLICATION_METADATA.version
        and identity.release_channel == APPLICATION_METADATA.release_channel
        and identity.executable_name == APPLICATION_METADATA.executable_name
        and identity.package_name == APPLICATION_METADATA.package_name
        and bool(contract.required_components)
    )
