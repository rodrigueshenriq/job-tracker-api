"""Fictional agent tools and the separate human confirmation endpoint."""

import os
from copy import deepcopy
from secrets import compare_digest
from typing import Optional

from fastapi import APIRouter, Header, HTTPException

from agent_store import PENDING_TTL_SECONDS, confirm_result, prepare_result
from demo_data import APPLICATION_HISTORY, CANDIDATE_PROFILE
from schemas.agent import (
    ApplicationHistory,
    CandidateProfile,
    ConfirmApplicationResult,
    PrepareApplicationResult,
    PreparedApplicationResult,
    RecordedApplicationResult,
)

# Only tool_router is included in the curated agent OpenAPI document.
tool_router = APIRouter()
# confirmation_router belongs exclusively to the trusted human/UI surface.
confirmation_router = APIRouter()


@tool_router.get(
    "/candidate-profile",
    response_model=CandidateProfile,
    operation_id="get_candidate_profile",
)
def get_candidate_profile():
    return deepcopy(CANDIDATE_PROFILE)


@tool_router.get(
    "/application-history",
    response_model=ApplicationHistory,
    operation_id="get_application_history",
)
def get_application_history():
    return deepcopy(APPLICATION_HISTORY)


@tool_router.post(
    "/application-results/prepare",
    response_model=PreparedApplicationResult,
    operation_id="prepare_application_result",
)
def prepare_application_result(request: PrepareApplicationResult):
    token = prepare_result(request.application_id, request.result)
    if token is None:
        raise HTTPException(status_code=409, detail="Application already pending or recorded")
    return {
        "approval_token": token,
        "summary": {"application_id": request.application_id, "result": request.result},
        "expires_in_seconds": PENDING_TTL_SECONDS,
    }


@confirmation_router.post(
    "/application-results/confirm",
    response_model=RecordedApplicationResult,
    operation_id="confirm_application_result",
)
def confirm_application_result(
    request: ConfirmApplicationResult,
    approval_key: Optional[str] = Header(None, alias="X-Human-Approval-Key"),
):
    configured_key = os.getenv("HUMAN_APPROVAL_KEY")
    if not configured_key:
        raise HTTPException(status_code=503, detail="Human approval is not configured")
    if not approval_key or not compare_digest(approval_key, configured_key):
        raise HTTPException(status_code=403, detail="Human approval credential required")
    result = confirm_result(request.approval_token)
    if result is None:
        raise HTTPException(status_code=404, detail="Approval request not found or expired")
    return result
