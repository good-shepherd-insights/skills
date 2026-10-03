from __future__ import annotations

import argparse
import json
import secrets
import stat
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import uvicorn
from starlette.applications import Starlette
from starlette.background import BackgroundTask
from starlette.requests import Request
from starlette.responses import JSONResponse, Response, StreamingResponse
from starlette.routing import Route

HOP_BY_HOP_HEADERS = {
    b"connection",
    b"keep-alive",
    b"proxy-authenticate",
    b"proxy-authorization",
    b"te",
    b"trailers",
    b"transfer-encoding",
    b"upgrade",
}
A2A_CARD_PATH = "/.well-known/agent-card.json"
A2A_SECURITY_SCHEME = "bearerAuth"
RESPONSE_EXCLUDED_HEADERS = HOP_BY_HOP_HEADERS | {b"date", b"server"}


def load_bearer_key(path: Path) -> str:
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise ValueError(f"Bearer key file must not be accessible by group or others: {path}")
    key = path.read_text(encoding="utf-8").strip()
    if len(key) < 32:
        raise ValueError("Bearer key must contain at least 32 characters")
    return key


def _is_authorized(authorization: str | None, bearer_key: str) -> bool:
    if authorization is None:
        return False
    scheme, separator, token = authorization.partition(" ")
    return bool(
        separator
        and scheme.casefold() == "bearer"
        and token
        and secrets.compare_digest(token, bearer_key)
    )


def _request_headers(request: Request) -> list[tuple[bytes, bytes]]:
    return [
        (name, value)
        for name, value in request.headers.raw
        if name.lower() not in HOP_BY_HOP_HEADERS | {b"authorization", b"host"}
    ]


def _response_headers(response: httpx.Response) -> list[tuple[bytes, bytes]]:
    return [
        (name, value)
        for name, value in response.headers.raw
        if name.lower() not in RESPONSE_EXCLUDED_HEADERS
    ]


def _secure_agent_card(card: dict[str, object], public_url: str) -> dict[str, object]:
    for interface in card.get("supportedInterfaces", []):
        if not isinstance(interface, dict):
            continue
        raw_url = interface.get("url")
        if isinstance(raw_url, str):
            interface["url"] = f"{public_url}{urlsplit(raw_url).path}"

    security_requirement = {"schemes": {A2A_SECURITY_SCHEME: {}}}
    card["securitySchemes"] = {
        A2A_SECURITY_SCHEME: {
            "httpAuthSecurityScheme": {
                "scheme": "bearer",
                "bearerFormat": "API_KEY",
                "description": "Shared bearer key for A2A action routes.",
            }
        }
    }
    card["securityRequirements"] = [security_requirement]
    for skill in card.get("skills", []):
        if isinstance(skill, dict):
            skill["securityRequirements"] = [security_requirement]
    return card


def create_app(
    *,
    bearer_key: str,
    upstream: str,
    public_url: str,
    transport: httpx.AsyncBaseTransport | None = None,
) -> Starlette:
    upstream = upstream.rstrip("/")
    public_url = public_url.rstrip("/")

    @asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncIterator[None]:
        app.state.upstream = httpx.AsyncClient(
            base_url=upstream,
            timeout=None,
            follow_redirects=False,
            transport=transport,
        )
        try:
            yield
        finally:
            await app.state.upstream.aclose()

    async def proxy(request: Request) -> Response:
        if (request.url.path == "/a2a" or request.url.path.startswith("/a2a/")) and not _is_authorized(
            request.headers.get("authorization"), bearer_key
        ):
            return JSONResponse(
                {"error": "unauthorized"},
                status_code=401,
                headers={"WWW-Authenticate": 'Bearer realm="fast-agent-a2a"'},
            )

        client: httpx.AsyncClient = request.app.state.upstream
        upstream_request = client.build_request(
            request.method,
            request.url.path,
            params=request.query_params.multi_items(),
            headers=_request_headers(request),
            content=request.stream(),
        )
        try:
            upstream_response = await client.send(upstream_request, stream=True)
        except httpx.RequestError:
            return JSONResponse({"error": "upstream_unavailable"}, status_code=502)

        if request.url.path == A2A_CARD_PATH and upstream_response.is_success:
            payload = await upstream_response.aread()
            await upstream_response.aclose()
            try:
                card = _secure_agent_card(json.loads(payload), public_url)
            except (json.JSONDecodeError, TypeError):
                return JSONResponse({"error": "invalid_agent_card"}, status_code=502)
            return JSONResponse(card)

        response = StreamingResponse(
            upstream_response.aiter_raw(),
            status_code=upstream_response.status_code,
            background=BackgroundTask(upstream_response.aclose),
        )
        response.raw_headers = _response_headers(upstream_response)
        return response

    return Starlette(
        routes=[
            Route(
                "/{path:path}",
                proxy,
                methods=["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"],
            )
        ],
        lifespan=lifespan,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Bearer-authenticated proxy for fast-agent A2A")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--upstream", default="http://127.0.0.1:8001")
    parser.add_argument("--public-url", required=True)
    parser.add_argument("--key-file", type=Path, required=True)
    args = parser.parse_args()

    uvicorn.run(
        create_app(
            bearer_key=load_bearer_key(args.key_file),
            upstream=args.upstream,
            public_url=args.public_url,
        ),
        host=args.host,
        port=args.port,
        log_level="warning",
    )


if __name__ == "__main__":
    main()
