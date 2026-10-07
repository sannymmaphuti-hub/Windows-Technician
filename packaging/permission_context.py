"""Windows permission and privilege boundary."""

from dataclasses import dataclass
import ctypes
import os


@dataclass(frozen=True)
class PermissionContext:
    user_name: str
    is_admin: bool
    is_elevated: bool
    can_write_program_files: bool
    can_write_system_directory: bool

    @property
    def has_privileged_access(self) -> bool:
        return self.is_admin and self.is_elevated


def _detect_admin() -> bool:
    if os.name != "nt":
        return False

    try:
        return bool(
            ctypes.windll.shell32.IsUserAnAdmin()
        )
    except (AttributeError, OSError):
        return False


def _test_write_access(path: str) -> bool:
    if os.name != "nt":
        return False

    try:
        test_path = os.path.join(
            path,
            ".windows_technician_permission_test",
        )

        with open(
            test_path,
            "a",
            encoding="utf-8",
        ):
            pass

        os.remove(test_path)

        return True

    except (OSError, PermissionError):
        return False


def detect_permission_context() -> PermissionContext:
    user_name = os.environ.get(
        "USERNAME",
        os.environ.get("USER", "unknown"),
    )

    is_admin = _detect_admin()

    return PermissionContext(
        user_name=user_name,
        is_admin=is_admin,
        is_elevated=is_admin,
        can_write_program_files=_test_write_access(
            os.environ.get(
                "ProgramFiles",
                r"C:\Program Files",
            )
        ),
        can_write_system_directory=_test_write_access(
            os.environ.get(
                "SystemRoot",
                r"C:\Windows",
            )
        ),
    )


def permission_context_is_valid(
    context: PermissionContext,
) -> bool:
    if not isinstance(
        context,
        PermissionContext,
    ):
        raise TypeError(
            "context must be a PermissionContext."
        )

    return bool(
        context.user_name.strip()
    )
