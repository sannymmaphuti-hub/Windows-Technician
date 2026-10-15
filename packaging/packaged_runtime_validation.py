"""Packaged Windows Technician runtime validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
import time

from packaging.production_build import build_executable_path


@dataclass(frozen=True)
class PackagedRuntimeValidationResult:
    """Result of a packaged application runtime smoke test."""

    started: bool
    survived_startup: bool
    terminated: bool
    return_code: int | None
    executable: Path
    errors: tuple[str, ...] = ()


def validate_packaged_runtime(
    *,
    startup_timeout: float = 8.0,
    shutdown_timeout: float = 5.0,
) -> PackagedRuntimeValidationResult:
    """Launch the packaged executable and validate its startup boundary."""

    executable = build_executable_path()
    errors: list[str] = []

    if not executable.exists():
        return PackagedRuntimeValidationResult(
            started=False,
            survived_startup=False,
            terminated=False,
            return_code=None,
            executable=executable,
            errors=(f"Packaged executable does not exist: {executable}",),
        )

    if not executable.is_file():
        return PackagedRuntimeValidationResult(
            started=False,
            survived_startup=False,
            terminated=False,
            return_code=None,
            executable=executable,
            errors=(f"Packaged executable is not a file: {executable}",),
        )

    process: subprocess.Popen[bytes] | None = None

    try:
        process = subprocess.Popen(
            [str(executable)],
            cwd=str(executable.parent),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError as exc:
        return PackagedRuntimeValidationResult(
            started=False,
            survived_startup=False,
            terminated=False,
            return_code=None,
            executable=executable,
            errors=(f"Failed to launch packaged executable: {exc}",),
        )

    started = process.poll() is None or process.returncode is not None

    deadline = time.monotonic() + startup_timeout

    while time.monotonic() < deadline:
        if process.poll() is not None:
            break
        time.sleep(0.1)

    survived_startup = process.poll() is None

    if not survived_startup:
        return_code = process.returncode
        errors.append(
            f"Packaged executable exited during startup with return code {return_code}."
        )
        return PackagedRuntimeValidationResult(
            started=started,
            survived_startup=False,
            terminated=True,
            return_code=return_code,
            executable=executable,
            errors=tuple(errors),
        )

    process.terminate()

    try:
        return_code = process.wait(timeout=shutdown_timeout)
        terminated = True
    except subprocess.TimeoutExpired:
        process.kill()
        return_code = process.wait(timeout=shutdown_timeout)
        terminated = True


    return PackagedRuntimeValidationResult(
        started=started,
        survived_startup=True,
        terminated=terminated,
        return_code=return_code,
        executable=executable,
        errors=tuple(errors),
    )
