"""Windows Technician uninstall contract."""

from dataclasses import dataclass
from pathlib import Path

from packaging.installer_contract import INSTALLER_CONTRACT


@dataclass(frozen=True)
class UninstallContract:
    remove_application_files: bool
    remove_resources: bool
    remove_start_menu_shortcut: bool
    remove_desktop_shortcut: bool
    preserve_configuration: bool
    preserve_logs: bool
    preserve_reports: bool
    require_explicit_user_data_confirmation: bool

    def __post_init__(self):
        boolean_fields = (
            "remove_application_files",
            "remove_resources",
            "remove_start_menu_shortcut",
            "remove_desktop_shortcut",
            "preserve_configuration",
            "preserve_logs",
            "preserve_reports",
            "require_explicit_user_data_confirmation",
        )

        for field_name in boolean_fields:
            if not isinstance(getattr(self, field_name), bool):
                raise TypeError(
                    f"{field_name} must be a boolean."
                )


UNINSTALL_CONTRACT = UninstallContract(
    remove_application_files=True,
    remove_resources=True,
    remove_start_menu_shortcut=True,
    remove_desktop_shortcut=True,
    preserve_configuration=(
        INSTALLER_CONTRACT.preserve_configuration_on_uninstall
    ),
    preserve_logs=True,
    preserve_reports=True,
    require_explicit_user_data_confirmation=True,
)


def user_data_may_be_removed(
    explicit_confirmation: bool,
) -> bool:
    return bool(explicit_confirmation)


def uninstall_preserves_user_data_by_default() -> bool:
    return (
        UNINSTALL_CONTRACT.preserve_configuration
        and UNINSTALL_CONTRACT.preserve_logs
        and UNINSTALL_CONTRACT.preserve_reports
    )


def uninstall_is_application_only_by_default() -> bool:
    return (
        uninstall_preserves_user_data_by_default()
        and UNINSTALL_CONTRACT.require_explicit_user_data_confirmation
    )
