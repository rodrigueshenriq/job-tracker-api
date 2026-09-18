import asyncio
import json
import os
import unittest

# main.py creates tables during import. Force an isolated in-memory database first.
os.environ["DATABASE_URL"] = "sqlite://"

from main import app  # noqa: E402
from database.database import engine  # noqa: E402


class BaselineTests(unittest.TestCase):
    def test_app_is_created_with_in_memory_database(self):
        self.assertEqual(app.title, "FastAPI")
        self.assertEqual(str(engine.url), "sqlite://")

    def test_openapi_endpoint_is_available(self):
        async def request_openapi():
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
                "path": "/openapi.json",
                "raw_path": b"/openapi.json",
                "query_string": b"",
                "root_path": "",
                "headers": [],
                "client": ("testclient", 0),
                "server": ("testserver", 80),
            }
            await app(scope, receive, send)
            return messages

        messages = asyncio.run(request_openapi())
        self.assertEqual(messages[0]["status"], 200)
        body = b"".join(
            message.get("body", b"")
            for message in messages
            if message["type"] == "http.response.body"
        )
        self.assertEqual(json.loads(body)["openapi"], "3.0.2")

    def test_existing_crud_routes_are_present(self):
        operations = {
            (method.upper(), path)
            for path, methods in app.openapi()["paths"].items()
            for method in methods
        }
        self.assertEqual(
            operations,
            {
                ("GET", "/"),
                ("POST", "/applications/"),
                ("GET", "/applications/"),
                ("GET", "/applications/{application_id}"),
                ("PUT", "/applications/{application_id}"),
                ("DELETE", "/applications/{application_id}"),
            },
        )

    def test_agent_routes_are_absent(self):
        self.assertFalse(
            any(path.startswith("/agent") for path in app.openapi()["paths"])
        )


if __name__ == "__main__":
    unittest.main()
