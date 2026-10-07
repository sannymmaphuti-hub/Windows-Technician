"""Production diagnostic dataset environment boundary."""

from dataclasses import dataclass
from enum import Enum


class DiagnosticDatasetLevel(str, Enum):
    EMPTY = "EMPTY"
    NORMAL = "NORMAL"
    LARGE = "LARGE"
    STRESS = "STRESS"


@dataclass(frozen=True)
class DiagnosticDatasetEnvironment:
    item_count: int

    def __post_init__(self) -> None:
        if not isinstance(self.item_count, int):
            raise TypeError("item_count must be an integer.")

        if isinstance(self.item_count, bool):
            raise TypeError("item_count must be an integer.")

        if self.item_count < 0:
            raise ValueError("item_count must not be negative.")


@dataclass(frozen=True)
class DiagnosticDatasetCompatibilityResult:
    compatible: bool
    level: DiagnosticDatasetLevel
    reason: str

    def __post_init__(self) -> None:
        if not isinstance(self.compatible, bool):
            raise TypeError("compatible must be a boolean.")

        if not isinstance(self.level, DiagnosticDatasetLevel):
            raise TypeError(
                "level must be a DiagnosticDatasetLevel."
            )

        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("reason must be a non-empty string.")


NORMAL_DATASET_MAX_ITEMS = 100
LARGE_DATASET_MAX_ITEMS = 1_000
STRESS_DATASET_MAX_ITEMS = 10_000


def classify_diagnostic_dataset(
    environment: DiagnosticDatasetEnvironment,
) -> DiagnosticDatasetLevel:
    """Classify the size of a diagnostic dataset."""

    if not isinstance(environment, DiagnosticDatasetEnvironment):
        raise TypeError(
            "environment must be a DiagnosticDatasetEnvironment."
        )

    count = environment.item_count

    if count == 0:
        return DiagnosticDatasetLevel.EMPTY

    if count <= NORMAL_DATASET_MAX_ITEMS:
        return DiagnosticDatasetLevel.NORMAL

    if count <= LARGE_DATASET_MAX_ITEMS:
        return DiagnosticDatasetLevel.LARGE

    return DiagnosticDatasetLevel.STRESS


def evaluate_diagnostic_dataset_compatibility(
    environment: DiagnosticDatasetEnvironment,
) -> DiagnosticDatasetCompatibilityResult:
    """Evaluate whether a diagnostic dataset is supported."""

    level = classify_diagnostic_dataset(environment)

    if level is DiagnosticDatasetLevel.EMPTY:
        return DiagnosticDatasetCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "Empty diagnostic dataset is supported; "
                "the application should present a no-findings state."
            ),
        )

    if level is DiagnosticDatasetLevel.NORMAL:
        return DiagnosticDatasetCompatibilityResult(
            compatible=True,
            level=level,
            reason="Normal diagnostic dataset is supported.",
        )

    if level is DiagnosticDatasetLevel.LARGE:
        return DiagnosticDatasetCompatibilityResult(
            compatible=True,
            level=level,
            reason=(
                "Large diagnostic dataset is supported within "
                "the normal large-dataset performance boundary."
            ),
        )

    return DiagnosticDatasetCompatibilityResult(
        compatible=True,
        level=level,
        reason=(
            "Stress diagnostic dataset is supported within "
            "the production stress boundary."
        ),
    )


def diagnostic_dataset_compatibility_is_safe(
    environment: DiagnosticDatasetEnvironment,
) -> bool:
    """Return whether the diagnostic dataset is safe to process."""

    return evaluate_diagnostic_dataset_compatibility(environment).compatible
