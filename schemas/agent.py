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
    application_id: Literal["demo-001", "demo-002"]
    result: Literal["interview", "rejected", "offer", "withdrawn"]

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
