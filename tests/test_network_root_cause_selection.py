from engine.root_cause_candidate import RootCauseCandidate
from engine.root_cause_evaluation import RootCauseEvaluation
from engine.root_cause_selection import RootCauseSelection


def create_dns_candidate():
    return RootCauseCandidate(
        cause_type="DNS_FAILURE",
        category="NETWORK",
        explanation=(
            "DNS resolution is failing, which may prevent "
            "the computer from locating Internet services."
        ),
    )


def create_local_network_candidate():
    return RootCauseCandidate(
        cause_type="LOCAL_NETWORK_FAILURE",
        category="NETWORK",
        explanation=(
            "The local network gateway is unreachable while "
            "Internet connectivity is unavailable."
        ),
    )


def create_adapter_candidate():
    return RootCauseCandidate(
        cause_type="NETWORK_ADAPTER_FAILURE",
        category="NETWORK",
        explanation=(
            "The network adapter is disconnected, which may "
            "prevent communication with the network."
        ),
    )


def create_evaluation(
    candidate,
    assessment,
    supporting_evidence=None,
):
    return RootCauseEvaluation(
        candidate=candidate,
        supporting_evidence=(
            supporting_evidence
            if supporting_evidence is not None
            else []
        ),
        assessment=assessment,
        explanation="Test evaluation.",
    )


def test_network_selection_returns_none_when_no_evaluations_exist():
    selection = RootCauseSelection()

    result = selection.select([])

    assert result is None


def test_network_selection_ignores_insufficient_candidate():
    candidate = create_dns_candidate()

    evaluation = create_evaluation(
        candidate,
        "INSUFFICIENT",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is None


def test_network_selection_selects_supported_dns_candidate():
    candidate = create_dns_candidate()

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is candidate


def test_network_selection_selects_strongly_supported_adapter_candidate():
    candidate = create_adapter_candidate()

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is candidate


def test_network_selection_prefers_strongly_supported_over_supported():
    dns_candidate = create_dns_candidate()
    adapter_candidate = create_adapter_candidate()

    dns_evaluation = create_evaluation(
        dns_candidate,
        "SUPPORTED",
    )

    adapter_evaluation = create_evaluation(
        adapter_candidate,
        "STRONGLY_SUPPORTED",
    )

    selection = RootCauseSelection()

    result = selection.select([
        dns_evaluation,
        adapter_evaluation,
    ])

    assert result is adapter_candidate


def test_network_selection_can_select_local_network_candidate():
    candidate = create_local_network_candidate()

    evaluation = create_evaluation(
        candidate,
        "STRONGLY_SUPPORTED",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is candidate


def test_network_selection_preserves_candidate_identity():
    candidate = create_dns_candidate()

    evaluation = create_evaluation(
        candidate,
        "SUPPORTED",
    )

    selection = RootCauseSelection()

    result = selection.select([evaluation])

    assert result is candidate