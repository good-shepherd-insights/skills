---
name: pr-af-review
description: Trigger and track pull-request reviews through the Good Shepherd Insights PR-AF AgentField control plane. Use when Codex is asked to run PR-AF against a GitHub pull request, check a PR-AF execution, wait for a review to finish, or reproduce the exact authenticated HTTP request for the deployed PR-AF instance.
---

# PR-AF Review

Trigger PR-AF through the verified AgentField control-plane endpoint and track the returned execution. Use `scripts/pr_af.py` for deterministic URL validation, authentication, JSON encoding, error handling, and polling.

## Requirements

- Require an explicit GitHub pull-request URL.
- Read the API key from `AGENTFIELD_API_KEY`. Never place the key in a command, skill file, repository file, response, or log.
- Default to `https://control-plane-production-ddb8.up.railway.app`.
- Override the control plane only with `PR_AF_CONTROL_PLANE_URL` or `--base-url` when the user supplies another instance.
- Treat starting a review as an external write because PR-AF may post GitHub review comments. Obtain explicit user authorization before `start` or `start --wait`.
- Treat `status` and `wait` as read-only.

## Start a review

Run:

```bash
python3 ~/.codex/skills/pr-af-review/scripts/pr_af.py start \
  https://github.com/OWNER/REPOSITORY/pull/NUMBER
```

To start and keep polling until a terminal state:

```bash
python3 ~/.codex/skills/pr-af-review/scripts/pr_af.py start \
  https://github.com/OWNER/REPOSITORY/pull/NUMBER --wait
```

Report the returned `execution_id`, `run_id`, `status`, and target. Do not claim that the review completed when the response says `queued` or `running`.

## Check or wait for an execution

Run one status request:

```bash
python3 ~/.codex/skills/pr-af-review/scripts/pr_af.py status EXECUTION_ID
```

Wait for a terminal state:

```bash
python3 ~/.codex/skills/pr-af-review/scripts/pr_af.py wait EXECUTION_ID
```

Use `--interval` and `--timeout` only when a different polling cadence or deadline is useful. A timeout stops local polling; it does not cancel the remote execution.

## HTTP contract

Read [references/api-contract.md](references/api-contract.md) when diagnosing authentication, routing, payload, or response-shape problems. Do not substitute the PR-AF node URL for the control-plane URL.

## Failure handling

- On `401`, report that `AGENTFIELD_API_KEY` is missing or invalid without displaying it.
- On `404`, verify that the base URL is the AgentField control plane and that the path is `/api/v1/execute/async/pr-af.review`.
- On a malformed GitHub URL, stop before making a request.
- On polling timeout, report the last observed status and execution ID.
- Never retry a `start` request automatically after an ambiguous network failure; first check whether an execution was created to avoid duplicate reviews.
