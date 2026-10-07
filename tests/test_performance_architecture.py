"""Tests for the integrated production performance architecture."""

from dataclasses import replace

import pytest

from packaging.dataset_performance import DatasetPerformanceBudget
from packaging.finding_performance import FindingPerformanceBudget
from packaging.performance_architecture import (
    PRODUCTION_PERFORMANCE_ARCHITECTURE,
    PerformanceArchitecture,
    performance_architecture_is_consistent,
)
from packaging.performance_boundary import PerformanceBudget
from packaging.rendering_performance import RenderingPerformanceBudget
from packaging.resource_performance import ResourcePerformanceBudget
from packaging.ui_responsiveness import UIResponsivenessBudget


def test_production_architecture_has_expected_type():
    assert isinstance(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        PerformanceArchitecture,
    )


def test_production_architecture_is_consistent():
    assert performance_architecture_is_consistent()


def test_architecture_contains_all_boundaries():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    assert architecture.startup.operation == "application_startup"
    assert architecture.dashboard.operation == "dashboard_rendering"
    assert architecture.large_dashboard.operation == "large_dashboard_rendering"

    assert architecture.dataset_normal.operation == "diagnostic_dataset_processing"
    assert architecture.dataset_large.operation == "diagnostic_dataset_processing"
    assert architecture.dataset_stress.operation == "diagnostic_dataset_processing"

    assert architecture.dataset_normal.minimum_item_count == 100
    assert architecture.dataset_large.minimum_item_count == 1000
    assert architecture.dataset_stress.minimum_item_count == 10000

    assert architecture.findings_normal.operation == "finding_processing"
    assert architecture.findings_large.operation == "finding_processing"
    assert architecture.findings_stress.operation == "finding_processing"

    assert architecture.findings_normal.minimum_finding_count == 100
    assert architecture.findings_large.minimum_finding_count == 1000
    assert architecture.findings_stress.minimum_finding_count == 10000

    assert architecture.resources.operation == "system_wide_intelligence"

    assert architecture.ui_interaction.operation == "ui_interaction"
    assert architecture.ui_state_update.operation == "ui_state_update"
    assert architecture.dashboard_refresh.operation == "dashboard_refresh"


def test_dataset_budgets_scale_monotonically():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    assert (
        architecture.dataset_normal.maximum_seconds
        <= architecture.dataset_large.maximum_seconds
        <= architecture.dataset_stress.maximum_seconds
    )


def test_dataset_workload_thresholds_scale_monotonically():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    assert (
        architecture.dataset_normal.minimum_item_count
        < architecture.dataset_large.minimum_item_count
        < architecture.dataset_stress.minimum_item_count
    )


def test_finding_budgets_scale_monotonically():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    assert (
        architecture.findings_normal.maximum_seconds
        <= architecture.findings_large.maximum_seconds
        <= architecture.findings_stress.maximum_seconds
    )


def test_finding_workload_thresholds_scale_monotonically():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    assert (
        architecture.findings_normal.minimum_finding_count
        < architecture.findings_large.minimum_finding_count
        < architecture.findings_stress.minimum_finding_count
    )


def test_dashboard_budgets_scale_monotonically():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    assert (
        architecture.dashboard.maximum_seconds
        <= architecture.large_dashboard.maximum_seconds
    )


def test_ui_budgets_protect_interactive_operations():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    assert (
        architecture.ui_interaction.maximum_seconds
        <= architecture.dashboard_refresh.maximum_seconds
    )

    assert (
        architecture.ui_state_update.maximum_seconds
        <= architecture.dashboard_refresh.maximum_seconds
    )


@pytest.mark.parametrize(
    "field",
    [
        "startup",
        "dashboard",
        "large_dashboard",
        "dataset_normal",
        "dataset_large",
        "dataset_stress",
        "findings_normal",
        "findings_large",
        "findings_stress",
        "resources",
        "ui_interaction",
        "ui_state_update",
        "dashboard_refresh",
    ],
)
def test_every_boundary_is_present(field):
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE
    assert getattr(architecture, field) is not None


def test_rejects_wrong_architecture_type():
    with pytest.raises(TypeError):
        performance_architecture_is_consistent(object())


def test_rejects_wrong_startup_operation():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        startup=PerformanceBudget(
            operation="wrong_operation",
            maximum_seconds=5.0,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_wrong_dashboard_operation():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        dashboard=RenderingPerformanceBudget(
            operation="wrong_operation",
            maximum_seconds=1.0,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_wrong_large_dashboard_operation():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        large_dashboard=RenderingPerformanceBudget(
            operation="wrong_operation",
            maximum_seconds=2.0,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_wrong_dataset_operation():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        dataset_large=DatasetPerformanceBudget(
            operation="wrong_operation",
            maximum_seconds=1.0,
            minimum_item_count=1000,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_wrong_finding_operation():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        findings_large=FindingPerformanceBudget(
            operation="wrong_operation",
            maximum_seconds=1.0,
            minimum_finding_count=1000,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_wrong_resource_operation():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        resources=ResourcePerformanceBudget(
            operation="wrong_operation",
            maximum_seconds=5.0,
            maximum_memory_growth_bytes=256 * 1024 * 1024,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_invalid_dataset_progression():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        dataset_large=DatasetPerformanceBudget(
            operation="diagnostic_dataset_processing",
            maximum_seconds=0.1,
            minimum_item_count=1000,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_invalid_finding_progression():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        findings_large=FindingPerformanceBudget(
            operation="finding_processing",
            maximum_seconds=0.1,
            minimum_finding_count=1000,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_rejects_invalid_ui_progression():
    architecture = replace(
        PRODUCTION_PERFORMANCE_ARCHITECTURE,
        dashboard_refresh=UIResponsivenessBudget(
            operation="dashboard_refresh",
            maximum_seconds=0.05,
        ),
    )

    assert not performance_architecture_is_consistent(architecture)


def test_architecture_is_frozen():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    with pytest.raises(AttributeError):
        architecture.startup = architecture.startup


def test_all_boundaries_have_positive_time_limits():
    architecture = PRODUCTION_PERFORMANCE_ARCHITECTURE

    boundaries = (
        architecture.startup,
        architecture.dashboard,
        architecture.large_dashboard,
        architecture.dataset_normal,
        architecture.dataset_large,
        architecture.dataset_stress,
        architecture.findings_normal,
        architecture.findings_large,
        architecture.findings_stress,
        architecture.resources,
        architecture.ui_interaction,
        architecture.ui_state_update,
        architecture.dashboard_refresh,
    )

    assert all(
        boundary.maximum_seconds > 0
        for boundary in boundaries
    )
