#!/usr/bin/env python3
"""Trigger and track PR-AF reviews through an AgentField control plane."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_BASE_URL = "https://control-plane-production-ddb8.up.railway.app"
TERMINAL_STATUSES = {
    "cancelled",
    "completed",
    "failed",
    "succeeded",
    "success",
    "timed_out",
    "timeout",
}
SUCCESS_STATUSES = {"completed", "succeeded", "success"}
PR_PATH = re.compile(r"^/[^/]+/[^/]+/pull/[1-9][0-9]*/?$")


class ApiError(RuntimeError):
    """Represent an HTTP or response-contract failure."""


def api_key() -> str:
    value = os.environ.get("AGENTFIELD_API_KEY", "").strip()
    if not value:
        raise ApiError("AGENTFIELD_API_KEY is not set")
    return value


def base_url(value: str | None) -> str:
    selected = value or os.environ.get("PR_AF_CONTROL_PLANE_URL") or DEFAULT_BASE_URL
    parsed = urllib.parse.urlparse(selected)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ApiError("control-plane URL must be an absolute HTTP(S) URL")
    return selected.rstrip("/")


def validate_pr_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme != "https" or parsed.netloc.lower() != "github.com":
        raise ApiError("PR URL must use https://github.com")
    if not PR_PATH.fullmatch(parsed.path) or parsed.query or parsed.fragment:
        raise ApiError("PR URL must match https://github.com/OWNER/REPO/pull/NUMBER")
    return value


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload, separators=(",", ":")).encode()
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-API-Key": api_key(),
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raw = error.read().decode("utf-8", errors="replace")
        if error.code == 401:
            raise ApiError("authentication failed: AGENTFIELD_API_KEY is missing or invalid") from error
        raise ApiError(f"HTTP {error.code}: {raw}") from error
    except urllib.error.URLError as error:
        raise ApiError(f"request failed: {error.reason}") from error

    try:
        result = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ApiError("control plane returned non-JSON content") from error
    if not isinstance(result, dict):
        raise ApiError("control plane returned an unexpected JSON shape")
    return result


def get_status(control_plane: str, execution_id: str) -> dict[str, Any]:
    safe_id = urllib.parse.quote(execution_id, safe="")
    return request_json("GET", f"{control_plane}/api/v1/executions/{safe_id}")


def wait_for_execution(
    control_plane: str,
    execution_id: str,
    interval: float,
    timeout: float,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    last_status = "unknown"
    while True:
        result = get_status(control_plane, execution_id)
        last_status = str(result.get("status", "unknown")).lower()
        print(json.dumps(result, indent=2, sort_keys=True), flush=True)
        if last_status in TERMINAL_STATUSES:
            return result
        if time.monotonic() >= deadline:
            raise ApiError(
                f"polling timed out; execution {execution_id} last reported status {last_status}"
            )
        time.sleep(interval)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="override the AgentField control-plane URL")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start", help="queue a PR-AF review")
    start.add_argument("pr_url", help="GitHub pull-request URL")
    start.add_argument("--wait", action="store_true", help="poll until a terminal status")
    start.add_argument("--interval", type=float, default=15, help="poll interval in seconds")
    start.add_argument("--timeout", type=float, default=3600, help="polling timeout in seconds")

    status = subparsers.add_parser("status", help="read one execution status")
    status.add_argument("execution_id")

    wait = subparsers.add_parser("wait", help="poll an existing execution")
    wait.add_argument("execution_id")
    wait.add_argument("--interval", type=float, default=15, help="poll interval in seconds")
    wait.add_argument("--timeout", type=float, default=3600, help="polling timeout in seconds")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        control_plane = base_url(args.base_url)
        if args.command == "start":
            result = request_json(
                "POST",
                f"{control_plane}/api/v1/execute/async/pr-af.review",
                {"input": {"pr_url": validate_pr_url(args.pr_url)}},
            )
            print(json.dumps(result, indent=2, sort_keys=True))
            execution_id = result.get("execution_id")
            if not isinstance(execution_id, str) or not execution_id:
                raise ApiError("start response did not include execution_id")
            if args.wait:
                result = wait_for_execution(
                    control_plane, execution_id, args.interval, args.timeout
                )
                return 0 if str(result.get("status", "")).lower() in SUCCESS_STATUSES else 1
            return 0
        if args.command == "status":
            print(json.dumps(get_status(control_plane, args.execution_id), indent=2, sort_keys=True))
            return 0
        result = wait_for_execution(
            control_plane, args.execution_id, args.interval, args.timeout
        )
        return 0 if str(result.get("status", "")).lower() in SUCCESS_STATUSES else 1
    except ApiError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
