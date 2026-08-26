import pytest

from engine.rules.base_rule import BaseRule


def test_base_rule_has_name():

    rule = BaseRule()

    assert rule.name == "Base Rule"


def test_base_rule_requires_evaluate_implementation():

    rule = BaseRule()

    with pytest.raises(NotImplementedError):

        rule.evaluate({})

def test_base_rule_has_category():

    rule = BaseRule()

    assert rule.category == "GENERAL"