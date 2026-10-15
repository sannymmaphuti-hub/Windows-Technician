"""Independent production-release approval gate.

Candidate readiness is not production approval. This gate requires explicit,
verified evidence for signing, clean-Windows installation, and approval.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class ProductionReleaseEvidence:
    """Verified release facts; callers must not infer these from RC readiness."""

    trusted_signature_verified: bool
    clean_windows_installation_verified: bool
    explicit_release_approval: bool

    def __post_init__(self) -> None:
        for name in (
            "trusted_signature_verified",
            "clean_windows_installation_verified",
            "explicit_release_approval",
        ):
            if not isinstance(getattr(self, name), bool):
                raise TypeError(f"{name} must be a boolean.")


@dataclass(frozen=True)
class ProductionReleaseDecision:
    approved: bool
    blockers: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.approved, bool):
            raise TypeError("approved must be a boolean.")
        if not isinstance(self.blockers, tuple):
            raise TypeError("blockers must be a tuple.")
        if any(not isinstance(item, str) or not item.strip() for item in self.blockers):
            raise ValueError("blockers must contain non-empty strings.")
        if self.approved != (not self.blockers):
            raise ValueError("approved must be true exactly when no blockers remain.")


def evaluate_production_release(
    evidence: ProductionReleaseEvidence,
) -> ProductionReleaseDecision:
    """Approve production distribution only when all independent gates pass."""
    if not isinstance(evidence, ProductionReleaseEvidence):
        raise TypeError("evidence must be ProductionReleaseEvidence.")

    blockers = []
    if not evidence.trusted_signature_verified:
        blockers.append("Trusted code-signature verification is incomplete.")
    if not evidence.clean_windows_installation_verified:
        blockers.append("Clean-Windows installation validation is incomplete.")
    if not evidence.explicit_release_approval:
        blockers.append("Explicit final production-release approval is missing.")

    blocker_tuple = tuple(blockers)
    return ProductionReleaseDecision(
        approved=not blocker_tuple,
        blockers=blocker_tuple,
    )
