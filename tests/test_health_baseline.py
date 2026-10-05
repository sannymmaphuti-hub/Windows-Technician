# ==========================================
# Windows Technician v0.8
# HEALTH BASELINE TESTS
# ==========================================

from engine.managed_machine import ManagedMachine
from engine.health_baseline import HealthBaseline


def build_machine():
    return ManagedMachine(
        machine_id="machine-001",
        hostname="REMOTE-PC",
        platform="Windows",
        operating_system="Windows 11",
    )


def build_baseline():
    return HealthBaseline(build_machine())


def test_health_baseline_requires_managed_machine():
    machine = build_machine()

    baseline = HealthBaseline(machine)

    assert baseline.machine is machine


def test_health_baseline_preserves_machine_identity():
    machine = build_machine()

    baseline = HealthBaseline(machine)

    assert baseline.machine_id == machine.machine_id
    assert baseline.hostname == machine.hostname


def test_health_baseline_identifies_as_baseline():
    baseline = build_baseline()

    assert baseline.machine is not None


def test_health_baseline_starts_without_samples():
    baseline = build_baseline()

    assert baseline.samples == []


def test_health_baseline_can_record_a_sample():
    baseline = build_baseline()

    baseline.add_sample({"memory_usage": 60})

    assert len(baseline.samples) == 1
    assert baseline.samples[0]["memory_usage"] == 60


def test_health_baseline_preserves_sample_history():
    baseline = build_baseline()

    baseline.add_sample({"memory_usage": 60})
    baseline.add_sample({"memory_usage": 65})

    assert len(baseline.samples) == 2
    assert baseline.samples[0]["memory_usage"] == 60
    assert baseline.samples[1]["memory_usage"] == 65


def test_health_baseline_does_not_modify_machine_identity():
    machine = build_machine()
    baseline = HealthBaseline(machine)

    baseline.add_sample({"memory_usage": 70})

    assert machine.machine_id == "machine-001"
    assert machine.hostname == "REMOTE-PC"


def test_health_baseline_does_not_authorize_remediation():
    baseline = build_baseline()

    assert not hasattr(baseline, "authorize")
    assert not hasattr(baseline, "approve")


def test_health_baseline_does_not_execute_remediation():
    baseline = build_baseline()

    assert not hasattr(baseline, "execute")
    assert not hasattr(baseline, "remediate")


def test_health_baseline_does_not_create_remediation_action():
    baseline = build_baseline()

    assert not hasattr(baseline, "remediation_action")
    assert not hasattr(baseline, "remediation_actions")


def test_health_baseline_does_not_create_diagnostic_case():
    baseline = build_baseline()

    assert not hasattr(baseline, "case")
    assert not hasattr(baseline, "diagnostic_case")


def test_health_baseline_does_not_create_proactive_alert():
    baseline = build_baseline()

    assert not hasattr(baseline, "alert")
    assert not hasattr(baseline, "proactive_alert")


def test_health_baseline_does_not_perform_diagnosis():
    baseline = build_baseline()

    assert not hasattr(baseline, "diagnose")
    assert not hasattr(baseline, "diagnostic_pipeline")


def test_health_baseline_does_not_perform_recovery():
    baseline = build_baseline()

    assert not hasattr(baseline, "recover")
    assert not hasattr(baseline, "recovery")


def test_health_baseline_does_not_retry():
    baseline = build_baseline()

    assert not hasattr(baseline, "retry")
    assert not hasattr(baseline, "retry_count")


def test_health_baseline_is_machine_specific():
    machine_a = build_machine()

    machine_b = ManagedMachine(
        machine_id="machine-002",
        hostname="SECOND-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    baseline_a = HealthBaseline(machine_a)
    baseline_b = HealthBaseline(machine_b)

    assert baseline_a.machine_id != baseline_b.machine_id
    assert baseline_a.hostname != baseline_b.hostname


def test_health_baseline_keeps_samples_isolated_between_machines():
    machine_a = build_machine()

    machine_b = ManagedMachine(
        machine_id="machine-002",
        hostname="SECOND-PC",
        platform="Windows",
        operating_system="Windows 11",
    )

    baseline_a = HealthBaseline(machine_a)
    baseline_b = HealthBaseline(machine_b)

    baseline_a.add_sample({"memory_usage": 70})

    assert len(baseline_a.samples) == 1
    assert baseline_b.samples == []


def test_health_baseline_exposes_machine_id():
    baseline = build_baseline()

    assert baseline.machine_id == "machine-001"


def test_health_baseline_exposes_hostname():
    baseline = build_baseline()

    assert baseline.hostname == "REMOTE-PC"


def test_health_baseline_does_not_equal_current_health_state():
    machine = build_machine()
    machine.health_state = "UNHEALTHY"

    baseline = HealthBaseline(machine)

    assert baseline.machine.health_state == "UNHEALTHY"
    assert baseline.samples == []


def test_health_baseline_is_observation_history_not_remediation_state():
    baseline = build_baseline()

    baseline.add_sample({"cpu_usage": 40})

    assert baseline.samples == [{"cpu_usage": 40}]
    assert not hasattr(baseline, "execution_status")
    assert not hasattr(baseline, "authorization_status")


def test_health_baseline_can_store_multiple_health_dimensions():
    baseline = build_baseline()

    sample = {
        "cpu_usage": 40,
        "memory_usage": 65,
        "disk_usage": 50,
    }

    baseline.add_sample(sample)

    assert baseline.samples[0] == sample


def test_health_baseline_preserves_original_sample_values():
    baseline = build_baseline()

    sample = {
        "cpu_usage": 40,
        "memory_usage": 65,
    }

    baseline.add_sample(sample)

    assert baseline.samples[0]["cpu_usage"] == 40
    assert baseline.samples[0]["memory_usage"] == 65