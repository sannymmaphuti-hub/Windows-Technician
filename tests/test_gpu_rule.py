from engine.rules.gpu_rule import GPUStatusRule


def test_gpu_rule_name():

    rule = GPUStatusRule()

    assert rule.name == "GPU Status Rule"


def test_gpu_rule_category():

    rule = GPUStatusRule()

    assert rule.category == "GPU"


def test_gpu_rule_normal_gpu():

    rule = GPUStatusRule()

    evidence = {
        "gpus": [
            {
                "name": "Intel(R) UHD Graphics 620",
                "memory_gb": 1.0,
                "driver_version": "27.20.100.8280",
                "status": "OK"
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result is None


def test_gpu_rule_no_gpu():

    rule = GPUStatusRule()

    evidence = {
        "gpus": []
    }

    result = rule.evaluate(evidence)

    assert result["category"] == "GPU"
    assert result["severity"] == "WARNING"
    assert result["message"] == "No GPU was detected."
    assert result["confidence"] == 0.85


def test_gpu_rule_unhealthy_gpu():

    rule = GPUStatusRule()

    evidence = {
        "gpus": [
            {
                "name": "Intel(R) UHD Graphics 620",
                "memory_gb": 1.0,
                "driver_version": "27.20.100.8280",
                "status": "ERROR"
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result["category"] == "GPU"
    assert result["severity"] == "WARNING"
    assert "Intel(R) UHD Graphics 620" in result["message"]
    assert "ERROR" in result["message"]
    assert result["confidence"] == 0.90