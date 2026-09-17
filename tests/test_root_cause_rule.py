from engine.root_cause_rule import RootCauseRule


def test_root_cause_rule_requires_matches_implementation():

    class IncompleteRule(RootCauseRule):

        def create_candidate(self, findings):
            pass

    try:
        IncompleteRule()
        assert False
    except TypeError:
        assert True


def test_root_cause_rule_requires_create_candidate_implementation():

    class IncompleteRule(RootCauseRule):

        def matches(self, findings):
            return True

    try:
        IncompleteRule()
        assert False
    except TypeError:
        assert True


def test_root_cause_rule_can_be_implemented():

    class TestRule(RootCauseRule):

        def matches(self, findings):
            return True

        def create_candidate(self, findings):
            return "candidate"

    rule = TestRule()

    assert rule.matches([]) is True
    assert rule.create_candidate([]) == "candidate"