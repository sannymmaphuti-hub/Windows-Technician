from engine.collectors.gpu_collector import GPUCollector
from engine.evidence_builder import EvidenceBuilder
from engine.rules.gpu_rule import GPUStatusRule


def test_gpu_pipeline():

    gpu_data = GPUCollector().collect()

    builder = EvidenceBuilder()

    builder.add_category(
        "GPU",
        {
            "gpus": gpu_data
        }
    )

    evidence = builder.build()

    gpu_evidence = evidence.get("GPU")

    rule = GPUStatusRule()

    result = rule.evaluate(
        gpu_evidence
    )

    if gpu_data:

        healthy_gpus = all(
            gpu.get("status") in ("OK", "NORMAL")
            for gpu in gpu_data
        )

        if healthy_gpus:
            assert result is None
        else:
            assert result is not None

    else:

        assert result is not None
        assert result["category"] == "GPU"