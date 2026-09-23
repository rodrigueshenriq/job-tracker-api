"""Response contracts for the agent demo and human approval boundary."""

from datetime import date
from typing import List, Literal

from pydantic import BaseModel, Field


class CandidateProfile(BaseModel):
    skills: List[str]
    experience_summary: str
    education: str
    languages: List[str]


class ApplicationHistoryItem(BaseModel):
    application_id: str
    company: str
    position: str
    status: str
    applied_on: date


class ApplicationHistory(BaseModel):
    applications: List[ApplicationHistoryItem]


class PrepareApplicationResult(BaseModel):
    application_id: Literal["demo-001", "demo-002"] = Field(
        ...,
        description="Use exactly one of the enumerated application IDs.",
    )
    result: Literal["interview", "rejected", "offer", "withdrawn"] = Field(
        ...,
        description=(
            "Use only one of the enumerated values: interview, rejected, offer, or "
            "withdrawn. Do not include explanations, sentences, or additional notes. "
            "Map an 'accepted' outcome to offer."
        ),
    )

    class Config:
        extra = "forbid"


class ApplicationResultSummary(BaseModel):
    application_id: str
    result: str


class PreparedApplicationResult(BaseModel):
    approval_token: str
    summary: ApplicationResultSummary
    expires_in_seconds: int


class ConfirmApplicationResult(BaseModel):
    approval_token: str = Field(..., min_length=1)

    class Config:
        extra = "forbid"


class RecordedApplicationResult(ApplicationResultSummary):
    pass
