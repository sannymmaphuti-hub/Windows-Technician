# ==========================================
# WINDOWS TECHNICIAN v0.2
# DIAGNOSTIC ENGINE FACTORY
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

from engine.recommendation_engine import RecommendationEngine
from engine.collectors.process_collector import ProcessCollector


def create_diagnostic_engine():

    process_collector = ProcessCollector()

    return Analyzer(

        collectors=[
            CPUCollector(),
            MemoryCollector(),
            StorageCollector(),
            NetworkCollector(),
            GPUCollector(),
            process_collector
        ],

        rules=[
            CPUUsageRule(),
            MemoryUsageRule(),
            StorageFreeSpaceRule(),
            NetworkAdapterRule(),
            GPUStatusRule()
        ],

        recommendation_engine=RecommendationEngine(),
        process_collector=process_collector
    )
