from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class CaseInput(Model):
    resident_name: str = Field(min_length=1, max_length=100)
    municipality: str = Field(min_length=2, max_length=80)
    zip_code: str = Field(pattern=r"^\d{5}$")
    disaster_type: Literal["flood", "storm", "tornado", "fire", "other"] = "flood"
    incident_date: date
    description: str = Field(min_length=10, max_length=6000)
    property_situation: Literal["owner", "renter", "other", "unknown"] = "unknown"
    displaced: bool = False
    immediate_needs: list[Literal["shelter", "food", "clothing", "transportation", "cleanup"]] = Field(
        default_factory=list, max_length=5
    )

    @field_validator("incident_date")
    @classmethod
    def not_future(cls, value):
        from datetime import datetime
        from zoneinfo import ZoneInfo

        if value > datetime.now(ZoneInfo("America/Chicago")).date():
            raise ValueError("Incident date cannot be in the future")
        return value


class DamageInput(Model):
    item: str = Field(min_length=2, max_length=120)
    area: str = Field(min_length=1, max_length=100)
    observation: str = Field(min_length=3, max_length=1800)


class TaskInput(Model):
    title: str = Field(min_length=3, max_length=160)
    explanation: str = Field(default="", max_length=1000)
    priority: Literal["urgent", "high", "normal"] = "normal"
    due_date: date | None = None


class TaskPatch(Model):
    status: Literal["todo", "done"]


class InsuranceInput(Model):
    insurer: str = Field(default="", max_length=150)
    policy_number: str = Field(default="", max_length=100)
    claim_number: str = Field(default="", max_length=100)
    notes: str = Field(default="", max_length=3000)


class ContactInput(Model):
    organization: str = Field(min_length=2, max_length=150)
    contacted_on: date
    notes: str = Field(min_length=2, max_length=1500)


class Consent(Model):
    consent: Literal[True]


class ChatInput(Consent):
    question: str = Field(min_length=3, max_length=2000)


class Observation(Model):
    item: str = Field(min_length=1, max_length=120)
    area: str = Field(max_length=100)
    observation: str = Field(min_length=1, max_length=1800)
    evidence_ids: list[str] = Field(min_length=1, max_length=10)
    uncertainty: str = Field(max_length=1000)


class PolicyExtraction(Model):
    policy_identifier: str = Field(max_length=150)
    coverage_wording: list[str] = Field(max_length=12)
    exclusions: list[str] = Field(max_length=12)
    deductible_wording: str = Field(max_length=1000)
    insurer_questions: list[str] = Field(max_length=12)


class AnalysisOutput(Model):
    summary: str = Field(max_length=3000)
    observations: list[Observation] = Field(max_length=30)
    missing_details: list[str] = Field(max_length=15)
    uncertainties: list[str] = Field(max_length=15)
    policy: PolicyExtraction


class AssistantOutput(Model):
    answer: str = Field(min_length=1, max_length=7000)
    resource_ids: list[str] = Field(max_length=10)
    uncertainties: list[str] = Field(max_length=10)


class PlanStep(Model):
    title: str = Field(max_length=160)
    explanation: str = Field(max_length=1000)
    priority: Literal["urgent", "high", "normal"]
    required_information: list[str] = Field(max_length=8)
    responsible_party: str = Field(max_length=120)
    resource_ids: list[str] = Field(max_length=5)
    status: Literal["suggested"]


class PlanOutput(Model):
    steps: list[PlanStep] = Field(max_length=12)
    uncertainties: list[str] = Field(max_length=10)
