import pytest

from packaging.memory_environment import (
    HIGH_MEMORY_THRESHOLD_BYTES,
    LOW_MEMORY_THRESHOLD_BYTES,
    MemoryCompatibilityResult,
    MemoryEnvironment,
    MemoryEnvironmentLevel,
    classify_memory_environment,
    evaluate_memory_compatibility,
    memory_compatibility_is_safe,
)


def make_memory(gigabytes: int) -> MemoryEnvironment:
    return MemoryEnvironment(
        total_memory_bytes=gigabytes * 1024 * 1024 * 1024
    )


def test_low_memory_is_classified_correctly():
    environment = make_memory(2)

    assert (
        classify_memory_environment(environment)
        is MemoryEnvironmentLevel.LOW
    )


def test_standard_memory_is_classified_correctly():
    environment = make_memory(8)

    assert (
        classify_memory_environment(environment)
        is MemoryEnvironmentLevel.STANDARD
    )


def test_high_memory_is_classified_correctly():
    environment = make_memory(32)

    assert (
        classify_memory_environment(environment)
        is MemoryEnvironmentLevel.HIGH
    )


def test_zero_memory_is_unknown():
    environment = MemoryEnvironment(total_memory_bytes=0)

    assert (
        classify_memory_environment(environment)
        is MemoryEnvironmentLevel.UNKNOWN
    )


def test_low_memory_is_supported():
    result = evaluate_memory_compatibility(make_memory(2))

    assert result.compatible
    assert result.level is MemoryEnvironmentLevel.LOW
    assert memory_compatibility_is_safe(make_memory(2))


def test_standard_memory_is_supported():
    result = evaluate_memory_compatibility(make_memory(8))

    assert result.compatible
    assert result.level is MemoryEnvironmentLevel.STANDARD
    assert memory_compatibility_is_safe(make_memory(8))


def test_high_memory_is_supported():
    result = evaluate_memory_compatibility(make_memory(32))

    assert result.compatible
    assert result.level is MemoryEnvironmentLevel.HIGH
    assert memory_compatibility_is_safe(make_memory(32))


def test_zero_memory_is_not_safe():
    result = evaluate_memory_compatibility(
        MemoryEnvironment(total_memory_bytes=0)
    )

    assert not result.compatible
    assert result.level is MemoryEnvironmentLevel.UNKNOWN
    assert not memory_compatibility_is_safe(
        MemoryEnvironment(total_memory_bytes=0)
    )


def test_low_memory_threshold_is_low():
    environment = MemoryEnvironment(
        total_memory_bytes=LOW_MEMORY_THRESHOLD_BYTES - 1
    )

    assert (
        classify_memory_environment(environment)
        is MemoryEnvironmentLevel.LOW
    )


def test_low_memory_threshold_is_standard():
    environment = MemoryEnvironment(
        total_memory_bytes=LOW_MEMORY_THRESHOLD_BYTES
    )

    assert (
        classify_memory_environment(environment)
        is MemoryEnvironmentLevel.STANDARD
    )


def test_high_memory_threshold_is_high():
    environment = MemoryEnvironment(
        total_memory_bytes=HIGH_MEMORY_THRESHOLD_BYTES
    )

    assert (
        classify_memory_environment(environment)
        is MemoryEnvironmentLevel.HIGH
    )


def test_memory_environment_rejects_negative_values():
    with pytest.raises(ValueError):
        MemoryEnvironment(total_memory_bytes=-1)


def test_memory_environment_rejects_non_integer_values():
    with pytest.raises(TypeError):
        MemoryEnvironment(total_memory_bytes=8.0)


def test_memory_environment_rejects_boolean_values():
    with pytest.raises(TypeError):
        MemoryEnvironment(total_memory_bytes=True)


def test_classification_requires_memory_environment():
    with pytest.raises(TypeError):
        classify_memory_environment(8)


def test_result_requires_boolean_compatibility():
    with pytest.raises(TypeError):
        MemoryCompatibilityResult(
            compatible="yes",
            level=MemoryEnvironmentLevel.STANDARD,
            reason="invalid",
        )


def test_result_requires_valid_level():
    with pytest.raises(TypeError):
        MemoryCompatibilityResult(
            compatible=True,
            level="STANDARD",
            reason="invalid",
        )


def test_result_requires_reason():
    with pytest.raises(ValueError):
        MemoryCompatibilityResult(
            compatible=True,
            level=MemoryEnvironmentLevel.STANDARD,
            reason="",
        )


def test_memory_environment_is_immutable():
    environment = make_memory(8)

    with pytest.raises(AttributeError):
        environment.total_memory_bytes = 16


def test_result_is_immutable():
    result = evaluate_memory_compatibility(make_memory(8))

    with pytest.raises(AttributeError):
        result.compatible = False
