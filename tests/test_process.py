from diagnostics.process_analyzer import (
    get_process_snapshot,
    analyze_processes,
    get_top_processes_by_memory,
    get_top_processes_by_cpu,
    get_process_cpu_history,
    analyze_process_persistence,
    analyze_cpu_behavior_history
)


def test_process_snapshot():
    snapshot = get_process_snapshot()

    assert isinstance(snapshot, list)

    for process in snapshot:

        assert isinstance(process, dict)

        assert "pid" in process
        assert "name" in process

        assert isinstance(
            process["pid"],
            int
        )

        assert isinstance(
            process["name"],
            str
        )


def test_process_analysis():
    snapshot = get_process_snapshot()

    findings = analyze_processes(
        snapshot
    )

    assert isinstance(
        findings,
        list
    )

    for finding in findings:

        assert isinstance(
            finding,
            dict
        )

        assert "severity" in finding
        assert "category" in finding
        assert "message" in finding


def test_top_processes_by_memory():
    snapshot = get_process_snapshot()

    processes = get_top_processes_by_memory(
        snapshot
    )

    assert isinstance(
        processes,
        list
    )

    for process in processes:

        assert "pid" in process
        assert "name" in process
        assert "memory_mb" in process

        assert isinstance(
            process["pid"],
            int
        )

        assert isinstance(
            process["name"],
            str
        )

        assert isinstance(
            process["memory_mb"],
            (int, float)
        )


def test_top_processes_by_cpu():
    snapshot = get_process_snapshot()

    processes = get_top_processes_by_cpu(
        snapshot
    )

    assert isinstance(
        processes,
        list
    )

    for process in processes:

        assert "pid" in process
        assert "name" in process
        assert "cpu_percent" in process

        assert isinstance(
            process["pid"],
            int
        )

        assert isinstance(
            process["name"],
            str
        )

        assert isinstance(
            process["cpu_percent"],
            (int, float)
        )


