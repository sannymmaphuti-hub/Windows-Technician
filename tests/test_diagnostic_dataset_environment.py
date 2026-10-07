import pytest

from packaging.diagnostic_dataset_environment import (
    LARGE_DATASET_MAX_ITEMS,
    NORMAL_DATASET_MAX_ITEMS,
    STRESS_DATASET_MAX_ITEMS,
    DiagnosticDatasetCompatibilityResult,
    DiagnosticDatasetEnvironment,
    DiagnosticDatasetLevel,
    classify_diagnostic_dataset,
    diagnostic_dataset_compatibility_is_safe,
    evaluate_diagnostic_dataset_compatibility,
)


def make_dataset(count: int) -> DiagnosticDatasetEnvironment:
    return DiagnosticDatasetEnvironment(item_count=count)


def test_empty_dataset_is_classified():
    assert (
        classify_diagnostic_dataset(make_dataset(0))
        is DiagnosticDatasetLevel.EMPTY
    )


def test_normal_dataset_is_classified():
    assert (
        classify_diagnostic_dataset(make_dataset(50))
        is DiagnosticDatasetLevel.NORMAL
    )


def test_large_dataset_is_classified():
    assert (
        classify_diagnostic_dataset(make_dataset(500))
        is DiagnosticDatasetLevel.LARGE
    )


def test_stress_dataset_is_classified():
    assert (
        classify_diagnostic_dataset(make_dataset(10_000))
        is DiagnosticDatasetLevel.STRESS
    )


def test_dataset_above_stress_boundary_is_stress():
    assert (
        classify_diagnostic_dataset(make_dataset(10_001))
        is DiagnosticDatasetLevel.STRESS
    )


def test_empty_dataset_is_supported():
    result = evaluate_diagnostic_dataset_compatibility(
        make_dataset(0)
    )

    assert result.compatible
    assert result.level is DiagnosticDatasetLevel.EMPTY
    assert diagnostic_dataset_compatibility_is_safe(
        make_dataset(0)
    )


def test_normal_dataset_is_supported():
    result = evaluate_diagnostic_dataset_compatibility(
        make_dataset(NORMAL_DATASET_MAX_ITEMS)
    )

    assert result.compatible
    assert result.level is DiagnosticDatasetLevel.NORMAL


def test_large_dataset_is_supported():
    result = evaluate_diagnostic_dataset_compatibility(
        make_dataset(LARGE_DATASET_MAX_ITEMS)
    )

    assert result.compatible
    assert result.level is DiagnosticDatasetLevel.LARGE


def test_stress_boundary_is_stress():
    result = evaluate_diagnostic_dataset_compatibility(
        make_dataset(STRESS_DATASET_MAX_ITEMS)
    )

    assert result.compatible
    assert result.level is DiagnosticDatasetLevel.STRESS


def test_stress_dataset_is_supported():
    result = evaluate_diagnostic_dataset_compatibility(
        make_dataset(STRESS_DATASET_MAX_ITEMS + 1)
    )

    assert result.compatible
    assert result.level is DiagnosticDatasetLevel.STRESS


def test_negative_count_is_rejected():
    with pytest.raises(ValueError):
        DiagnosticDatasetEnvironment(item_count=-1)


def test_non_integer_count_is_rejected():
    with pytest.raises(TypeError):
        DiagnosticDatasetEnvironment(item_count=10.5)


def test_boolean_count_is_rejected():
    with pytest.raises(TypeError):
        DiagnosticDatasetEnvironment(item_count=True)


def test_classification_requires_dataset_environment():
    with pytest.raises(TypeError):
        classify_diagnostic_dataset([])


def test_result_requires_boolean_compatibility():
    with pytest.raises(TypeError):
        DiagnosticDatasetCompatibilityResult(
            compatible="yes",
            level=DiagnosticDatasetLevel.NORMAL,
            reason="invalid",
        )


def test_result_requires_valid_level():
    with pytest.raises(TypeError):
        DiagnosticDatasetCompatibilityResult(
            compatible=True,
            level="NORMAL",
            reason="invalid",
        )


def test_result_requires_reason():
    with pytest.raises(ValueError):
        DiagnosticDatasetCompatibilityResult(
            compatible=True,
            level=DiagnosticDatasetLevel.NORMAL,
            reason="",
        )


def test_dataset_environment_is_immutable():
    environment = make_dataset(10)

    with pytest.raises(AttributeError):
        environment.item_count = 20


def test_result_is_immutable():
    result = evaluate_diagnostic_dataset_compatibility(
        make_dataset(10)
    )

    with pytest.raises(AttributeError):
        result.compatible = False
