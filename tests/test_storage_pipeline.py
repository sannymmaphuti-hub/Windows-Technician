from engine.collectors.storage_collector import StorageCollector
from engine.diagnostic_engine import DiagnosticEngine
from engine.rules.storage_rule import StorageFreeSpaceRule


def test_storage_pipeline():

    collector = StorageCollector()

    storage_devices = collector.collect()

    engine = DiagnosticEngine()

    engine.add_rule(StorageFreeSpaceRule())

    findings = []

    for device in storage_devices:

        result = engine.diagnose(
            {
                "STORAGE": device
            }
        )

        findings.extend(
            result["findings"]
        )

    assert isinstance(
        findings,
        list
    )