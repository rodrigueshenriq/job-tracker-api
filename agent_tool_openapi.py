"""Curated OpenAPI for agent tools; the human confirmation route is excluded."""

from fastapi import FastAPI

from routers.agent import tool_router


def build_agent_tool_openapi():
    tool_app = FastAPI(title="Job Application Agent Demo Tools")
    tool_app.include_router(tool_router, prefix="/agent", tags=["Agent Demo"])
    return tool_app.openapi()
