"""Curated OpenAPI for agent tools; the human confirmation route is excluded."""

from fastapi import FastAPI

from routers.agent import tool_router

AGENT_TOOL_SERVER_URL = (
    "https://job-agent-api.lemoncoast-97f1175c.brazilsouth.azurecontainerapps.io"
)


def build_agent_tool_openapi():
    tool_app = FastAPI(title="Job Application Agent Demo Tools")
    tool_app.include_router(tool_router, prefix="/agent", tags=["Agent Demo"])
    schema = tool_app.openapi()
    schema["servers"] = [{"url": AGENT_TOOL_SERVER_URL}]
    return schema
