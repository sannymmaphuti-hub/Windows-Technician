from engine.evidence import DiagnosticEvidence


def test_evidence_starts_empty():

    evidence = DiagnosticEvidence()

    assert evidence.get_all() == {}


def test_evidence_can_add_category():

    evidence = DiagnosticEvidence()

    evidence.add(
        "CPU",
        {
            "usage_percent": 90
        }
    )

    assert evidence.has("CPU")


def test_evidence_can_retrieve_category():

    evidence = DiagnosticEvidence()

    cpu_data = {
        "usage_percent": 90
    }

    evidence.add("CPU", cpu_data)

    assert evidence.get("CPU") == cpu_data


def test_evidence_missing_category_returns_none():

    evidence = DiagnosticEvidence()

    assert evidence.get("GPU") is None


def test_evidence_can_initialize_with_data():

    data = {
        "CPU": {
            "usage_percent": 50
        },

        "MEMORY": {
            "usage_percent": 60
        }
    }

    evidence = DiagnosticEvidence(data)

    assert evidence.get("CPU") == data["CPU"]
    assert evidence.get("MEMORY") == data["MEMORY"]


def test_evidence_returns_all_data():

    data = {
        "CPU": {
            "usage_percent": 50
        }
    }

    evidence = DiagnosticEvidence(data)

    assert evidence.get_all() == data

def test_evidence_rejects_non_dictionary_data():

    try:

        DiagnosticEvidence("invalid")

        assert False

    except ValueError:

        assert True


def test_evidence_rejects_invalid_category():

    evidence = DiagnosticEvidence()

    try:

        evidence.add(
            123,
            {
                "usage_percent": 90
            }
        )

        assert False

    except ValueError:

        assert True


def test_evidence_rejects_empty_category():

    evidence = DiagnosticEvidence()

    try:

        evidence.add(
            "",
            {
                "usage_percent": 90
            }
        )

        assert False

    except ValueError:

        assert True


def test_evidence_rejects_non_dictionary_payload():

    evidence = DiagnosticEvidence()

    try:

        evidence.add(
            "CPU",
            90
        )

        assert False

    except ValueError:

        assert True


def test_evidence_accepts_valid_payload():

    evidence = DiagnosticEvidence()

    evidence.add(
        "CPU",
        {
            "usage_percent": 90
        }
    )

    assert evidence.get("CPU")["usage_percent"] == 90