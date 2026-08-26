from diagnostics.issue_prioritizer import (
    prioritize_issues,
    identify_primary_issue
)


def test_prioritize_issues():
    issues = [
        {
            "severity": "WARNING",
            "category": "MEMORY",
            "issue": "High memory pressure",
            "confidence": 80,
            "impact": 20,
            "persistence": 10,
            "correlation": 10,
            "reason": "Memory usage is high."
        },
        {
            "severity": "CRITICAL",
            "category": "CPU",
            "issue": "Critical CPU utilization",
            "confidence": 90,
            "impact": 30,
            "persistence": 20,
            "correlation": 10,
            "reason": "CPU utilization is extremely high."
        }
    ]

    result = prioritize_issues(issues)

    assert isinstance(result, list)

    assert len(result) == 2

    assert result[0]["category"] == "CPU"

    assert result[0]["priority_score"] >= result[1]["priority_score"]


def test_identify_primary_issue():
    issues = [
        {
            "severity": "WARNING",
            "category": "MEMORY",
            "issue": "High memory pressure",
            "confidence": 80,
            "impact": 20,
            "persistence": 10,
            "correlation": 10,
            "reason": "Memory usage is high."
        },
        {
            "severity": "CRITICAL",
            "category": "CPU",
            "issue": "Critical CPU utilization",
            "confidence": 90,
            "impact": 30,
            "persistence": 20,
            "correlation": 10,
            "reason": "CPU utilization is extremely high."
        }
    ]

    result = identify_primary_issue(issues)

    assert result is not None

    assert result["category"] == "CPU"

    assert result["issue"] == "Critical CPU utilization"

    assert "priority_score" in result


def test_no_issues():
    issues = []

    prioritized = prioritize_issues(issues)

    primary = identify_primary_issue(issues)

    assert isinstance(prioritized, list)

    assert len(prioritized) == 0

    assert primary is not None
    assert primary["status"] == "HEALTHY"
    assert primary["category"] == "SYSTEM"