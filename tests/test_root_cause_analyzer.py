# ==========================================
# Windows Technician v0.6
# ROOT CAUSE ANALYZER TESTS
# ==========================================

from engine.root_cause_analyzer import RootCauseAnalyzer


def test_no_root_cause_detected():

    analyzer = RootCauseAnalyzer()

    result = analyzer.analyze(
        findings=[],
        correlations=[]
    )

    assert isinstance(result, list)
    assert len(result) == 0


def test_memory_cpu_root_cause():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "severity": "WARNING",
            "category": "MEMORY",
            "message": (
                "High memory pressure detected."
            )
        },

        {
            "severity": "INFO",
            "category": "PROCESS CPU BEHAVIOR",
            "classification": "CPU SPIKE",
            "message": (
                "MemCompression experienced "
                "temporary high CPU activity."
            )
        }
    ]

    correlations = [

        {
            "severity": "INFO",
            "category": (
                "CROSS-DIAGNOSTIC CORRELATION"
            ),
            "relationship": (
                "MEMORY PRESSURE + CPU SPIKE"
            ),
            "process": "MemCompression",
            "message": (
                "High memory pressure coincided "
                "with temporary CPU activity."
            )
        }
    ]

    result = analyzer.analyze(
        findings=findings,
        correlations=correlations
    )

    assert isinstance(result, list)

    assert len(result) == 1

    candidate = result[0]

    assert candidate["category"] == "MEMORY"

    assert candidate["confidence"] == 0.80

    assert candidate["confidence_level"] == "HIGH"

    assert "Memory pressure" in candidate["cause"]

    assert len(candidate["evidence"]) == 3

    assert candidate["reason"]


def test_primary_candidate():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "severity": "WARNING",
            "category": "MEMORY",
            "message": "High memory pressure detected."
        },

        {
            "severity": "INFO",
            "category": "PROCESS CPU BEHAVIOR",
            "classification": "CPU SPIKE",
            "message": "CPU spike detected."
        }
    ]

    correlations = [

        {
            "relationship": (
                "MEMORY PRESSURE + CPU SPIKE"
            ),
            "message": (
                "Memory pressure and CPU activity "
                "were observed together."
            )
        }
    ]

    analyzer.analyze(
        findings=findings,
        correlations=correlations
    )

    primary = analyzer.get_primary_candidate()

    assert primary is not None

    assert primary["category"] == "MEMORY"

    assert primary["confidence"] == 0.80


def test_clear_candidates():

    analyzer = RootCauseAnalyzer()

    analyzer.add_candidate(
        cause="Test cause",
        category="TEST",
        confidence=0.50
    )

    assert len(analyzer.get_candidates()) == 1

    analyzer.clear()

    assert len(analyzer.get_candidates()) == 0


def test_candidate_evidence_is_preserved():

    analyzer = RootCauseAnalyzer()

    findings = [

        {
            "severity": "WARNING",
            "category": "MEMORY",
            "message": "Memory pressure detected."
        },

        {
            "severity": "INFO",
            "category": "PROCESS CPU BEHAVIOR",
            "classification": "CPU SPIKE",
            "message": "CPU spike detected."
        }
    ]

    correlations = [

        {
            "relationship": (
                "MEMORY PRESSURE + CPU SPIKE"
            ),
            "message": "Relationship detected."
        }
    ]

    result = analyzer.analyze(
        findings,
        correlations
    )

    candidate = result[0]

    assert "Memory pressure detected." in (
        candidate["evidence"]
    )

    assert "CPU spike detected." in (
        candidate["evidence"]
    )

    assert "Relationship detected." in (
        candidate["evidence"]
    )
