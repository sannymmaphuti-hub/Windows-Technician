# ==========================================
# Windows Technician v0.5
# FULL ANALYZER INTEGRATION TEST
# ==========================================

from engine.analyzer import Analyzer

from engine.collectors.cpu_collector import CPUCollector
from engine.collectors.memory_collector import MemoryCollector
from engine.collectors.storage_collector import StorageCollector
from engine.collectors.network_collector import NetworkCollector
from engine.collectors.gpu_collector import GPUCollector

from engine.rules.cpu_rule import CPUUsageRule
from engine.rules.memory_rule import MemoryUsageRule
from engine.rules.storage_rule import StorageFreeSpaceRule
from engine.rules.network_rule import NetworkAdapterRule
from engine.rules.gpu_rule import GPUStatusRule


def test_full_analyzer_collects_all_domains():

    analyzer = Analyzer(

        collectors=[
            CPUCollector(),
            MemoryCollector(),
            StorageCollector(),
            NetworkCollector(),
            GPUCollector()
        ],

        rules=[
            CPUUsageRule(),
            MemoryUsageRule(),
            StorageFreeSpaceRule(),
            NetworkAdapterRule(),
            GPUStatusRule()
        ]
    )

    result = analyzer.analyze()

    evidence = result["evidence"]

    assert "CPU" in evidence
    assert "MEMORY" in evidence
    assert "STORAGE" in evidence
    assert "NETWORK" in evidence
    assert "GPU" in evidence


def test_full_analyzer_returns_diagnosis():

    analyzer = Analyzer(

        collectors=[
            CPUCollector(),
            MemoryCollector(),
            StorageCollector(),
            NetworkCollector(),
            GPUCollector()
        ],

        rules=[
            CPUUsageRule(),
            MemoryUsageRule(),
            StorageFreeSpaceRule(),
            NetworkAdapterRule(),
            GPUStatusRule()
        ]
    )

    result = analyzer.analyze()

    diagnosis = result["diagnosis"]

    assert "status" in diagnosis
    assert "total_findings" in diagnosis
    assert "findings" in diagnosis
    assert "recommendations" in diagnosis

