from engine.diagnostic_action import DiagnosticAction
from engine.adaptive_diagnostic_result import AdaptiveDiagnosticResult
from engine.adaptive_diagnostic_loop import AdaptiveDiagnosticLoop
from engine.diagnostic_action_outcome import DiagnosticActionOutcome


class StubDecisionEngine:
    def __init__(self, decisions):
        self.decisions = list(decisions)
        self.calls = []

    def decide(self, evidence):
        self.calls.append(dict(evidence))

        if self.decisions:
            decision = self.decisions.pop(0)
            return [decision]

        return []


class StubActionSelector:
    def __init__(self, actions):
        self.actions = list(actions)
        self.calls = []

    def select(self, decision_type):
        self.calls.append(decision_type)

        if self.actions:
            action_type = self.actions.pop(0)

            return DiagnosticAction(
                action_type=action_type,
                category="NETWORK",
                description="Stub diagnostic action.",
            )

        return None


class StubExecutor:
    def __init__(self, evidence_results):
        self.evidence_results = list(evidence_results)
        self.calls = []

    def execute(self, action):
        self.calls.append(action)

        evidence = self.evidence_results.pop(0)

        return DiagnosticActionOutcome(
            action_type=action.action_type,
            evidence=evidence,
        )

def test_adaptive_loop_can_be_created():
    loop = AdaptiveDiagnosticLoop(
        StubDecisionEngine([]),
        StubActionSelector([]),
        StubExecutor([]),
    )

    assert loop is not None


def test_loop_requires_initial_evidence_dictionary():
    loop = AdaptiveDiagnosticLoop(
        StubDecisionEngine([]),
        StubActionSelector([]),
        StubExecutor([]),
    )

    try:
        loop.run(None)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")


def test_loop_stops_when_no_decision_is_returned():
    decision_engine = StubDecisionEngine([])
    action_selector = StubActionSelector([])
    executor = StubExecutor([])

    loop = AdaptiveDiagnosticLoop(
        decision_engine,
        action_selector,
        executor,
    )

    result = loop.run({})

    assert isinstance(result, AdaptiveDiagnosticResult)
    assert result.evidence == {}
    assert result.steps == 0
    assert result.stopped_reason == "NO_DECISION"


def test_loop_selects_action_for_decision():
    decision_engine = StubDecisionEngine(
        ["CHECK_GATEWAY_REACHABILITY"]
    )

    action_selector = StubActionSelector(
        ["PING_DEFAULT_GATEWAY"]
    )

    executor = StubExecutor(
        [{"gateway_reachable": True}]
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine,
        action_selector,
        executor,
    )

    loop.run({})

    assert action_selector.calls == [
        "CHECK_GATEWAY_REACHABILITY",
    ]


def test_loop_executes_selected_action():
    decision_engine = StubDecisionEngine(
        ["CHECK_GATEWAY_REACHABILITY"]
    )

    action_selector = StubActionSelector(
        ["PING_DEFAULT_GATEWAY"]
    )

    executor = StubExecutor(
        [{"gateway_reachable": True}]
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine,
        action_selector,
        executor,
    )

    loop.run({})

    assert len(executor.calls) == 1
    assert executor.calls[0].action_type == "PING_DEFAULT_GATEWAY"


def test_loop_feeds_new_evidence_back_into_decision_engine():
    decision_engine = StubDecisionEngine(
        [
            "CHECK_GATEWAY_REACHABILITY",
            "CHECK_DNS_RESOLUTION",
        ]
    )

    action_selector = StubActionSelector(
        [
            "PING_DEFAULT_GATEWAY",
            "TEST_DNS_RESOLUTION",
        ]
    )

    executor = StubExecutor(
        [
            {"gateway_reachable": True},
            {"dns_working": True},
        ]
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine,
        action_selector,
        executor,
    )

    loop.run({})

    assert decision_engine.calls == [
        {},
        {"gateway_reachable": True},
        {
            "gateway_reachable": True,
            "dns_working": True,
        },
    ]


def test_loop_stops_after_decision_engine_returns_no_decision():
    decision_engine = StubDecisionEngine(
        ["CHECK_GATEWAY_REACHABILITY"]
    )

    action_selector = StubActionSelector(
        ["PING_DEFAULT_GATEWAY"]
    )

    executor = StubExecutor(
        [{"gateway_reachable": True}]
    )

    loop = AdaptiveDiagnosticLoop(
        decision_engine,
        action_selector,
        executor,
    )

    result = loop.run({})

    assert isinstance(result, AdaptiveDiagnosticResult)
    assert result.evidence == {
        "gateway_reachable": True,
    }
    assert result.steps == 1
    assert result.stopped_reason == "NO_DECISION"


def test_loop_requires_a_selected_action():
    decision_engine = StubDecisionEngine(
        ["CHECK_GATEWAY_REACHABILITY"]
    )

    action_selector = StubActionSelector([])
    executor = StubExecutor([])

    loop = AdaptiveDiagnosticLoop(
        decision_engine,
        action_selector,
        executor,
    )

    try:
        loop.run({})
    except ValueError:
        pass
    else:
        raise AssertionError("Expected ValueError")

def test_loop_translates_diagnostic_outcome_into_observation():
    from engine.observation import Observation

    class FakeTranslator:
        def translate(self, outcome):
            return Observation(
                source="diagnostic_action",
                subject="network_gateway",
                attribute="reachable",
                value=True,
            )

    class FakeDecision:
        decision_type = "CHECK_GATEWAY"

    class FakeDecisionEngine:
        def decide(self, evidence):
            if "gateway_reachable" not in evidence:
                return [FakeDecision()]

            return []

    class FakeAction:
        action_type = "CHECK_GATEWAY"

    class FakeActionSelector:
        def select(self, decision_type):
            return FakeAction()

    class FakeExecutor:
        def execute(self, action):
            return DiagnosticActionOutcome(
                action_type="CHECK_GATEWAY",
                evidence={
                    "gateway_reachable": True,
                },
            )

    translator = FakeTranslator()

    loop = AdaptiveDiagnosticLoop(
        decision_engine=FakeDecisionEngine(),
        action_selector=FakeActionSelector(),
        executor=FakeExecutor(),
        observation_translator=translator,
    )

    result = loop.run({})

    assert len(result.observations) == 1

    observation = result.observations[0]

    assert isinstance(observation, Observation)
    assert observation.subject == "network_gateway"
    assert observation.attribute == "reachable"
    assert observation.value is True


def test_loop_passes_diagnostic_outcome_to_observation_translator():
    class FakeDecision:
        decision_type = "CHECK_GATEWAY"

    class FakeDecisionEngine:
        def decide(self, evidence):
            if "gateway_reachable" not in evidence:
                return [FakeDecision()]

            return []

    class FakeAction:
        action_type = "CHECK_GATEWAY"

    class FakeActionSelector:
        def select(self, decision_type):
            return FakeAction()

    class FakeExecutor:
        def execute(self, action):
            return DiagnosticActionOutcome(
                action_type="CHECK_GATEWAY",
                evidence={
                    "gateway_reachable": True,
                },
            )

    class FakeTranslator:
        def __init__(self):
            self.received_outcome = None

        def translate(self, outcome):
            self.received_outcome = outcome
            return "translated-observation"

    translator = FakeTranslator()

    loop = AdaptiveDiagnosticLoop(
        decision_engine=FakeDecisionEngine(),
        action_selector=FakeActionSelector(),
        executor=FakeExecutor(),
        observation_translator=translator,
    )

    result = loop.run({})

    assert translator.received_outcome is not None
    assert isinstance(
        translator.received_outcome,
        DiagnosticActionOutcome,
    )

    assert result.observations == [
        "translated-observation"
    ]