---
name: fast-agent-a2a-setup
description: >-
  Use when provisioning or repairing a fast-agent A2A (Agent-to-Agent) service
  behind a Cloudflare-fronted bearer gateway. Covers the agent-card frontmatter
  contract (coordinator + implementer + tool-card pattern), the bearer-auth
  gateway, launchd cutover and rollback, streaming model-idle timeouts, and the
  Cloudflare 125-second non-streaming proxy-read-timeout caveat. Triggers on
  "set up fast-agent a2a", "configure a2a cards", "add bearer auth to a2a",
  "cut over a new a2a service", "fast-agent card loader", "fast-agent
  coordinator/implementer pattern", or any mention of
  /Users/dev/.fast-agent/agent-cards/ alongside the a2A service.
license: MIT
metadata:
  hermes:
    tags: [fast-agent, a2a, agent-cards, cloudflare, bearer-auth, launchd, streaming]
  related-skills: [cloudflare, cloudflare-one, whiteboarding]
---

# fast-agent A2A Setup

Set up a fast-agent A2A server with the canonical two-card coordinator/implementer pattern, a localhost bearer-auth gateway, a Cloudflare tunnel, and a launchd-managed cutover discipline.

## When to use this

- **Provisioning** a fresh `fast-agent` A2A server (public hostname + bearer auth + agent cards).
- **Renaming** or **replacing** agent cards (cards load at server-startup — restart upstream after editing).
- **Adding a new agent** to an existing A2A server (coordinator or worker).
- **Cutover or rollback** of the launchd-managed A2A service.
- **Audit** of an existing A2A setup against this contract.

Do **not** use this for non-A2A fast-agent workflows (CLI agents, MCP-only servers, batch eval). Use `agents-sdk` for those patterns.

## Architecture (the only one that scales)

```
Internet → Cloudflare Tunnel (origin: 127.0.0.1:8000)
              ↓
              localhost bearer gateway on :8000  ←─── auth + card rewrite
              ↓ (only when Authorization: Bearer <key> matches)
              fast-agent A2A server on :8001  ←─── loopback-only, no auth
              ↓
              AgentCards (tool-cards + agent-cards) → agents → models
```

- **Discovery public.** `GET /.well-known/agent-card.json` requires no auth and advertises `securitySchemes.bearerAuth` so callers know to send one.
- **All action routes protected.** `POST /a2a`, `POST /a2a/*`, and every other method on `/a2a*` require `Authorization: Bearer <shared-key>`. `401` with `WWW-Authenticate: Bearer realm="fast-agent-a2a"` otherwise.
- **One shared key.** 256-bit hex (64 chars), file mode `0600`. Same key authorizes every agent.
- **Upstream is loopback-only.** Never expose `127.0.0.1:8001` to the network or LAN; the gateway is the only ingress.

## Agent-card contract (frontmatter)

Required fields and their semantics:

| Field | Required | Meaning |
|---|---|---|
| `type: agent` | ✅ | Currently only `agent` is supported for A2A. |
| `name` | ✅ | PascalCase. **Public skill ID.** Renaming is breaking for any caller using `metadata.agent: <oldname>`. |
| `description` | ✅ | Plain-English one-liner. Shown in public card. State role + key constraints + timeout. |
| `default: true` | one only | The default agent for requests that omit `metadata.agent`. **Pick the coordinator**, not the executor. |
| `shell: true` | optional | Enables host shell. **Give only to the executor**, never the coordinator. |
| `subagents: true` | optional | Lets the agent spawn child sessions (slashes-cost model). |
| `harness_tools: true` | optional | Exposes `/commands` and the subagent tool. |
| `agents: [ChildName]` | optional | Declares Agent-as-Tool children. Load order is computed from these. |
| `model: $system.default` | recommended | Inherits from `~/.fast-agent/fast-agent.yaml`. |
| `request_params.streaming_timeout` | ✅ | Model stream-idle timeout in seconds. See [Streaming](#streaming-and-the-cloudflare-125s-caveat). |

### The two-card pattern (mandatory)

Every A2A service runs **at least two cards**: one coordinator (no shell) and one implementer (shell). Tool-cards attach to whichever agent the runtime resolves to.

| | **Coordinator** (default) | **Implementer** (child) |
|---|---|---|
| `default` | ✅ true | ❌ false |
| `shell` | ❌ **never** | ✅ true |
| `harness_tools` | ✅ | ✅ |
| `subagents` | ✅ | ✅ |
| `agents:` | `[Implementer]` | `[ToolCard]` |
| `streaming_timeout` | longest (e.g. 3600) | shorter (e.g. 1800) |
| Purpose | Plans, routes, reviews, delegates | Executes shell, edits files, runs harnesses |

**Why coordinator has no shell (defense in depth):** instruction-layer rules ("delegate, don't act") are best-effort. Omitting `shell: true` enforces the rule at the tool layer — even a polyglot LLM reasoning past the instruction physically cannot run `bash`. Combined with single-point-of-execution attribution, one auditor can always answer "which agent did this?".

Reference cards live at `references/agent-card-coordinator.md` and `references/agent-card-implementer.md`.

## Tool-only cards (`tool_only: true`)

A card with `tool_only: true` (e.g. `ripgrep_spark`) is loaded from `~/.fast-agent/tool-cards/`, not `agent-cards/`. Two attachment rules:

1. **Auto-attached** to the active request's target agent, falling back to the **default agent**.
2. To force a tool-card onto a non-default agent, declare it in that agent's `agents:` list. The loader records it as `child_agents`; the runtime honors it.

Consequence: if you rename the default agent, every auto-attached tool follows. Always re-verify which agent actually owns each tool-card after a rename.

## Bearer-auth gateway

The gateway is a 200-line Starlette ASGI app that lives in front of `fast-agent serve a2a`. Reference implementation: `references/a2a_bearer_gateway.py`.

Behavior contract (must match — clients depend on it):

| | |
|---|---|
| Public | `GET /.well-known/agent-card.json` |
| Protected | `POST /a2a`, every method on `/a2a/*` |
| Credential | `Authorization: Bearer <shared-key>` |
| Failure | `401 {"error":"unauthorized"}` + `WWW-Authenticate: Bearer realm="fast-agent-a2a"` |
| Upstream down | `502 {"error":"upstream_unavailable"}` |
| Invalid upstream card | `502 {"error":"invalid_agent_card"}` |
| Forwarding | strips `Authorization`, `Host`, hop-by-hop headers; duplicates `Date`/`Server` are dropped |
| Streaming | `timeout=None` on upstream `httpx.AsyncClient`; `StreamingResponse(aiter_raw())`; no buffering |
| Card rewriting | rewrites `supportedInterfaces[].url` from upstream loopback to public URL; adds `securitySchemes.bearerAuth` and per-skill `securityRequirements` |
| Key file | mode `0600`, length ≥ 32 chars; group/other readable ⇒ refuses startup |

Four-test simulator suite at `references/test_a2a_bearer_gateway.py` exercises all of the above using `httpx.ASGITransport` against an in-process Starlette upstream. No mocks.

## Streaming and the Cloudflare 125s caveat

`request_params.streaming_timeout` is a **model stream-idle** limit, not a total wall-clock guarantee. Cloudflare's proxied non-streaming origin read timeout defaults to 125 seconds. A 22-minute silent HTTP response can still be terminated at the edge.

For long-duration calls (anything approaching the 125 s threshold):

- **Must** use A2A streaming (`/a2a/rest/message:stream` or JSON-RPC streaming). Streaming activity keeps the connection active at the edge.
- **Do not** use non-streaming `message:send` as proof of >125 s support — it will hit the edge timeout regardless of the model's stream-idle setting.

If a true silent request must run >125 s, the follow-up architecture is async-task submission + polling, or an Enterprise Cloudflare timeout increase. Both are outside this skill.

## File layout

```
~/.fast-agent/
├── fast-agent.yaml                    # default model, MCP servers, plugins
├── agent-cards/
│   ├── <Coordinator>.md               # default: true, no shell
│   └── <Implementer>.md               # shell: true, child of Coordinator
├── tool-cards/
│   └── <ToolCard>.md                  # tool_only: true
├── secrets/
│   └── a2a-bearer-key                 # 0600, 64 hex chars
├── a2a_bearer_gateway.py              # auth gateway (no fast-agent patches)
└── tests/
    └── test_a2a_bearer_gateway.py     # 4 simulator tests

~/Library/LaunchAgents/
├── com.goodshepherd.fast-agent-a2a.plist            # upstream on 127.0.0.1:8001
└── com.goodshepherd.fast-agent-a2a-gateway.plist    # gateway on 127.0.0.1:8000

~/.cloudflared/
└── fast-agent-a2a.yml                 # ingress → http://127.0.0.1:8000
```

## Cutover discipline (mandatory)

Never edit live state without going through this loop:

1. **Backup** every mutable existing file. Snapshot dir under `~/.fast-agent/backups/<label>-<stamp>/`. Record the latest in `~/.fast-agent/backups/<label>-latest`.
2. **Generate or preserve** the bearer key. `openssl rand -hex 32 > a2a-bearer-key; chmod 600 a2a-bearer-key`. Guard with `if [ ! -s ... ]` so reruns don't rotate clients.
3. **Validate before touching launchd:**
   ```bash
   /Users/dev/.local/share/uv/tools/fast-agent-mcp/bin/python -m py_compile \
       ~/.fast-agent/a2a_bearer_gateway.py \
       ~/.fast-agent/tests/test_a2a_bearer_gateway.py
   /Users/dev/.local/share/uv/tools/fast-agent-mcp/bin/python -m unittest -v \
       ~/.fast-agent/tests/test_a2a_bearer_gateway
   /Users/dev/.local/share/uv/tools/fast-agent-mcp/bin/python - <<'PY'
   from pathlib import Path
   from fast_agent.core.agent_card_loader import load_agent_cards
   from fast_agent.core.validation import get_dependencies_groups
   cards = load_agent_cards(Path.home() / '.fast-agent/agent-cards')
   for c in cards:
       print(c.name, c.agent_data['config'].default_request_params.streaming_timeout)
   print(get_dependencies_groups({c.name: c.agent_data for c in cards}))
   PY
   plutil -lint ~/Library/LaunchAgents/com.goodshepherd.fast-agent-a2a*.plist
   ```
4. **Cut over** upstream first, then gateway. Never start the gateway before the upstream is healthy:
   ```bash
   uid=$(id -u)
   launchctl bootout "gui/$uid/com.goodshepherd.fast-agent-a2a" 2>/dev/null || true
   launchctl bootstrap "gui/$uid" ~/Library/LaunchAgents/com.goodshepherd.fast-agent-a2a.plist
   for _ in {1..40}; do curl -fsS --max-time 1 http://127.0.0.1:8001/.well-known/agent-card.json >/dev/null && break; sleep 0.25; done
   launchctl bootstrap "gui/$uid" ~/Library/LaunchAgents/com.goodshepherd.fast-agent-a2a-gateway.plist
   for _ in {1..40}; do curl -fsS --max-time 1 http://127.0.0.1:8000/.well-known/agent-card.json >/dev/null && break; sleep 0.25; done
   ```
5. **Verify** listeners (`lsof -nP -iTCP:8000,8001 -sTCP:LISTEN`), public discovery, and auth (`401` on missing/wrong key, `200` on valid key reaching upstream protocol validation). Then repeat against the public Cloudflare hostname.
6. **Inspect service health:** `launchctl print`, tail `~/Library/Logs/fast-agent-a2a*.log`. No `Traceback`, no bind conflict, no upstream `RequestError` in the gateway error log.

A reference cutover script is `references/cutover.sh`. Run it only after steps 1–3 pass.

## Rollback

```bash
uid=$(id -u)
backup_dir=$(cat ~/.fast-agent/backups/<label>-latest)
launchctl bootout "gui/$uid/com.goodshepherd.fast-agent-a2a-gateway" 2>/dev/null || true
launchctl bootout "gui/$uid/com.goodshepherd.fast-agent-a2a" 2>/dev/null || true
cp "$backup_dir"/* /Users/dev/.fast-agent/agent-cards/ ~/Library/LaunchAgents/ 2>/dev/null
rm -f ~/.fast-agent/a2a_bearer_gateway.py
rm -f ~/.fast-agent/tests/test_a2a_bearer_gateway.py
rm -f ~/Library/LaunchAgents/com.goodshepherd.fast-agent-a2a-gateway.plist
launchctl bootstrap "gui/$uid" ~/Library/LaunchAgents/com.goodshepherd.fast-agent-a2a.plist
```

The bearer key is intentionally retained. Delete it separately only after confirming no future reuse is needed. A reference script is `references/rollback.sh`.

## Common pitfalls

- **Cards load at server startup.** Editing an agent card without restarting upstream silently serves the old card. Always `launchctl bootout` + `bootstrap` after a card edit.
- **Renames are breaking.** A caller using `metadata.agent: dev` will silently fall through to the new default if you rename `dev → Cody`. Add a `validation_reject_unknown_agents: true` flag if you want hard rejection — but that flag does not exist today; check the loader's allowed fields before assuming.
- **Bearer key leak vectors.** It must not appear in any plist, `ps` listing, agent card, test fixture, or gateway error log. Audit with:
  ```bash
  key=$(tr -d '\n' < ~/.fast-agent/secrets/a2a-bearer-key)
  grep -rIn "$key" ~/Library/LaunchAgents/ ~/.fast-agent/agent-cards/ ~/.fast-agent/tests/ 2>/dev/null
  ```
- **`tool_only` cards drift with the default.** Renaming the default agent re-targets every auto-attached tool-card. Re-verify each tool's owning agent after a rename.
- **`shell: true` on the coordinator breaks the defense-in-depth model.** If you need shell on a coordinator for one-off reasons, fork a separate agent — do not weaken the pattern.
- **Cloudflare 125 s non-streaming timeout.** Don't promise long-running non-streaming calls. The gateway can stream; the edge won't honor non-streaming >125 s.

## What "correctly" looks like (acceptance)

The setup is correct when, in one shell session, all of the following return without manual intervention:

```bash
# 1. Discovery advertises both names + bearer security
curl -fsS https://<host>/.well-known/agent-card.json | \
    jq '{name, skills: [.skills[].name], sec: .securitySchemes.bearerAuth.httpAuthSecurityScheme.scheme}'

# 2. Missing and invalid keys are rejected
[ "$(curl -sS -o /dev/null -w '%{http_code}' -X POST https://<host>/a2a/jsonrpc)" = 401 ]
[ "$(curl -sS -o /dev/null -w '%{http_code}' -X POST -H 'Authorization: Bearer wrong' https://<host>/a2a/jsonrpc)" = 401 ]

# 3. Valid key reaches upstream protocol validation
A2A_KEY=$(tr -d '\n' < ~/.fast-agent/secrets/a2a-bearer-key)
status=$(curl -sS -o /dev/null -w '%{http_code}' \
    -X POST -H "Authorization: Bearer $A2A_KEY" -H 'Content-Type: application/json' --data '{}' \
    https://<host>/a2a/jsonrpc)
unset A2A_KEY
[ "$status" != 401 ] && [ "$status" != 502 ]   # PASS — non-401/non-502

# 4. Stream response is chunked end-to-end
curl -fsS -i -X POST -H "Authorization: Bearer $A2A_KEY" https://<host>/a2a/rest/message:stream \
    | grep -i '^transfer-encoding: chunked'      # PASS
```

## References

| File | Purpose |
|---|---|
| `references/a2a_bearer_gateway.py` | Gateway source — copy verbatim, edit nothing |
| `references/test_a2a_bearer_gateway.py` | 4 simulator tests, must pass before any cutover |
| `references/agent-card-coordinator.md` | Default coordinator template (no shell) |
| `references/agent-card-implementer.md` | Implementer child template (shell, harness_tools, subagents) |
| `references/plist-upstream.xml` | `com.goodshepherd.fast-agent-a2a.plist` (binds 127.0.0.1:8001) |
| `references/plist-gateway.xml` | `com.goodshepherd.fast-agent-a2a-gateway.plist` (binds 127.0.0.1:8000) |
| `references/cutover.sh` | Idempotent cutover script |
| `references/rollback.sh` | Idempotent rollback script (uses `<label>-latest` backup pointer) |