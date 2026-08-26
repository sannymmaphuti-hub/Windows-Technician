
from engine.rules.cpu_contributor_rule import CPUContributorRule


def test_cpu_contributor_rule_name():

    rule = CPUContributorRule()

    assert rule.name == "CPU Contributor Rule"


def test_cpu_contributor_rule_category():

    rule = CPUContributorRule()

    assert rule.category == "CPU"


def test_cpu_contributor_normal_cpu():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 50,
        "top_processes": [
            {
                "pid": 1234,
                "name": "chrome.exe",
                "cpu_percent": 20.0
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result is None


def test_cpu_contributor_warning():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 85,
        "top_processes": [
            {
                "pid": 1234,
                "name": "chrome.exe",
                "cpu_percent": 60.0
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result["category"] == "CPU"
    assert result["severity"] == "WARNING"
    assert result["message"] == (
        "chrome.exe is the highest CPU-consuming process "
        "at 60.00%."
    )


def test_cpu_contributor_critical():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 97,
        "top_processes": [
            {
                "pid": 1234,
                "name": "chrome.exe",
                "cpu_percent": 70.0
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result["category"] == "CPU"
    assert result["severity"] == "CRITICAL"
    assert result["message"] == (
        "chrome.exe is the highest CPU-consuming process "
        "at 70.00%."
    )


def test_cpu_contributor_confidence_warning():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 85,
        "top_processes": [
            {
                "pid": 1234,
                "name": "chrome.exe",
                "cpu_percent": 60.0
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result["confidence"] == 0.90


def test_cpu_contributor_confidence_critical():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 97,
        "top_processes": [
            {
                "pid": 1234,
                "name": "chrome.exe",
                "cpu_percent": 70.0
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result["confidence"] == 0.95


def test_cpu_contributor_missing_processes():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 90
    }

    result = rule.evaluate(evidence)

    assert result is None


def test_cpu_contributor_empty_processes():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 90,
        "top_processes": []
    }

    result = rule.evaluate(evidence)

    assert result is None


def test_cpu_contributor_uses_highest_process():

    rule = CPUContributorRule()

    evidence = {
        "usage_percent": 90,
        "top_processes": [
            {
                "pid": 1234,
                "name": "chrome.exe",
                "cpu_percent": 70.0
            },
            {
                "pid": 5678,
                "name": "code.exe",
                "cpu_percent": 30.0
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert "chrome.exe" in result["message"]
    assert "70.00%" in result["message"]

