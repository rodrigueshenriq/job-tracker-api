"""Response contracts for the read-only agent demo routes."""

from datetime import date
from typing import List

from pydantic import BaseModel


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
