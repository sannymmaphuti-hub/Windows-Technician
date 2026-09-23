# ==========================================
# Windows Technician v0.6
# PROCESS COLLECTOR TESTS
# ==========================================

from engine.collectors.process_collector import ProcessCollector


def test_process_collector_has_correct_category():

    collector = ProcessCollector()

    assert collector.category == "PROCESS"


def test_process_collector_returns_process_data():

    collector = ProcessCollector()

    result = collector.collect()

    assert isinstance(result, dict)

    assert "processes" in result

    assert isinstance(
        result["processes"],
        list
    )


def test_process_entries_have_expected_fields():

    collector = ProcessCollector()

    result = collector.collect()

    processes = result["processes"]

    if not processes:
        return

    process = processes[0]

    assert "pid" in process
    assert "name" in process
    assert "cpu_percent" in process
    assert "memory_mb" in process
    assert "status" in process


def test_process_collector_can_collect_cpu_history():

    collector = ProcessCollector()

    history = collector.collect_cpu_history(
        sample_count=2,
        interval=0
    )

    assert isinstance(
        history,
        list
    )

    if history:

        assert "pid" in history[0]
        assert "name" in history[0]
        assert "samples" in history[0]
