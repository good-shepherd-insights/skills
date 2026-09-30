---
name: streamctl-containers
description: Use when calling the streamctl container API to build, deploy, or destroy Streamlit apps on Cloudflare - one HMAC-signed HTTP POST per app, public URL <app>.marylandinsights.com. Covers the full API surface (create/destroy/status), request schema, signing, response shapes, status polling, and failure debugging.
metadata:
  hermes:
    tags: [streamctl, containers, cloudflare, streamlit, api]
    related_skills: [cloudflare, durable-objects]
---

# streamctl Containers API

## Overview

`streamctl` turns one signed HTTP call into a running app. The caller sends app
requirements (name, git repo, port); a deterministic build system clones the
repo, builds the Docker image, pushes it to Cloudflare's registry, deploys the
container worker, wires DNS + route on `marylandinsights.com`, polls until the
public URL returns 200, and reports the verified URL. A `destroy` call deletes
every object and the URL goes dead. There is no AI in the pipeline and no CLI
step for the caller - the HTTPS request is the entire interface.

Two router backends share one contract:

| Backend | Base URL | Notes |
|---|---|---|
| Self-host (Backend B) | `http://127.0.0.1:8516` (LAN) | FastAPI; also serves as the reference implementation |
| CF Worker (Backend A) | `https://router.marylandinsights.com` | Same routes, same signing |

## Authentication: HMAC signature

Every POST/DELETE to `/v1/intents` needs two things:

1. Body is **compact JSON** (no spaces after separators).
2. A `mac` header: `HMAC-SHA256(secret, body_bytes + str(issued_at_millis))`
   where `issued_at_millis` is inside the body.

Python signing exactly:

```python
import json, hmac, hashlib, time
secret = conf["HMAC_SECRET"].encode()          # shared key, server-side
intent = {
    "id": f"api-{int(time.time())}",           # globally unique caller-chosen id
    "action": "create",                        # or "destroy"
    "target": "container",                     # app runs in a CF Container
    "app": "myapp",                            # DNS-safe label: ^[a-z][a-z0-9-]{1,30}$
    "repo": "https://github.com/org/my-app.git",  # required; repo root must contain a Dockerfile
    "port": 8501,                              # optional; conf CONTAINER_PORT default
    "issued_at": int(time.time() * 1000),      # milliseconds; 300s replay window
}
body = json.dumps(intent, separators=(",", ":"), ensure_ascii=False).encode()
intent["mac"] = hmac.new(secret, body + str(intent["issued_at"]).encode(), hashlib.sha256).hexdigest()
```

`mac` goes in the POST body (re-serialized exactly as above), not in a header
line of its own - the signed object plus `mac` is the JSON request body.

## Endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/v1/intents` | mac header in body | create or destroy an app |
| GET | `/v1/intents/{id}` | none (id is capability URL) | status polling + steps + failed_reason |
| DELETE | `/v1/intents/{id}` | signed | cancel a pending intent |
| GET | `/v1/intents/{unknown}` | - | 404 `{"error": "unknown intent: <id>"}` |

## Create: request -> URL out

### 1. Build the intent and POST it (see signing above)

Response, 202:

```json
{"id": "api-1790712353", "status": "pending",
 "url": "https://router.marylandinsights.com/v1/intents/api-1790712353"}
```

### 2. Poll GET /v1/intents/{id} until terminal

`status` is one of `pending | building | done | failed`. While `building`,
`steps` shows per-stage progress - each is `{step, status, ts}`:

```
fetch:ok,build:ok,push:ok,render:ok,npm:ok,deploy:ok,wire:ok,health:ok,verify:ok
```

| Step | What it does | Failure means |
|---|---|---|
| fetch | `git clone --depth 1` of `repo` under WORK_ROOT/app | bad URL, no Dockerfile |
| build | `docker build -t <image>` | Dockerfile error, no docker daemon access |
| push | `wrangler containers push registry.cloudflare.com/<acct>/<app>-<sha12>:<tag>` | registry auth, tag rules (below) |
| render | wrangler.toml + index.ts from templates (workers_dev=false pinned) | template missing |
| npm | `npm install` the `@cloudflare/containers` dep in the deploy dir | bad package spec |
| deploy | `wrangler deploy` (env CLOUDFLARE_API_TOKEN only) | bundling errors, CF validation |
| wire | DNS A record + workers route on `<app>`.<PUBLIC_DOMAIN> | CF API perm |
| health | poll public URL until 200 (or timeout, HEALTH_TIMEOUT_SEC) | app boot slow/dead |
| verify | final public check; the step list ends with `verify` | URL not live |

### 3. Terminal responses

`done`:

```json
{"id": "...", "status": "done", "app": "myapp",
 "hostname": "myapp.marylandinsights.com", "verified": true,
 "steps": [...]}
```

`failed`:

```json
{"id": "...", "status": "failed", "app": "myapp",
 "failed_reason": "`npx wrangler...` failed: VALIDATE_INPUT image Invalid image. Latest tags are not allowed on images.",
 "steps": [{"step": "deploy", "status": "failed", "ts": 1790733976354}]}
```

`failed_reason` carries the actual tool error tail. On failure the public URL
does not resolve (wired only on success) and the workdir can be inspected at
`$WORK_ROOT/<app>`.

## Destroy

Same POST, `action: "destroy"`, same `app`. Reverse-order teardown: worker
route -> DNS record -> worker script -> container application. Steps in the
response mirror the deletions; destroy on a missing app is a no-op success
(idempotent). Terminal statuses are identical (`done` / `failed`), so the same
polling loop works.

## Idempotency rules

- Re-POST a create for a live app: allowed, it redeploys (new image hash, same URL).
- Re-POST a destroy after everything is gone: `done` no-op.
- Caller-chosen `id` must be unique per logical attempt; a retried identical id
  maps to the same row.

## Constraints baked into the platform (do not work around)

| Constraint | Reason |
|---|---|
| Image refs must be `registry.cloudflare.com/<account>/...:<concrete-tag>` | CF accepts only its managed registry namespace and rejects `:latest` |
| `@cloudflare/containers` dep: `^0.3.7` | `1.x` does not exist on npm; 0.3.7 is the proven line |
| Registry auth via `wrangler containers push` | raw `docker login` with an API token returns 401 - CF mints short-lived push creds internally |
| `workers_dev = false` in every rendered config | custom domain only; no workers.dev exposure, ever |
| Every operational value from conf | zero literals in source; streamctl.conf carries zone, account, domain, ports, paths |

## streamctl.conf keys (operator side)

```ini
PUBLIC_DOMAIN = marylandinsights.com
CF_API_BASE = https://api.cloudflare.com/client/v4
CF_ZONE_ID  = <zone>
CF_ACCOUNT_ID = <account>
CF_REGISTRY_HOST = registry.cloudflare.com
CF_API_KEY_FILE = /etc/streamctl/cf.key      # 0600, mounted by the router
HMAC_SECRET = <shared caller key>
WORK_ROOT = /var/lib/streamctl/work
CONTAINER_PORT = 8501
CONTAINER_MAX_INSTANCES = 2
TARGETS = home,container
HEALTH_POLL_SEC = 15
HEALTH_TIMEOUT_SEC = 420
WRANGLER_BIN = npx wrangler
NPM_BIN = npm
CF_CONTAINERS_PKG = @cloudflare/containers@^0.3.7
```

Callers need only `HMAC_SECRET` and the router base URL - no CF token ever
touches the caller.

## Failure debugging playbook

1. GET the intent, read `failed_reason` + last step.
2. Build-step `permission denied ... docker.sock`: the router process needs docker
   group access (run it under `sg docker -c '...'`).
3. Push 401/`no basic auth credentials`: image ref not namespaced, or auth not via
   wrangler. Use `wrangler containers push` only.
4. `Latest tags are not allowed`: tag suffix must be a concrete tag (v1, sha).
5. Deploy `Could not resolve "@cloudflare/containers"`: deploy dir missing
   package.json/npm step, or wrong version spec (`^1.0.0` does not exist).
6. `VALIDATE_INPUT` on deploy: read the misconfiguration text; it echoes the
   rendered `[[containers]]` block that failed.
7. Health timeout but 200 works from a browser: container boot slow - raise
   `HEALTH_TIMEOUT_SEC`.
8. 522 on a just-wired custom domain: propagation; retry a few minutes.

## Common Pitfalls

1. **Re-serializing after signing.** If you add fields after computing `mac`, the
   signature is dead. Compute `mac` last, then serialize once.
2. **Seconds vs milliseconds in `issued_at`.** Seconds old + 300s window =>
   `401 stale intent`. Use `int(time.time() * 1000)`.
3. **Compact separators are not optional.** Pretty-printed JSON (spaces) changes
   the canonical bytes and breaks the MAC.
4. **Assuming `done` means instant.** Docker build + registry push + CF deploy is
   minutes; poll, don't loop-fire.
5. **Polling GET for auth decisions.** GET is 404 for unknown ids and unsigned
   POSTs are rejected before id lookup; don't infer auth state from GETs.

## Verification Checklist

- [ ] Signed POST returned 202 with a `pending` row and a status URL
- [ ] GET shows `verify:ok` in `steps` and `verified: true`
- [ ] `https://<app>.<PUBLIC_DOMAIN>/` returns 200 with the app title
- [ ] Destroy intent's step list ends with `verify` (URL dead check)
- [ ] No `*.workers.dev` hostname ever served public traffic for the app
- [ ] All new operational values landed in conf, not in code