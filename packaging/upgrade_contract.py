"""Windows Technician upgrade contract."""

from dataclasses import dataclass

from packaging.application_metadata import APPLICATION_METADATA
from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class UpgradeContract:
    application_name: str
    current_version: str
    replace_application_files: bool
    replace_resources: bool
    preserve_configuration: bool
    preserve_logs: bool
    preserve_reports: bool
    preserve_shortcuts: bool
    allow_downgrade: bool

    def __post_init__(self):
        if self.application_name != APPLICATION_METADATA.display_name:
            raise ValueError(
                "Upgrade application identity must match metadata."
            )

        if self.current_version != APPLICATION_METADATA.version:
            raise ValueError(
                "Upgrade version must match application metadata."
            )


UPGRADE_CONTRACT = UpgradeContract(
    application_name=APPLICATION_METADATA.display_name,
    current_version=APPLICATION_METADATA.version,
    replace_application_files=True,
    replace_resources=True,
    preserve_configuration=(
        INSTALLER_CONTRACT.preserve_configuration_on_upgrade
    ),
    preserve_logs=True,
    preserve_reports=True,
    preserve_shortcuts=True,
    allow_downgrade=False,
)


def is_newer_version(
    installed_version: tuple[int, ...],
    candidate_version: tuple[int, ...],
) -> bool:
    return candidate_version > installed_version


def is_same_version(
    installed_version: tuple[int, ...],
    candidate_version: tuple[int, ...],
) -> bool:
    return candidate_version == installed_version


def is_downgrade(
    installed_version: tuple[int, ...],
    candidate_version: tuple[int, ...],
) -> bool:
    return candidate_version < installed_version


def upgrade_preserves_user_data() -> bool:
    return (
        UPGRADE_CONTRACT.preserve_configuration
        and UPGRADE_CONTRACT.preserve_logs
        and UPGRADE_CONTRACT.preserve_reports
    )
