"""Integrated production performance architecture."""

from dataclasses import dataclass

from packaging.dataset_performance import (
    LARGE_DATASET_BUDGET,
    NORMAL_DATASET_BUDGET,
    STRESS_DATASET_BUDGET,
    DatasetPerformanceBudget,
)
from packaging.finding_performance import (
    LARGE_FINDINGS_BUDGET,
    NORMAL_FINDINGS_BUDGET,
    STRESS_FINDINGS_BUDGET,
    FindingPerformanceBudget,
)
from packaging.performance_boundary import (
    STARTUP_PERFORMANCE_BUDGET,
    PerformanceBudget,
)
from packaging.rendering_performance import (
    DASHBOARD_RENDERING_PERFORMANCE_BUDGET,
    LARGE_DASHBOARD_RENDERING_PERFORMANCE_BUDGET,
    RenderingPerformanceBudget,
)
from packaging.resource_performance import (
    SYSTEM_WIDE_INTELLIGENCE_RESOURCE_BUDGET,
    ResourcePerformanceBudget,
)
from packaging.ui_responsiveness import (
    DASHBOARD_REFRESH_RESPONSIVENESS_BUDGET,
    UI_INTERACTION_PERFORMANCE_BUDGET,
    UI_STATE_UPDATE_PERFORMANCE_BUDGET,
    UIResponsivenessBudget,
)


@dataclass(frozen=True)
class PerformanceArchitecture:
    """Canonical production performance boundaries."""

    startup: PerformanceBudget
    dashboard: RenderingPerformanceBudget
    large_dashboard: RenderingPerformanceBudget

    dataset_normal: DatasetPerformanceBudget
    dataset_large: DatasetPerformanceBudget
    dataset_stress: DatasetPerformanceBudget

    findings_normal: FindingPerformanceBudget
    findings_large: FindingPerformanceBudget
    findings_stress: FindingPerformanceBudget

    resources: ResourcePerformanceBudget

    ui_interaction: UIResponsivenessBudget
    ui_state_update: UIResponsivenessBudget
    dashboard_refresh: UIResponsivenessBudget


PRODUCTION_PERFORMANCE_ARCHITECTURE = PerformanceArchitecture(
    startup=STARTUP_PERFORMANCE_BUDGET,
    dashboard=DASHBOARD_RENDERING_PERFORMANCE_BUDGET,
    large_dashboard=LARGE_DASHBOARD_RENDERING_PERFORMANCE_BUDGET,
    dataset_normal=NORMAL_DATASET_BUDGET,
    dataset_large=LARGE_DATASET_BUDGET,
    dataset_stress=STRESS_DATASET_BUDGET,
    findings_normal=NORMAL_FINDINGS_BUDGET,
    findings_large=LARGE_FINDINGS_BUDGET,
    findings_stress=STRESS_FINDINGS_BUDGET,
    resources=SYSTEM_WIDE_INTELLIGENCE_RESOURCE_BUDGET,
    ui_interaction=UI_INTERACTION_PERFORMANCE_BUDGET,
    ui_state_update=UI_STATE_UPDATE_PERFORMANCE_BUDGET,
    dashboard_refresh=DASHBOARD_REFRESH_RESPONSIVENESS_BUDGET,
)


def performance_architecture_is_consistent(
    architecture: PerformanceArchitecture = PRODUCTION_PERFORMANCE_ARCHITECTURE,
) -> bool:
    """Validate the relationships between all performance boundaries."""

    if not isinstance(architecture, PerformanceArchitecture):
        raise TypeError("architecture must be a PerformanceArchitecture.")

    budgets = (
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

    if not all(
        getattr(budget, "maximum_seconds", 0) > 0
        for budget in budgets
    ):
        return False

    if architecture.startup.operation != "application_startup":
        return False

    if architecture.dashboard.operation != "dashboard_rendering":
        return False

    if architecture.large_dashboard.operation != "large_dashboard_rendering":
        return False

    if architecture.dataset_normal.operation != "diagnostic_dataset_processing":
        return False

    if architecture.dataset_large.operation != "diagnostic_dataset_processing":
        return False

    if architecture.dataset_stress.operation != "diagnostic_dataset_processing":
        return False

    if architecture.dataset_normal.minimum_item_count != 100:
        return False

    if architecture.dataset_large.minimum_item_count != 1000:
        return False

    if architecture.dataset_stress.minimum_item_count != 10000:
        return False

    if architecture.findings_normal.operation != "finding_processing":
        return False

    if architecture.findings_large.operation != "finding_processing":
        return False

    if architecture.findings_stress.operation != "finding_processing":
        return False

    if architecture.findings_normal.minimum_finding_count != 100:
        return False

    if architecture.findings_large.minimum_finding_count != 1000:
        return False

    if architecture.findings_stress.minimum_finding_count != 10000:
        return False

    if architecture.resources.operation != "system_wide_intelligence":
        return False

    if architecture.ui_interaction.operation != "ui_interaction":
        return False

    if architecture.ui_state_update.operation != "ui_state_update":
        return False

    if architecture.dashboard_refresh.operation != "dashboard_refresh":
        return False

    if (
        architecture.dashboard.maximum_seconds
        > architecture.large_dashboard.maximum_seconds
    ):
        return False

    if (
        architecture.dataset_normal.maximum_seconds
        > architecture.dataset_large.maximum_seconds
    ):
        return False

    if (
        architecture.dataset_large.maximum_seconds
        > architecture.dataset_stress.maximum_seconds
    ):
        return False

    if (
        architecture.findings_normal.maximum_seconds
        > architecture.findings_large.maximum_seconds
    ):
        return False

    if (
        architecture.findings_large.maximum_seconds
        > architecture.findings_stress.maximum_seconds
    ):
        return False

    if (
        architecture.ui_interaction.maximum_seconds
        > architecture.dashboard_refresh.maximum_seconds
    ):
        return False

    if (
        architecture.ui_state_update.maximum_seconds
        > architecture.dashboard_refresh.maximum_seconds
    ):
        return False

    return True
