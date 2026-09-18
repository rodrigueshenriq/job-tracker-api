import asyncio
import json
import os
import unittest

# main.py creates tables during import. Never use the repository's SQLite file.
os.environ["DATABASE_URL"] = "sqlite://"

from database.database import SessionLocal, engine  # noqa: E402
from main import app  # noqa: E402
from models.models import JobApplication  # noqa: E402


async def get_json(path):
    messages = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        messages.append(message)

    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": b"",
        "root_path": "",
        "headers": [],
        "client": ("testclient", 0),
        "server": ("testserver", 80),
    }
    await app(scope, receive, send)
    body = b"".join(
        message.get("body", b"")
        for message in messages
        if message["type"] == "http.response.body"
    )
    return messages[0]["status"], json.loads(body)


class AgentReadToolsTests(unittest.TestCase):
    def test_candidate_profile_is_fixed_and_fictional(self):
        status, profile = asyncio.run(get_json("/agent/candidate-profile"))
        self.assertEqual(status, 200)
        self.assertEqual(
            profile,
            {
                "skills": ["Python", "FastAPI", "SQL", "REST APIs", "automated testing"],
                "experience_summary": "Three years building small web APIs and data workflows in fictional demo projects.",
                "education": "Bachelor's degree in Computer Science (fictional)",
                "languages": ["English", "Portuguese"],
            },
        )
        self.assertEqual(profile, asyncio.run(get_json("/agent/candidate-profile"))[1])

    def test_application_history_is_fixed_and_fictional(self):
        status, history = asyncio.run(get_json("/agent/application-history"))
        self.assertEqual(status, 200)
        self.assertEqual(
            history,
            {
                "applications": [
                    {
                        "application_id": "demo-001",
                        "company": "Fictional Data Studio",
                        "position": "Backend Developer",
                        "status": "interview",
                        "applied_on": "2025-01-15",
                    },
                    {
                        "application_id": "demo-002",
                        "company": "Fictional Cloud Workshop",
                        "position": "API Engineer",
                        "status": "rejected",
                        "applied_on": "2025-02-10",
                    },
                ]
            },
        )
        self.assertEqual(history, asyncio.run(get_json("/agent/application-history"))[1])

    def test_agent_responses_do_not_depend_on_application_database(self):
        self.assertEqual(str(engine.url), "sqlite://")
        before = [
            asyncio.run(get_json(path))[1]
            for path in ("/agent/candidate-profile", "/agent/application-history")
        ]
        with SessionLocal() as db:
            decoy = JobApplication(
                company="DATABASE SENTINEL",
                position="Private role",
                status="applied",
                notes="Must never appear in agent data",
            )
            db.add(decoy)
            db.commit()
            try:
                after = [
                    asyncio.run(get_json(path))[1]
                    for path in ("/agent/candidate-profile", "/agent/application-history")
                ]
                self.assertEqual(after, before)
                self.assertNotIn("DATABASE SENTINEL", json.dumps(after))
            finally:
                db.delete(decoy)
                db.commit()

    def test_openapi_has_exact_operation_ids_and_get_only(self):
        paths = app.openapi()["paths"]
        self.assertEqual(
            {path for path in paths if path.startswith("/agent")},
            {"/agent/candidate-profile", "/agent/application-history"},
        )
        self.assertEqual(set(paths["/agent/candidate-profile"]), {"get"})
        self.assertEqual(set(paths["/agent/application-history"]), {"get"})
        self.assertEqual(
            paths["/agent/candidate-profile"]["get"]["operationId"],
            "get_candidate_profile",
        )
        self.assertEqual(
            paths["/agent/application-history"]["get"]["operationId"],
            "get_application_history",
        )


if __name__ == "__main__":
    unittest.main()
