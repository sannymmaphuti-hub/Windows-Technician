from copy import deepcopy

import pytest

from engine.technician_observability_projection import (
    TechnicianObservabilityProjection,
)


class ProjectionProvider:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    def projection(self):
        self.calls += 1
        return self.value


def test_projection_has_complete_schema():
    result = TechnicianObservabilityProjection().projection()

    assert set(result) == {
        "schema_version",
        "generated_at",
        "observability",
        "operation_metrics",
        "reliability_metrics",
        "event_history",
    }
    assert result["schema_version"] == "1.0"


def test_projection_timestamp_is_utc():
    result = TechnicianObservabilityProjection().projection()

    assert result["generated_at"].endswith("+00:00")


def test_projection_supports_missing_optional_providers():
    result = TechnicianObservabilityProjection().projection()

    assert result["observability"] is None
    assert result["operation_metrics"] is None
    assert result["reliability_metrics"] is None
    assert result["event_history"] is None


def test_projection_combines_all_provider_outputs():
    boundary = ProjectionProvider({
        "schema_version": "1.0",
        "telemetry_enabled": False,
        "engine": {"state": "IDLE"},
        "reliability": {"operation_count": 2},
    })
    operations = ProjectionProvider({
        "total_operations": 2,
        "failed_count": 1,
    })
    reliability = ProjectionProvider({
        "failed_operation_count": 1,
        "recovery_approved_count": 0,
    })
    history = ProjectionProvider({
        "capacity": 1000,
        "event_count": 7,
        "evicted_event_count": 2,
        "events": [{"event_id": "event-1"}],
    })

    result = TechnicianObservabilityProjection(
        observability_boundary=boundary,
        operation_metrics=operations,
        reliability_metrics=reliability,
        event_history=history,
    ).projection()

    assert result["observability"]["engine"]["state"] == "IDLE"
    assert result["operation_metrics"]["total_operations"] == 2
    assert result["reliability_metrics"]["failed_operation_count"] == 1
    assert result["event_history"] == {
        "capacity": 1000,
        "event_count": 7,
        "evicted_event_count": 2,
    }


def test_event_history_projection_excludes_full_event_payloads():
    history = ProjectionProvider({
        "capacity": 100,
        "event_count": 1,
        "evicted_event_count": 0,
        "events": [
            {
                "event_id": "event-1",
                "attributes": {"detail": "not part of the summary"},
            }
        ],
    })

    result = TechnicianObservabilityProjection(
        event_history=history,
    ).projection()

    assert result["event_history"] == {
        "capacity": 100,
        "event_count": 1,
        "evicted_event_count": 0,
    }
    assert "events" not in result["event_history"]


def test_each_provider_is_read_once_per_projection():
    providers = [
        ProjectionProvider({}),
        ProjectionProvider({}),
        ProjectionProvider({}),
        ProjectionProvider({
            "capacity": 10,
            "event_count": 0,
            "evicted_event_count": 0,
        }),
    ]

    component = TechnicianObservabilityProjection(
        observability_boundary=providers[0],
        operation_metrics=providers[1],
        reliability_metrics=providers[2],
        event_history=providers[3],
    )

    assert [provider.calls for provider in providers] == [0, 0, 0, 0]

    component.projection()

    assert [provider.calls for provider in providers] == [1, 1, 1, 1]


def test_each_projection_is_a_new_snapshot():
    provider = ProjectionProvider({
        "total_operations": 3,
        "by_status": {"FAILED": 1},
    })
    component = TechnicianObservabilityProjection(
        operation_metrics=provider,
    )

    first = component.projection()
    first["operation_metrics"]["total_operations"] = 999
    first["operation_metrics"]["by_status"]["FAILED"] = 999

    second = component.projection()

    assert second["operation_metrics"]["total_operations"] == 3
    assert second["operation_metrics"]["by_status"]["FAILED"] == 1


def test_projection_does_not_modify_provider_state():
    initial = {
        "total_operations": 3,
        "by_status": {"FAILED": 1},
    }
    provider = ProjectionProvider(deepcopy(initial))

    TechnicianObservabilityProjection(
        operation_metrics=provider,
    ).projection()

    assert provider.value == initial


@pytest.mark.parametrize(
    "provider_name",
    [
        "observability_boundary",
        "operation_metrics",
        "reliability_metrics",
        "event_history",
    ],
)
def test_rejects_provider_without_projection(provider_name):
    with pytest.raises(TypeError, match="projection"):
        TechnicianObservabilityProjection(
            **{provider_name: object()},
        )


def test_rejects_invalid_provider_projection():
    provider = ProjectionProvider(["not", "a", "mapping"])

    with pytest.raises(TypeError, match="must return a mapping"):
        TechnicianObservabilityProjection(
            operation_metrics=provider,
        ).projection()


def test_failed_provider_read_is_not_silently_hidden():
    class BrokenProvider:
        def projection(self):
            raise RuntimeError("provider unavailable")

    component = TechnicianObservabilityProjection(
        operation_metrics=BrokenProvider(),
    )

    with pytest.raises(RuntimeError, match="provider unavailable"):
        component.projection()


def test_event_history_summary_handles_missing_summary_fields():
    history = ProjectionProvider({"events": []})

    result = TechnicianObservabilityProjection(
        event_history=history,
    ).projection()

    assert result["event_history"] == {
        "capacity": None,
        "event_count": None,
        "evicted_event_count": None,
    }
