from engine.rules.network_rule import NetworkAdapterRule


def test_network_rule_name():

    rule = NetworkAdapterRule()

    assert rule.name == "Network Adapter Rule"


def test_network_rule_category():

    rule = NetworkAdapterRule()

    assert rule.category == "NETWORK"


def test_network_rule_missing_adapters():

    rule = NetworkAdapterRule()

    result = rule.evaluate({})

    assert result is None


def test_network_rule_detects_no_usable_adapter():

    rule = NetworkAdapterRule()

    evidence = {
        "adapters": [
            {
                "name": "Loopback Pseudo-Interface 1",
                "ip_address": "127.0.0.1",
                "netmask": "255.0.0.0"
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result["category"] == "NETWORK"
    assert result["severity"] == "WARNING"
    assert result["confidence"] == 0.90


def test_network_rule_accepts_usable_adapter():

    rule = NetworkAdapterRule()

    evidence = {
        "adapters": [
            {
                "name": "WiFi",
                "ip_address": "192.168.0.238",
                "netmask": "255.255.255.0"
            }
        ]
    }

    result = rule.evaluate(evidence)

    assert result is None