from engine.signal import Signal


def test_same_signal_type_can_represent_different_observed_values():
    first = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    second = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=92,
    )

    assert first.signal_type == second.signal_type
    assert first.source == second.source
    assert first.subject == second.subject
    assert first.attribute == second.attribute
    assert first.value != second.value