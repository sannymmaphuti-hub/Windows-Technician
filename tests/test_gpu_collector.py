from engine.collectors.gpu_collector import GPUCollector


def test_gpu_collector_returns_list():

    collector = GPUCollector()

    result = collector.collect()

    assert isinstance(result, list)


def test_gpu_collector_returns_valid_gpu_structure():

    collector = GPUCollector()

    result = collector.collect()

    for gpu in result:

        assert "name" in gpu
        assert "memory_gb" in gpu
        assert "driver_version" in gpu
        assert "status" in gpu


def test_gpu_memory_is_numeric():

    collector = GPUCollector()

    result = collector.collect()

    for gpu in result:

        assert isinstance(
            gpu["memory_gb"],
            (int, float)
        )


def test_gpu_status_is_string_or_none():

    collector = GPUCollector()

    result = collector.collect()

    for gpu in result:

        assert (
            isinstance(gpu["status"], str)
            or gpu["status"] is None
        )


def test_gpu_collector_handles_no_gpu():

    collector = GPUCollector()

    result = collector.collect()

    assert result is not None
    