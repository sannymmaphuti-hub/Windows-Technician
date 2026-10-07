import pytest

from packaging.display_environment import (
    HIGH_DPI_THRESHOLD_PERCENT,
    LARGE_HEIGHT,
    LARGE_WIDTH,
    MIN_SUPPORTED_HEIGHT,
    MIN_SUPPORTED_WIDTH,
    DisplayCompatibilityResult,
    DisplayEnvironment,
    DisplayEnvironmentLevel,
    classify_display_environment,
    display_compatibility_is_safe,
    evaluate_display_compatibility,
)


def test_small_display_is_classified():
    environment = DisplayEnvironment(
        width_pixels=800,
        height_pixels=600,
        dpi_scale_percent=100,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.SMALL,
    )


def test_standard_display_is_classified():
    environment = DisplayEnvironment(
        width_pixels=1920,
        height_pixels=1080,
        dpi_scale_percent=100,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.STANDARD,
    )


def test_large_display_is_classified():
    environment = DisplayEnvironment(
        width_pixels=3840,
        height_pixels=2160,
        dpi_scale_percent=100,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.LARGE,
    )


def test_high_dpi_display_is_classified():
    environment = DisplayEnvironment(
        width_pixels=1920,
        height_pixels=1080,
        dpi_scale_percent=150,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.STANDARD,
        DisplayEnvironmentLevel.HIGH_DPI,
    )


def test_small_high_dpi_display_has_both_levels():
    environment = DisplayEnvironment(
        width_pixels=800,
        height_pixels=600,
        dpi_scale_percent=200,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.SMALL,
        DisplayEnvironmentLevel.HIGH_DPI,
    )


def test_zero_display_information_is_unknown():
    environment = DisplayEnvironment(
        width_pixels=0,
        height_pixels=0,
        dpi_scale_percent=0,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.UNKNOWN,
    )


def test_small_display_is_supported():
    result = evaluate_display_compatibility(
        DisplayEnvironment(
            width_pixels=800,
            height_pixels=600,
            dpi_scale_percent=100,
        )
    )

    assert result.compatible
    assert DisplayEnvironmentLevel.SMALL in result.levels
    assert display_compatibility_is_safe(
        DisplayEnvironment(
            width_pixels=800,
            height_pixels=600,
            dpi_scale_percent=100,
        )
    )


def test_high_dpi_display_is_supported():
    result = evaluate_display_compatibility(
        DisplayEnvironment(
            width_pixels=1920,
            height_pixels=1080,
            dpi_scale_percent=HIGH_DPI_THRESHOLD_PERCENT,
        )
    )

    assert result.compatible
    assert DisplayEnvironmentLevel.HIGH_DPI in result.levels


def test_unknown_display_is_not_safe():
    environment = DisplayEnvironment(
        width_pixels=0,
        height_pixels=0,
        dpi_scale_percent=0,
    )

    result = evaluate_display_compatibility(environment)

    assert not result.compatible
    assert result.levels == (DisplayEnvironmentLevel.UNKNOWN,)
    assert not display_compatibility_is_safe(environment)


def test_width_boundary():
    small = DisplayEnvironment(
        width_pixels=MIN_SUPPORTED_WIDTH - 1,
        height_pixels=1080,
        dpi_scale_percent=100,
    )
    standard = DisplayEnvironment(
        width_pixels=MIN_SUPPORTED_WIDTH,
        height_pixels=1080,
        dpi_scale_percent=100,
    )

    assert DisplayEnvironmentLevel.SMALL in classify_display_environment(small)
    assert DisplayEnvironmentLevel.STANDARD in classify_display_environment(
        standard
    )


def test_height_boundary():
    small = DisplayEnvironment(
        width_pixels=1920,
        height_pixels=MIN_SUPPORTED_HEIGHT - 1,
        dpi_scale_percent=100,
    )
    standard = DisplayEnvironment(
        width_pixels=1920,
        height_pixels=MIN_SUPPORTED_HEIGHT,
        dpi_scale_percent=100,
    )

    assert DisplayEnvironmentLevel.SMALL in classify_display_environment(small)
    assert DisplayEnvironmentLevel.STANDARD in classify_display_environment(
        standard
    )


def test_large_width_and_height_boundary():
    environment = DisplayEnvironment(
        width_pixels=LARGE_WIDTH,
        height_pixels=LARGE_HEIGHT,
        dpi_scale_percent=100,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.LARGE,
    )


def test_large_width_without_large_height_is_standard():
    environment = DisplayEnvironment(
        width_pixels=LARGE_WIDTH,
        height_pixels=LARGE_HEIGHT - 1,
        dpi_scale_percent=100,
    )

    assert classify_display_environment(environment) == (
        DisplayEnvironmentLevel.STANDARD,
    )


def test_high_dpi_boundary():
    environment = DisplayEnvironment(
        width_pixels=1920,
        height_pixels=1080,
        dpi_scale_percent=HIGH_DPI_THRESHOLD_PERCENT,
    )

    assert DisplayEnvironmentLevel.HIGH_DPI in classify_display_environment(
        environment
    )


def test_invalid_negative_width():
    with pytest.raises(ValueError):
        DisplayEnvironment(
            width_pixels=-1,
            height_pixels=1080,
            dpi_scale_percent=100,
        )


def test_invalid_negative_height():
    with pytest.raises(ValueError):
        DisplayEnvironment(
            width_pixels=1920,
            height_pixels=-1,
            dpi_scale_percent=100,
        )


def test_invalid_negative_dpi():
    with pytest.raises(ValueError):
        DisplayEnvironment(
            width_pixels=1920,
            height_pixels=1080,
            dpi_scale_percent=-1,
        )


def test_boolean_width_is_rejected():
    with pytest.raises(TypeError):
        DisplayEnvironment(
            width_pixels=True,
            height_pixels=1080,
            dpi_scale_percent=100,
        )


def test_classification_requires_display_environment():
    with pytest.raises(TypeError):
        classify_display_environment("1920x1080")


def test_result_requires_boolean_compatibility():
    with pytest.raises(TypeError):
        DisplayCompatibilityResult(
            compatible="yes",
            levels=(DisplayEnvironmentLevel.STANDARD,),
            reason="invalid",
        )


def test_result_requires_tuple_levels():
    with pytest.raises(TypeError):
        DisplayCompatibilityResult(
            compatible=True,
            levels=[DisplayEnvironmentLevel.STANDARD],
            reason="invalid",
        )


def test_result_requires_valid_levels():
    with pytest.raises(TypeError):
        DisplayCompatibilityResult(
            compatible=True,
            levels=("STANDARD",),
            reason="invalid",
        )


def test_result_requires_reason():
    with pytest.raises(ValueError):
        DisplayCompatibilityResult(
            compatible=True,
            levels=(DisplayEnvironmentLevel.STANDARD,),
            reason="",
        )


def test_display_environment_is_immutable():
    environment = DisplayEnvironment(
        width_pixels=1920,
        height_pixels=1080,
        dpi_scale_percent=100,
    )

    with pytest.raises(AttributeError):
        environment.width_pixels = 1280


def test_result_is_immutable():
    result = evaluate_display_compatibility(
        DisplayEnvironment(
            width_pixels=1920,
            height_pixels=1080,
            dpi_scale_percent=100,
        )
    )

    with pytest.raises(AttributeError):
        result.compatible = False
