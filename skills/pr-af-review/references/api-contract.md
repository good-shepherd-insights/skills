# Verified PR-AF HTTP contract

Verified against the deployed Good Shepherd Insights AgentField control plane on 2026-07-16.

## Control plane

Default base URL:

```text
https://control-plane-production-ddb8.up.railway.app
```

The separately deployed PR-AF node URL exposes node health and reasoner metadata, but it does not expose the control-plane `/api/v1/execute/async/...` route.

## Authentication

Send the API key in this header:

```http
X-API-Key: <AGENTFIELD_API_KEY>
```

Keep the value in the `AGENTFIELD_API_KEY` environment variable. The control plane also advertises `Authorization: Bearer <token>`, but this skill uses `X-API-Key` because that form was verified successfully.

## Start an asynchronous review

```http
POST /api/v1/execute/async/pr-af.review
Content-Type: application/json
X-API-Key: <AGENTFIELD_API_KEY>

{"input":{"pr_url":"https://github.com/owner/repo/pull/123"}}
```

Verified queued response fields:

```json
{
  "execution_id": "exec_...",
  "run_id": "run_...",
  "workflow_id": "run_...",
  "status": "queued",
  "target": "pr-af.review",
  "type": "reasoner",
  "created_at": "...",
  "enqueued_at": "...",
  "webhook_registered": false
}
```

## Read execution status

```http
GET /api/v1/executions/{execution_id}
X-API-Key: <AGENTFIELD_API_KEY>
```

Verified running response fields:

```json
{
  "execution_id": "exec_...",
  "run_id": "run_...",
  "status": "running",
  "started_at": "...",
  "webhook_registered": false
}
```

Preserve and report any additional fields returned for terminal executions rather than assuming a fixed result schema.
