"""Public demo tools backed only by fixed fictional data."""

from copy import deepcopy

from fastapi import APIRouter

from demo_data import APPLICATION_HISTORY, CANDIDATE_PROFILE
from schemas.agent import ApplicationHistory, CandidateProfile

router = APIRouter()


@router.get(
    "/candidate-profile",
    response_model=CandidateProfile,
    operation_id="get_candidate_profile",
)
def get_candidate_profile():
    return deepcopy(CANDIDATE_PROFILE)


@router.get(
    "/application-history",
    response_model=ApplicationHistory,
    operation_id="get_application_history",
)
def get_application_history():
    return deepcopy(APPLICATION_HISTORY)
