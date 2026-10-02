import time

from engine.finding import Finding
from engine.recommendation_intelligence import RecommendationIntelligence
from engine.remediation_decision_boundary import RemediationDecisionBoundary
from engine.remediation_verifier import RemediationVerifier


def _build_findings(count):
    finding_types = [
        ("MEMORY", "High memory usage detected."),
        ("CPU", "High CPU usage detected."),
        ("STORAGE", "Storage pressure detected."),
        ("NETWORK", "Network instability detected."),
    ]

    findings = []

    for index in range(count):
        finding_type, description = finding_types[
            index % len(finding_types)
        ]

        findings.append(
            Finding(
                finding_type=finding_type,
                description=description,
                category=finding_type,
                severity="HIGH",
                supporting_signals=[],
            )
        )

    return findings


def test_recommendation_generation_is_stable_across_repeated_runs():
    intelligence = RecommendationIntelligence()
    findings = _build_findings(100)

    first = intelligence.generate(findings=findings)
    second = intelligence.generate(findings=findings)

    first_evidence = [
        recommendation.to_evidence()
        for recommendation in first
    ]

    second_evidence = [
        recommendation.to_evidence()
        for recommendation in second
    ]

    assert first_evidence == second_evidence


def test_recommendation_generation_handles_moderate_finding_volume():
    intelligence = RecommendationIntelligence()
    findings = _build_findings(500)

    recommendations = intelligence.generate(findings=findings)

    assert recommendations
    assert len(recommendations) <= 4


def test_duplicate_heavy_input_does_not_create_duplicate_recommendations():
    intelligence = RecommendationIntelligence()

    findings = _build_findings(1000)

    recommendations = intelligence.generate(findings=findings)

    recommendation_types = [
        recommendation.recommendation_type
        for recommendation in recommendations
    ]

    assert len(recommendation_types) == len(
        set(recommendation_types)
    )


def test_decision_boundary_is_stable_across_repeated_evaluations():
    intelligence = RecommendationIntelligence()
    boundary = RemediationDecisionBoundary()

    recommendations = intelligence.generate(
        findings=_build_findings(100)
    )

    first = [
        boundary.evaluate(recommendation).eligible
        for recommendation in recommendations
    ]

    second = [
        boundary.evaluate(recommendation).eligible
        for recommendation in recommendations
    ]

    assert first == second


def test_verification_is_stable_across_repeated_runs():
    verifier = RemediationVerifier()

    expected = {
        "memory_pressure": "NORMAL",
        "service": "running",
    }

    observed = {
        "memory_pressure": "NORMAL",
        "service": "running",
    }

    results = [
        verifier.verify(
            expected=expected,
            observed=observed,
            action_id="performance-action",
        )
        for _ in range(100)
    ]

    assert all(
        result.verification_result["verified"] is True
        for result in results
    )

    assert all(
        result.action_id == "performance-action"
        for result in results
    )


def test_verification_does_not_leak_state_between_runs():
    verifier = RemediationVerifier()

    successful = verifier.verify(
        expected={"status": "resolved"},
        observed={"status": "resolved"},
        action_id="action-success",
    )

    failed = verifier.verify(
        expected={"status": "resolved"},
        observed={"status": "failed"},
        action_id="action-failed",
    )

    successful_again = verifier.verify(
        expected={"status": "resolved"},
        observed={"status": "resolved"},
        action_id="action-success-again",
    )

    assert successful.verification_result["verified"] is True
    assert failed.verification_result["verified"] is False
    assert successful_again.verification_result["verified"] is True


def test_intelligence_pipeline_completes_within_reasonable_time():
    intelligence = RecommendationIntelligence()
    boundary = RemediationDecisionBoundary()
    verifier = RemediationVerifier()

    findings = _build_findings(1000)

    start = time.perf_counter()

    recommendations = intelligence.generate(
        findings=findings
    )

    decisions = [
        boundary.evaluate(recommendation)
        for recommendation in recommendations
    ]

    verification_results = [
        verifier.verify(
            expected={"status": "resolved"},
            observed={"status": "resolved"},
            action_id=f"performance-{index}",
        )
        for index in range(100)
    ]

    elapsed = time.perf_counter() - start

    assert recommendations
    assert decisions
    assert len(verification_results) == 100

    assert all(
        result.verification_result["verified"] is True
        for result in verification_results
    )

    # This is a stability guard, not a production performance benchmark.
    assert elapsed < 5.0