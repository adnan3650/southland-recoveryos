from datetime import datetime, timezone
from uuid import uuid4

from .rules import initial_tasks


def now():
    return datetime.now(timezone.utc).isoformat()


class CaseService:
    def __init__(self, repository):
        self.repo = repository

    def create(self, data, owner):
        case = {
            **data.model_dump(mode="json"),
            "id": str(uuid4()),
            "created_at": now(),
            "updated_at": now(),
            "documents": [],
            "damage_items": [],
            "insurance": {},
            "contacts": [],
            "conversations": [],
            "analyses": [],
            "reports": [],
            "audit": [],
            "ai_plan": None,
        }
        case["tasks"] = initial_tasks(case)
        self.save(case, owner, "case.created")
        return case

    def save(self, case, owner, event):
        case["updated_at"] = now()
        case["audit"].append({"event": event, "at": now()})
        case["audit"] = case["audit"][-150:]
        self.repo.save(case, owner)
        return case


class InsuranceGuidanceService:
    @staticmethod
    def guidance(case):
        from .rules import readiness

        return {
            "record": case["insurance"],
            "readiness": readiness(case),
            "caveat": "Your insurer determines coverage. Policy extraction is an AI interpretation; verify original wording.",
        }


class AssistanceMatchingService:
    @staticmethod
    def match(case, resources):
        from .rules import match_programs

        return match_programs(case, resources)


class RecoveryPlanService:
    @staticmethod
    def plan(case, resources):
        from .rules import prioritized_plan

        return prioritized_plan(case, resources)
