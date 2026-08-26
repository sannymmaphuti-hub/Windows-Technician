from diagnostics.network import diagnose_network


def test_network_returns_expected_structure():
    result = diagnose_network()

    assert isinstance(result, dict)

    assert "active_adapter" in result
    assert "gateway" in result
    assert "gateway_reachable" in result
    assert "internet_reachable" in result
    assert "dns_working" in result
    assert "findings" in result

    assert isinstance(result["findings"], list)


def test_network_connectivity_values_are_boolean():
    result = diagnose_network()

    assert isinstance(
        result["gateway_reachable"],
        bool
    )

    assert isinstance(
        result["internet_reachable"],
        bool
    )

    assert isinstance(
        result["dns_working"],
        bool
    )


def test_network_findings_have_expected_structure():
    result = diagnose_network()

    for finding in result["findings"]:

        assert isinstance(finding, dict)

        assert "severity" in finding
        assert "category" in finding
        assert "message" in finding

        assert isinstance(
            finding["severity"],
            str
        )

        assert isinstance(
            finding["category"],
            str
        )

        assert isinstance(
            finding["message"],
            str
        )