from engine.signal import Signal


def test_signal_can_be_converted_to_evidence_record():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    record = signal.to_evidence()

    assert record == {
        "signal_type": "HIGH_MEMORY_USAGE",
        "source": "memory",
        "subject": "system_memory",
        "attribute": "usage_percent",
        "value": 88,
    }


def test_signal_evidence_record_preserves_original_value():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    record = signal.to_evidence()

    assert record["value"] == 88
    assert record["signal_type"] == "HIGH_MEMORY_USAGE"


def test_signal_evidence_record_is_independent_from_signal_attributes():
    signal = Signal(
        signal_type="HIGH_MEMORY_USAGE",
        source="memory",
        subject="system_memory",
        attribute="usage_percent",
        value=88,
    )

    record = signal.to_evidence()

    record["value"] = 95

    assert signal.value == 88