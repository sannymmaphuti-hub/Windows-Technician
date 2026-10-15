from copy import deepcopy

from engine.case_ownership import CaseOwnership
from engine.case_status_coordination import CaseStatusCoordinator
from engine.case_timeline import CaseTimeline
from engine.technician_collaboration_boundary import (
    TechnicianCollaborationBoundary,
)


class CaseCollaborationProjection:
    def __init__(
        self,
        collaboration_boundary,
        ownership,
        status_coordinator,
        timeline,
    ):
        if not isinstance(
            collaboration_boundary,
            TechnicianCollaborationBoundary,
        ):
            raise ValueError(
                "collaboration_boundary must be a "
                "TechnicianCollaborationBoundary."
            )

        if not isinstance(ownership, CaseOwnership):
            raise ValueError(
                "ownership must be a CaseOwnership."
            )

        if not isinstance(
            status_coordinator,
            CaseStatusCoordinator,
        ):
            raise ValueError(
                "status_coordinator must be a "
                "CaseStatusCoordinator."
            )

        if not isinstance(timeline, CaseTimeline):
            raise ValueError(
                "timeline must be a CaseTimeline."
            )

        case_id = collaboration_boundary.case_id

        if ownership.case_id != case_id:
            raise ValueError(
                "Ownership belongs to a different case."
            )

        if status_coordinator.case_id != case_id:
            raise ValueError(
                "Status coordinator belongs to a different case."
            )

        if timeline.case_id != case_id:
            raise ValueError(
                "Timeline belongs to a different case."
            )

        self.collaboration_boundary = collaboration_boundary
        self.ownership = ownership
        self.status_coordinator = status_coordinator
        self.timeline = timeline

    @property
    def case_id(self):
        return self.collaboration_boundary.case_id

    def projection(self):
        owner = self.ownership.owner

        return deepcopy(
            {
                "case": self.collaboration_boundary.case_projection(),
                "ownership": self.ownership.projection(),
                "status": self.status_coordinator.projection(),
                "timeline": self.timeline.projection(),
                "technician": (
                    owner.projection()
                    if owner is not None
                    else None
                ),
            }
        )

    def __repr__(self):
        return (
            f"CaseCollaborationProjection("
            f"case_id={self.case_id!r}"
            f")"
        )
