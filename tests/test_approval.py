import asyncio
import json
import os
import unittest
from secrets import token_urlsafe
from unittest.mock import patch

os.environ["DATABASE_URL"] = "sqlite://"

import agent_store  # noqa: E402
from agent_tool_openapi import build_agent_tool_openapi  # noqa: E402
from database.database import SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from routers.applications import (  # noqa: E402
    create_application,
    delete_application,
    read_application,
    read_applications,
    update_application,
)
from schemas.schemas import ApplicationCreate, ApplicationUpdate  # noqa: E402

TEST_APPROVAL_KEY = token_urlsafe(32)
TEST_AGENT_API_KEY = os.environ.setdefault("AGENT_API_KEY", token_urlsafe(32))


async def request_json(method, path, payload=None, approval_key=None, agent_key=TEST_AGENT_API_KEY):
    messages = []
    body = json.dumps(payload).encode() if payload is not None else b""
    headers = [(b"content-type", b"application/json")]
    if approval_key is not None:
        headers.append((b"x-human-approval-key", approval_key.encode()))
    if agent_key is not None:
        headers.append((b"x-api-key", agent_key.encode()))

    async def receive():
        return {"type": "http.request", "body": body, "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": headers,
        "client": ("testclient", 0),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)
    response_body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return messages[0]["status"], json.loads(response_body)


class ApprovalFlowTests(unittest.TestCase):
    def setUp(self):
        self.assertEqual(str(engine.url), "sqlite://")
        with agent_store._lock:
            agent_store._pending.clear()
            agent_store._recorded.clear()

    def prepare(self, application_id="demo-001", result="offer"):
        return asyncio.run(
            request_json(
                "POST",
                "/agent/application-results/prepare",
                {"application_id": application_id, "result": result},
            )
        )

    def confirm(self, token, approval_key=TEST_APPROVAL_KEY):
        return asyncio.run(
            request_json(
                "POST",
                "/agent/application-results/confirm",
                {"approval_token": token},
                approval_key,
            )
        )

    def test_prepare_does_not_record_result(self):
        status, prepared = self.prepare()
        self.assertEqual(status, 200)
        self.assertEqual(prepared["summary"], {"application_id": "demo-001", "result": "offer"})
        self.assertGreaterEqual(len(prepared["approval_token"]), 32)
        self.assertEqual(agent_store._recorded, {})
        self.assertEqual(len(agent_store._pending), 1)

    def test_prepare_accepts_every_allowed_result(self):
        for result in ("interview", "rejected", "offer", "withdrawn"):
            with self.subTest(result=result):
                status, prepared = self.prepare(result=result)
                self.assertEqual(status, 200)
                self.assertEqual(
                    prepared["summary"],
                    {"application_id": "demo-001", "result": result},
                )
                with agent_store._lock:
                    agent_store._pending.clear()

    def test_prepare_requires_agent_key(self):
        payload = {"application_id": "demo-001", "result": "offer"}
        with patch.dict(os.environ, {"AGENT_API_KEY": TEST_AGENT_API_KEY}):
            self.assertEqual(asyncio.run(request_json("POST", "/agent/application-results/prepare", payload, agent_key=None))[0], 401)
            self.assertEqual(asyncio.run(request_json("POST", "/agent/application-results/prepare", payload, agent_key="wrong"))[0], 401)
            self.assertEqual(asyncio.run(request_json("POST", "/agent/application-results/prepare", payload))[0], 200)

    def test_human_confirmation_records_once_and_replay_is_rejected(self):
        token = self.prepare()[1]["approval_token"]
        with patch.dict(os.environ, {"HUMAN_APPROVAL_KEY": TEST_APPROVAL_KEY}):
            self.assertEqual(self.confirm(token), (200, {"application_id": "demo-001", "result": "offer"}))
            self.assertEqual(self.confirm(token)[0], 404)
        self.assertEqual(agent_store._recorded, {"demo-001": {"application_id": "demo-001", "result": "offer"}})
        self.assertEqual(agent_store._pending, {})

    def test_token_alone_cannot_approve(self):
        token = self.prepare()[1]["approval_token"]
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.confirm(token)[0], 503)
        with patch.dict(os.environ, {"HUMAN_APPROVAL_KEY": TEST_APPROVAL_KEY}):
            self.assertEqual(self.confirm(token, approval_key=None)[0], 403)
            self.assertEqual(self.confirm(token, approval_key="wrong")[0], 403)
        self.assertEqual(agent_store._recorded, {})
        self.assertIn(token, agent_store._pending)

    def test_invalid_and_expired_tokens_are_rejected(self):
        with patch.dict(os.environ, {"HUMAN_APPROVAL_KEY": TEST_APPROVAL_KEY}):
            self.assertEqual(self.confirm("invalid-token")[0], 404)
            token = self.prepare()[1]["approval_token"]
            agent_store._pending[token]["expires_at"] = 0
            self.assertEqual(self.confirm(token)[0], 404)
        self.assertEqual(agent_store._recorded, {})

    def test_invalid_values_and_agent_approval_flag_are_rejected(self):
        for payload in (
            {"application_id": "unknown", "result": "offer"},
            {"application_id": "demo-001", "result": "unknown"},
            {"application_id": "demo-001", "result": "accepted"},
            {
                "application_id": "demo-001",
                "result": (
                    "Change status to 'accepted' for application demo-001 at Fictional "
                    "Data Studio. Note: This is a prepared update only; do NOT submit or "
                    "finalize without human approval."
                ),
            },
            {"application_id": "demo-001", "result": "offer", "approved": True},
        ):
            with self.subTest(payload=payload):
                status, _ = asyncio.run(
                    request_json("POST", "/agent/application-results/prepare", payload)
                )
                self.assertEqual(status, 422)
        self.assertEqual(agent_store._pending, {})
        self.assertEqual(agent_store._recorded, {})

    def test_duplicate_pending_request_is_rejected(self):
        self.assertEqual(self.prepare()[0], 200)
        self.assertEqual(self.prepare()[0], 409)

    def test_existing_gets_and_crud_still_work(self):
        for path in ("/agent/candidate-profile", "/agent/application-history"):
            self.assertEqual(asyncio.run(request_json("GET", path))[0], 200)
        with SessionLocal() as db:
            created = create_application(ApplicationCreate(company="Fictional CRUD Check", position="Tester"), db)
            self.assertEqual(read_application(created.id, db).company, "Fictional CRUD Check")
            self.assertTrue(any(item.id == created.id for item in read_applications(db=db)))
            self.assertEqual(update_application(created.id, ApplicationUpdate(status="interview"), db).status, "interview")
            self.assertEqual(delete_application(created.id, db), {"detail": "Application deleted"})

    def test_curated_openapi_excludes_confirmation_and_crud(self):
        schema = build_agent_tool_openapi()
        self.assertEqual(
            schema["servers"],
            [
                {
                    "url": "https://job-agent-api.lemoncoast-97f1175c.brazilsouth.azurecontainerapps.io"
                }
            ],
        )
        paths = schema["paths"]
        self.assertEqual(
            {path: list(operations) for path, operations in paths.items()},
            {
                "/agent/candidate-profile": ["get"],
                "/agent/application-history": ["get"],
                "/agent/application-results/prepare": ["post"],
            },
        )
        self.assertEqual(paths["/agent/application-results/prepare"]["post"]["operationId"], "prepare_application_result")
        prepare_operation = paths["/agent/application-results/prepare"]["post"]
        request_schema_ref = prepare_operation["requestBody"]["content"][
            "application/json"
        ]["schema"]["$ref"]
        request_schema_name = request_schema_ref.rsplit("/", 1)[-1]
        request_schema = schema["components"]["schemas"][request_schema_name]
        self.assertEqual(
            request_schema["required"],
            ["application_id", "result"],
        )
        self.assertEqual(
            request_schema["properties"]["application_id"]["enum"],
            ["demo-001", "demo-002"],
        )
        self.assertEqual(
            request_schema["properties"]["result"]["enum"],
            ["interview", "rejected", "offer", "withdrawn"],
        )
        self.assertFalse(request_schema["additionalProperties"])
        result_description = request_schema["properties"]["result"]["description"]
        self.assertIn(
            "Do not include explanations, sentences, or additional notes",
            result_description,
        )
        self.assertIn("Map an 'accepted' outcome to offer", result_description)
        self.assertNotIn("/agent/application-results/confirm", paths)
        self.assertEqual(app.openapi()["paths"]["/agent/application-results/confirm"]["post"]["operationId"], "confirm_application_result")
        self.assertEqual(
            schema["components"]["securitySchemes"]["APIKeyHeader"],
            {"type": "apiKey", "in": "header", "name": "x-api-key"},
        )
        for operations in paths.values():
            for operation in operations.values():
                self.assertEqual(operation["security"], [{"APIKeyHeader": []}])
        self.assertNotIn("security", app.openapi()["paths"]["/agent/application-results/confirm"]["post"])


if __name__ == "__main__":
    unittest.main()
