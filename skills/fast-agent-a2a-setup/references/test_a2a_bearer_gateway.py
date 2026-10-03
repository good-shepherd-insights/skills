from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

import httpx
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.routing import Route
from starlette.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from a2a_bearer_gateway import create_app, load_bearer_key

BEARER_KEY = "a" * 64
UPSTREAM_CARD = {
    "name": "fast-agent-a2a",
    "supportedInterfaces": [
        {"url": "http://127.0.0.1:8001/a2a/jsonrpc", "protocolBinding": "JSONRPC"},
        {"url": "http://127.0.0.1:8001/a2a/rest", "protocolBinding": "HTTP+JSON"},
    ],
    "skills": [{"id": "dev", "name": "dev"}, {"id": "manager", "name": "manager"}],
}


class GatewayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.requests: list[dict[str, object]] = []

        async def upstream(request: Request):
            self.requests.append(
                {
                    "path": request.url.path,
                    "query": request.url.query,
                    "authorization": request.headers.get("authorization"),
                    "body": await request.body(),
                }
            )
            if request.url.path == "/.well-known/agent-card.json":
                return JSONResponse(UPSTREAM_CARD)
            return StreamingResponse(iter([b"first", b"-second"]), media_type="text/plain")

        upstream_app = Starlette(routes=[Route("/{path:path}", upstream, methods=["GET", "POST"])])
        transport = httpx.ASGITransport(app=upstream_app)
        self.gateway = create_app(
            bearer_key=BEARER_KEY,
            upstream="http://upstream.test",
            public_url="https://a2a.example.com",
            transport=transport,
        )

    def test_agent_card_is_public_rewritten_and_advertises_bearer_auth(self) -> None:
        with TestClient(self.gateway) as client:
            response = client.get("/.well-known/agent-card.json")

        self.assertEqual(200, response.status_code)
        card = response.json()
        self.assertEqual(
            [
                "https://a2a.example.com/a2a/jsonrpc",
                "https://a2a.example.com/a2a/rest",
            ],
            [interface["url"] for interface in card["supportedInterfaces"]],
        )
        self.assertEqual("bearer", card["securitySchemes"]["bearerAuth"]["httpAuthSecurityScheme"]["scheme"])
        self.assertEqual({"schemes": {"bearerAuth": {}}}, card["securityRequirements"][0])
        self.assertTrue(all(skill["securityRequirements"] for skill in card["skills"]))

    def test_a2a_routes_reject_missing_or_invalid_keys(self) -> None:
        with TestClient(self.gateway) as client:
            boundary = client.get("/a2a")
            missing = client.post("/a2a/jsonrpc", content=b"request")
            invalid = client.post(
                "/a2a/jsonrpc",
                headers={"Authorization": "Bearer wrong"},
                content=b"request",
            )

        self.assertEqual(401, boundary.status_code)
        self.assertEqual(401, missing.status_code)
        self.assertEqual(401, invalid.status_code)
        self.assertEqual('Bearer realm="fast-agent-a2a"', missing.headers["www-authenticate"])
        self.assertEqual([], self.requests)

    def test_valid_key_streams_request_and_response_without_forwarding_key(self) -> None:
        with TestClient(self.gateway) as client:
            response = client.post(
                "/a2a/rest/message:stream?context=test",
                headers={"Authorization": f"Bearer {BEARER_KEY}"},
                content=b"request-body",
            )

        self.assertEqual(200, response.status_code)
        self.assertEqual("first-second", response.text)
        self.assertEqual(
            {
                "path": "/a2a/rest/message:stream",
                "query": "context=test",
                "authorization": None,
                "body": b"request-body",
            },
            self.requests[0],
        )

    def test_key_file_requires_private_permissions_and_minimum_length(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory, "a2a-bearer-key")
            path.write_text(BEARER_KEY, encoding="utf-8")
            path.chmod(0o600)
            self.assertEqual(BEARER_KEY, load_bearer_key(path))

            path.chmod(0o640)
            with self.assertRaisesRegex(ValueError, "group or others"):
                load_bearer_key(path)

            path.chmod(0o600)
            path.write_text("too-short", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "at least 32"):
                load_bearer_key(path)


if __name__ == "__main__":
    unittest.main()
