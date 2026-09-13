---
name: agentfield-api-schemas
version: 1.0.0
description: "Use when calling the Good Shepherd Insights AgentField fleet over HTTP or `af call` — the five public URLs (agents/swe/research/pr/sec.goodshepherdinsights.com), every reasoner endpoint with its full input schema, sync/async execution patterns, and result polling. Schema data generated from the live control-plane registry 2026-09-13."
---

# AgentField Fleet — API Schemas (Good Shepherd Insights)

Calling convention for the deployed AgentField fleet. The complete, per-reasoner
input schemas live in `references/api-schemas.md` (generated verbatim from the
live control-plane registry on 2026-09-13) — load it before constructing any payload.

## Endpoints

| Node | Purpose | Public base URL | Local |
|---|---|---|---|
| control plane | dashboard, registry, orchestration | https://agents.goodshepherdinsights.com | http://localhost:8080 |
| swe-planner | SWE-AF autonomous engineering fleet | https://swe.goodshepherdinsights.com | http://localhost:8002 |
| meta_deep_research | deep research engine (~10k invocations/query) | https://research.goodshepherdinsights.com | http://localhost:8003 |
| pr-af | AI pull-request reviewer | https://pr.goodshepherdinsights.com | http://localhost:8004 |
| sec-af | codebase security QA | https://sec.goodshepherdinsights.com | http://localhost:8005 |

## Calling a reasoner

Every reasoner: `POST <base>/api/v1/execute/<node_id>.<reasoner_id>` with body
`{"input": { ... }}` matching the schema in `references/api-schemas.md`.

Sync (blocks until done):

```bash
curl -sS https://pr.goodshepherdinsights.com/api/v1/execute/pr-af.review \
  -H 'Content-Type: application/json' \
  -d '{"input": {"pr_url": "https://github.com/OWNER/REPO/pull/123"}}'
```

Async (returns `{"execution_id": ...}` immediately; poll until terminal state):

```bash
curl -sS https://sec.goodshepherdinsights.com/api/v1/execute/async/sec-af.audit \
  -H 'Content-Type: application/json' \
  -d '{"input": {"repo_url": "https://github.com/OWNER/REPO"}}'
# poll:
curl -sS https://sec.goodshepherdinsights.com/api/v1/execution/<execution_id>/result
```

From this machine the `af` CLI wraps the same calls:

```bash
af call pr-af.review --in '{"pr_url": "https://github.com/OWNER/REPO/pull/123"}'
af tail <execution_id>     # watch a run
```

Node health: `GET /health` on each host. The registry source of truth is
`GET http://localhost:8080/api/v1/nodes` — includes manually-spawned nodes that
`af list` does not show.

## Schema reference

`references/api-schemas.md` — all 79 public reasoner endpoints with full input
schemas (required fields marked *REQUIRED*; internal-only reasoners listed and
excluded per node). No API keys in this repo: reasoners accept optional
`model`/`api_key` params resolved from the node's own secret store.

## Regenerating

When the fleet changes, regenerate from the live registry:
`GET http://localhost:8080/api/v1/nodes` → emit `<node>.<reasoner>` + `input_schema`
per reasoner. The committed file was produced exactly this way on 2026-09-13.
