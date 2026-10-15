from copy import deepcopy

import pytest

from engine.observability_boundary import ObservabilityBoundary


class ProjectionProvider:
    def __init__(self, value):
        self.value = value
        self.calls = 0

    def projection(self):
        self.calls += 1
        return self.value


def test_boundary_defaults_telemetry_to_disabled():
    boundary = ObservabilityBoundary()

    projection = boundary.projection()

    assert boundary.telemetry_enabled is False
    assert projection["telemetry_enabled"] is False


def test_boundary_exposes_schema_version():
    projection = ObservabilityBoundary().projection()

    assert projection["schema_version"] == "1.0"


def test_boundary_supports_missing_optional_providers():
    projection = ObservabilityBoundary().projection()

    assert projection["engine"] is None
    assert projection["reliability"] is None


def test_boundary_exposes_engine_projection():
    engine = ProjectionProvider({"state": "INVESTIGATING"})

    projection = ObservabilityBoundary(
        problem_solving_engine=engine
    ).projection()

    assert projection["engine"] == {"state": "INVESTIGATING"}
    assert engine.calls == 1


def test_boundary_exposes_reliability_projection():
    reliability = ProjectionProvider({"operations": {"total": 3}})

    projection = ObservabilityBoundary(
        reliability_service=reliability
    ).projection()

    assert projection["reliability"] == {
        "operations": {"total": 3}
    }
    assert reliability.calls == 1


def test_boundary_exposes_both_existing_projections():
    engine = ProjectionProvider({"state": "DIAGNOSED"})
    reliability = ProjectionProvider({"operations": {"total": 2}})

    projection = ObservabilityBoundary(
        engine,
        reliability,
    ).projection()

    assert projection["engine"]["state"] == "DIAGNOSED"
    assert projection["reliability"]["operations"]["total"] == 2


def test_boundary_does_not_mutate_provider_state():
    original = {
        "state": "INVESTIGATING",
        "items": ["cpu", "memory"],
    }
    engine = ProjectionProvider(deepcopy(original))

    before = deepcopy(engine.value)

    ObservabilityBoundary(
        problem_solving_engine=engine
    ).projection()

    assert engine.value == before


def test_boundary_returns_a_separate_outer_projection_mapping():
    engine = ProjectionProvider({"state": "INVESTIGATING"})

    projection = ObservabilityBoundary(
        problem_solving_engine=engine
    ).projection()

    projection["engine"]["state"] = "MODIFIED"

    assert engine.value["state"] == "INVESTIGATING"


def test_boundary_requires_boolean_telemetry_setting():
    with pytest.raises(TypeError, match="telemetry_enabled"):
        ObservabilityBoundary(telemetry_enabled=1)


def test_boundary_rejects_engine_without_projection_method():
    with pytest.raises(TypeError, match="problem_solving_engine"):
        ObservabilityBoundary(problem_solving_engine=object())


def test_boundary_rejects_reliability_provider_without_projection():
    with pytest.raises(TypeError, match="reliability_service"):
        ObservabilityBoundary(reliability_service=object())


def test_boundary_rejects_non_mapping_engine_projection():
    engine = ProjectionProvider(["not", "a", "mapping"])

    with pytest.raises(TypeError, match="must return a mapping"):
        ObservabilityBoundary(
            problem_solving_engine=engine
        ).projection()


def test_boundary_rejects_non_mapping_reliability_projection():
    reliability = ProjectionProvider(None)

    with pytest.raises(TypeError, match="must return a mapping"):
        ObservabilityBoundary(
            reliability_service=reliability
        ).projection()


def test_boundary_reads_each_provider_once_per_projection():
    engine = ProjectionProvider({})
    reliability = ProjectionProvider({})

    boundary = ObservabilityBoundary(engine, reliability)
    boundary.projection()

    assert engine.calls == 1
    assert reliability.calls == 1


def test_boundary_does_not_call_providers_during_construction():
    engine = ProjectionProvider({})
    reliability = ProjectionProvider({})

    ObservabilityBoundary(engine, reliability)

    assert engine.calls == 0
    assert reliability.calls == 0


def test_telemetry_can_only_be_enabled_explicitly():
    boundary = ObservabilityBoundary(telemetry_enabled=True)

    assert boundary.telemetry_enabled is True
    assert boundary.projection()["telemetry_enabled"] is True
