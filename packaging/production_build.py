"""Production Windows application build boundary."""

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess

from packaging.application_metadata import APPLICATION_METADATA
from packaging.package_manifest import (
    PRODUCTION_PACKAGE_MANIFEST,
    manifest_path,
    required_files_exist,
)
from packaging.resources import RESOURCE_ROOT


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BUILD_ROOT = PROJECT_ROOT / "build"
DIST_ROOT = PROJECT_ROOT / "dist"


@dataclass(frozen=True)
class ProductionBuildContract:
    """Canonical contract for producing the Windows onedir application."""

    application_name: str
    version: str
    entry_point: str
    executable_name: str
    project_root: Path
    build_root: Path
    distribution_root: Path
    resource_root: Path

    def __post_init__(self):
        if self.application_name != APPLICATION_METADATA.display_name:
            raise ValueError(
                "Build application name must match application metadata."
            )

        if self.version != APPLICATION_METADATA.version:
            raise ValueError(
                "Build version must match application metadata."
            )

        if self.entry_point != PRODUCTION_PACKAGE_MANIFEST.entry_point:
            raise ValueError(
                "Build entry point must match the production package manifest."
            )

        if self.executable_name != APPLICATION_METADATA.executable_name:
            raise ValueError(
                "Build executable name must match application metadata."
            )

        for field_name in (
            "project_root",
            "build_root",
            "distribution_root",
            "resource_root",
        ):
            if not isinstance(getattr(self, field_name), Path):
                raise TypeError(f"{field_name} must be a Path.")


PRODUCTION_BUILD_CONTRACT = ProductionBuildContract(
    application_name=APPLICATION_METADATA.display_name,
    version=APPLICATION_METADATA.version,
    entry_point=PRODUCTION_PACKAGE_MANIFEST.entry_point,
    executable_name=APPLICATION_METADATA.executable_name,
    project_root=PROJECT_ROOT,
    build_root=BUILD_ROOT,
    distribution_root=DIST_ROOT,
    resource_root=RESOURCE_ROOT,
)


def render_windows_version_info() -> str:
    """Render PyInstaller-compatible Windows executable version resources."""
    version = APPLICATION_METADATA.version_tuple
    version_string = ".".join(str(part) for part in version)

    return f"""VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={version + (0,) if len(version) == 3 else version},
    prodvers={version + (0,) if len(version) == 3 else version},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable(
        '040904B0',
        [
          StringStruct('FileDescription', {APPLICATION_METADATA.display_name!r}),
          StringStruct('FileVersion', {version_string!r}),
          StringStruct('InternalName', {APPLICATION_METADATA.name!r}),
          StringStruct('OriginalFilename', {APPLICATION_METADATA.executable_name!r}),
          StringStruct('ProductName', {APPLICATION_METADATA.display_name!r}),
          StringStruct('ProductVersion', {version_string!r})
        ]
      )
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def windows_version_info_path(
    contract: ProductionBuildContract = PRODUCTION_BUILD_CONTRACT,
) -> Path:
    """Return the generated Windows version-resource file path."""
    if not isinstance(contract, ProductionBuildContract):
        raise TypeError("contract must be a ProductionBuildContract.")
    return contract.build_root / "windows_version_info.txt"

@dataclass(frozen=True)
class BuildValidationResult:
    """Result of validating the production build boundary."""

    valid: bool
    errors: tuple[str, ...] = ()

    def __post_init__(self):
        if not isinstance(self.valid, bool):
            raise TypeError("valid must be a boolean.")

        if not isinstance(self.errors, tuple):
            raise TypeError("errors must be a tuple.")

        for error in self.errors:
            if not isinstance(error, str) or not error.strip():
                raise ValueError(
                    "Build validation errors must be non-empty strings."
                )


@dataclass(frozen=True)
class BuildResult:
    """Result of a production executable build."""

    success: bool
    executable: Path | None
    return_code: int | None
    stdout: str
    stderr: str
    validation: BuildValidationResult

    def __post_init__(self):
        if not isinstance(self.success, bool):
            raise TypeError("success must be a boolean.")

        if self.executable is not None and not isinstance(
            self.executable, Path
        ):
            raise TypeError("executable must be a Path or None.")

        if self.return_code is not None and not isinstance(
            self.return_code, int
        ):
            raise TypeError("return_code must be an integer or None.")

        if not isinstance(self.stdout, str):
            raise TypeError("stdout must be a string.")

        if not isinstance(self.stderr, str):
            raise TypeError("stderr must be a string.")

        if not isinstance(self.validation, BuildValidationResult):
            raise TypeError(
                "validation must be a BuildValidationResult."
            )


def build_executable_path(
    contract: ProductionBuildContract = PRODUCTION_BUILD_CONTRACT,
) -> Path:
    """Return the canonical executable artifact path."""
    if not isinstance(contract, ProductionBuildContract):
        raise TypeError(
            "contract must be a ProductionBuildContract."
        )

    return contract.distribution_root / contract.executable_name.removesuffix(".exe") / contract.executable_name


def validate_build_inputs(
    contract: ProductionBuildContract = PRODUCTION_BUILD_CONTRACT,
) -> BuildValidationResult:
    """Validate all source-side requirements before building."""

    if not isinstance(contract, ProductionBuildContract):
        raise TypeError(
            "contract must be a ProductionBuildContract."
        )

    errors: list[str] = []

    if not contract.project_root.is_dir():
        errors.append("Project root does not exist.")

    entry_point = manifest_path(contract.entry_point)

    if not entry_point.is_file():
        errors.append(
            f"Production entry point does not exist: {contract.entry_point}"
        )

    if not required_files_exist():
        errors.append(
            "One or more production manifest required files are missing."
        )

    for directory in PRODUCTION_PACKAGE_MANIFEST.package_directories:
        path = manifest_path(directory)
        if not path.is_dir():
            errors.append(
                f"Required package directory does not exist: {directory}"
            )

    for directory in PRODUCTION_PACKAGE_MANIFEST.resource_directories:
        path = manifest_path(directory)
        if not path.is_dir():
            errors.append(
                f"Required resource directory does not exist: {directory}"
            )

    if contract.resource_root != RESOURCE_ROOT:
        errors.append(
            "Build resource root does not match canonical resource root."
        )

    return BuildValidationResult(
        valid=not errors,
        errors=tuple(errors),
    )


def validate_build_artifact(
    contract: ProductionBuildContract = PRODUCTION_BUILD_CONTRACT,
) -> BuildValidationResult:
    """Validate the executable produced by the build."""

    executable = build_executable_path(contract)
    errors: list[str] = []

    if not executable.exists():
        errors.append(
            f"Build artifact does not exist: {executable}"
        )
    elif not executable.is_file():
        errors.append(
            f"Build artifact is not a file: {executable}"
        )
    elif executable.stat().st_size <= 0:
        errors.append(
            f"Build artifact is empty: {executable}"
        )

    return BuildValidationResult(
        valid=not errors,
        errors=tuple(errors),
    )


def _pyinstaller_available() -> bool:
    """Return whether PyInstaller is available to the current Python."""
    BUILD_ROOT.mkdir(parents=True, exist_ok=True)

    result = subprocess.run(
        ["py", "-m", "PyInstaller", "--version"],
        cwd=BUILD_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    return result.returncode == 0


def build_production_executable(
    *,
    contract: ProductionBuildContract = PRODUCTION_BUILD_CONTRACT,
    clean: bool = True,
) -> BuildResult:
    """
    Build the production Windows executable.

    PyInstaller is deliberately launched from the build boundary rather
    than the source-tree root so the project's ``packaging`` namespace
    cannot shadow PyInstaller's external ``packaging`` dependency.
    """
    validation = validate_build_inputs(contract)

    if not validation.valid:
        return BuildResult(
            success=False,
            executable=None,
            return_code=None,
            stdout="",
            stderr="",
            validation=validation,
        )

    if clean:
        shutil.rmtree(contract.build_root, ignore_errors=True)
        shutil.rmtree(contract.distribution_root, ignore_errors=True)

    contract.build_root.mkdir(parents=True, exist_ok=True)
    contract.distribution_root.mkdir(parents=True, exist_ok=True)

    if not _pyinstaller_available():
        unavailable = BuildValidationResult(
            valid=False,
            errors=(
                "PyInstaller is not available to the current Python "
                "from the build boundary.",
            ),
        )

        return BuildResult(
            success=False,
            executable=None,
            return_code=None,
            stdout="",
            stderr="",
            validation=unavailable,
        )

    version_info = windows_version_info_path(contract)
    version_info.write_text(
        render_windows_version_info(),
        encoding="utf-8",
    )

    command = [
        "py",
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onedir",
        "--version-file",
        str(version_info),
        "--name",
        contract.executable_name.removesuffix(".exe"),
        "--distpath",
        str(contract.distribution_root),
        "--workpath",
        str(contract.build_root),
        "--specpath",
        str(contract.build_root),
        str(contract.project_root / contract.entry_point),
    ]

    completed = subprocess.run(
        command,
        cwd=contract.build_root,
        capture_output=True,
        text=True,
        check=False,
    )

    artifact_validation = validate_build_artifact(contract)

    success = (
        completed.returncode == 0
        and artifact_validation.valid
    )

    return BuildResult(
        success=success,
        executable=(
            build_executable_path(contract)
            if artifact_validation.valid
            else None
        ),
        return_code=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        validation=artifact_validation,
    )


