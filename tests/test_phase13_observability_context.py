from dataclasses import FrozenInstanceError

import pytest

from engine.observability_context import ObservabilityContext


def test_create_generates_trace_and_correlation_ids():
    context = ObservabilityContext.create()

    assert context.trace_id
    assert context.correlation_id
    assert context.trace_id != context.correlation_id


def test_separate_contexts_receive_independent_ids():
    first = ObservabilityContext.create()
    second = ObservabilityContext.create()

    assert first.trace_id != second.trace_id
    assert first.correlation_id != second.correlation_id


def test_create_preserves_supplied_identifiers():
    context = ObservabilityContext.create(
        trace_id="trace-1",
        correlation_id="correlation-1",
        case_id="case-1",
        operation_id="operation-1",
    )

    assert context.projection() == {
        "trace_id": "trace-1",
        "correlation_id": "correlation-1",
        "case_id": "case-1",
        "operation_id": "operation-1",
    }


def test_child_preserves_trace_and_correlation_ids():
    parent = ObservabilityContext.create(
        case_id="case-1",
        operation_id="operation-parent",
    )

    child = parent.child(operation_id="operation-child")

    assert child.trace_id == parent.trace_id
    assert child.correlation_id == parent.correlation_id
    assert child.case_id == "case-1"
    assert child.operation_id == "operation-child"


def test_child_can_override_case_and_operation_identifiers():
    parent = ObservabilityContext.create(
        case_id="case-parent",
        operation_id="operation-parent",
    )

    child = parent.child(
        case_id="case-child",
        operation_id="operation-child",
    )

    assert child.case_id == "case-child"
    assert child.operation_id == "operation-child"
    assert child.trace_id == parent.trace_id
    assert child.correlation_id == parent.correlation_id


def test_child_without_overrides_inherits_optional_identifiers():
    parent = ObservabilityContext.create(
        case_id="case-1",
        operation_id="operation-1",
    )

    child = parent.child()

    assert child.case_id == parent.case_id
    assert child.operation_id == parent.operation_id


def test_child_does_not_mutate_parent():
    parent = ObservabilityContext.create(
        case_id="case-1",
        operation_id="operation-1",
    )

    parent_snapshot = parent.projection()
    parent.child(case_id="case-2", operation_id="operation-2")

    assert parent.projection() == parent_snapshot


def test_context_is_immutable():
    context = ObservabilityContext.create()

    with pytest.raises(FrozenInstanceError):
        context.trace_id = "changed"


@pytest.mark.parametrize(
    ("field_name", "value"),
    [
        ("trace_id", ""),
        ("trace_id", "   "),
        ("correlation_id", ""),
        ("correlation_id", "   "),
    ],
)
def test_required_identifiers_cannot_be_blank(field_name, value):
    with pytest.raises(ValueError):
        ObservabilityContext(
            trace_id="trace-1" if field_name != "trace_id" else value,
            correlation_id=(
                "correlation-1"
                if field_name != "correlation_id"
                else value
            ),
        )


@pytest.mark.parametrize(
    "field_name",
    ["case_id", "operation_id"],
)
def test_optional_identifiers_cannot_be_blank(field_name):
    with pytest.raises(ValueError):
        ObservabilityContext.create(**{field_name: "   "})


@pytest.mark.parametrize(
    "field_name",
    ["trace_id", "correlation_id", "case_id", "operation_id"],
)
def test_identifiers_must_be_strings_or_none(field_name):
    values = {
        "trace_id": "trace-1",
        "correlation_id": "correlation-1",
        "case_id": None,
        "operation_id": None,
    }
    values[field_name] = 123

    with pytest.raises(TypeError):
        ObservabilityContext(**values)


def test_projection_is_detached():
    context = ObservabilityContext.create(case_id="case-1")

    first = context.projection()
    first["case_id"] = "modified"
    first["trace_id"] = "modified"

    second = context.projection()

    assert second["case_id"] == "case-1"
    assert second["trace_id"] == context.trace_id


def test_explicit_contexts_do_not_share_mutable_state():
    first = ObservabilityContext.create(case_id="case-1")
    second = ObservabilityContext.create(case_id="case-2")

    assert first.case_id != second.case_id
    assert first.trace_id != second.trace_id
    assert first.correlation_id != second.correlation_id
