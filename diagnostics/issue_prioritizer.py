# ==========================================================
# Windows Technician v0.6
# ISSUE PRIORITIZATION ENGINE
# ==========================================================


def calculate_issue_priority(
    severity,
    impact=0,
    persistence=0,
    correlation=0,
    confidence=0
):
    """
    Calculate a priority score for a diagnostic issue.

    The score helps determine which detected problem
    deserves the technician's attention first.

    This function does NOT determine root cause.
    It only ranks observed issues.
    """

    severity_scores = {
        "CRITICAL": 100,
        "WARNING": 70,
        "ATTENTION": 40,
        "INFO": 10
    }

    severity_score = severity_scores.get(
        severity,
        0
    )

    score = (
        severity_score
        + impact
        + persistence
        + correlation
        + confidence
    )

    return score


def prioritize_issues(candidates):
    """
    Rank diagnostic candidates from highest priority
    to lowest priority.
    """

    prioritized = []

    for candidate in candidates:

        severity = candidate.get(
            "severity",
            "INFO"
        )

        impact = candidate.get(
            "impact",
            0
        )

        persistence = candidate.get(
            "persistence",
            0
        )

        correlation = candidate.get(
            "correlation",
            0
        )

        confidence = candidate.get(
            "confidence",
            0
        )

        score = calculate_issue_priority(
            severity=severity,
            impact=impact,
            persistence=persistence,
            correlation=correlation,
            confidence=confidence
        )

        prioritized_candidate = candidate.copy()

        prioritized_candidate["priority_score"] = score

        prioritized.append(
            prioritized_candidate
        )

    prioritized.sort(
        key=lambda issue: issue["priority_score"],
        reverse=True
    )

    return prioritized


def identify_primary_issue(candidates):
    """
    Select the highest-priority diagnostic issue.
    """

    prioritized = prioritize_issues(
        candidates
    )

    if not prioritized:

        return {
            "status": "HEALTHY",
            "category": "SYSTEM",
            "issue": "No significant system issue detected.",
            "severity": "INFO",
            "priority_score": 0,
            "reason": (
                "Current diagnostic results do not "
                "indicate a significant system problem."
            )
        }

    primary = prioritized[0]

    return {
        "status": primary.get(
            "severity",
            "INFO"
        ),

        "category": primary.get(
            "category",
            "SYSTEM"
        ),

        "issue": primary.get(
            "issue",
            "Unknown issue"
        ),

        "severity": primary.get(
            "severity",
            "INFO"
        ),

        "priority_score": primary.get(
            "priority_score",
            0
        ),

        "reason": primary.get(
            "reason",
            "No diagnostic explanation available."
        )
    }


# ==========================================================
# MODULE TEST
# ==========================================================

if __name__ == "__main__":

    test_candidates = [

        {
            "severity": "WARNING",
            "category": "MEMORY",
            "issue": "High memory pressure",
            "confidence": 80,
            "impact": 20,
            "persistence": 10,
            "correlation": 10,
            "reason": (
                "System memory usage is above "
                "the recommended operating range."
            )
        },

        {
            "severity": "WARNING",
            "category": "PROCESS",
            "issue": "High CPU activity",
            "confidence": 65,
            "impact": 15,
            "persistence": 0,
            "correlation": 0,
            "reason": (
                "A process is currently consuming "
                "significant CPU resources."
            )
        }
    ]

    print("==========================================")
    print("ISSUE PRIORITIZER TEST")
    print("==========================================")

    prioritized = prioritize_issues(
        test_candidates
    )

    print()
    print("Prioritized Issues")
    print("------------------------------------------")

    for issue in prioritized:

        print(
            f"{issue['category']} | "
            f"{issue['issue']} | "
            f"Severity: {issue['severity']} | "
            f"Score: {issue['priority_score']}"
        )

    print()
    print("Primary Issue")
    print("------------------------------------------")

    primary = identify_primary_issue(
        test_candidates
    )

    print(
        f"Issue : {primary['issue']}"
    )

    print(
        f"Category : {primary['category']}"
    )

    print(
        f"Severity : {primary['severity']}"
    )

    print(
        f"Priority Score : {primary['priority_score']}"
    )

    print(
        f"Reason : {primary['reason']}"
    )
