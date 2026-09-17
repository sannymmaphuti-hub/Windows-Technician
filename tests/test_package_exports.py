from application import Technician as PackageTechnician
from application.technician import Technician as CanonicalTechnician

from engine.collectors import StorageCollector as PackageStorageCollector
from engine.collectors.storage_collector import StorageCollector as CanonicalStorageCollector

from engine.intelligence import ProcessIntelligencePipeline as PackagePipeline
from engine.intelligence.process_pipeline import ProcessIntelligencePipeline as CanonicalPipeline

from engine.rules import StorageFreeSpaceRule as PackageStorageRule
from engine.rules.storage_rule import StorageFreeSpaceRule as CanonicalStorageRule


def test_application_package_exports_canonical_technician():
    assert PackageTechnician is CanonicalTechnician


def test_collectors_package_exports_canonical_storage_collector():
    assert PackageStorageCollector is CanonicalStorageCollector


def test_intelligence_package_exports_canonical_pipeline():
    assert PackagePipeline is CanonicalPipeline


def test_rules_package_exports_canonical_storage_rule():
    assert PackageStorageRule is CanonicalStorageRule