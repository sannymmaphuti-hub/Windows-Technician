from diagnostics.gpu import diagnose_gpu


def test_gpu_healthy():
    gpu_info = [
        {
            "name": "Test GPU",
            "memory": 4.0,
            "driver": "Test Driver",
            "status": "OK"
        }
    ]

    findings, recommendations = diagnose_gpu(gpu_info)

    assert isinstance(findings, list)
    assert isinstance(recommendations, list)
    assert len(findings) > 0


def test_gpu_empty():
    gpu_info = []

    findings, recommendations = diagnose_gpu(gpu_info)

    assert isinstance(findings, list)
    assert isinstance(recommendations, list)


def test_gpu_multiple():
    gpu_info = [
        {
            "name": "GPU 1",
            "memory": 4.0,
            "driver": "Driver 1",
            "status": "OK"
        },
        {
            "name": "GPU 2",
            "memory": 2.0,
            "driver": "Driver 2",
            "status": "OK"
        }
    ]

    findings, recommendations = diagnose_gpu(gpu_info)

    assert isinstance(findings, list)
    assert isinstance(recommendations, list)