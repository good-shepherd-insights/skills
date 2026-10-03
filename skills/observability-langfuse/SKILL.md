---
name: observability-langfuse
description: Use when Langfuse tracing is silent in Hermes - no traces land despite an enabled plugin, or when setting up trace capture for the first time. Covers the SDK-missing failure mode, the PM-extra fix, and how to prove traces are arriving.
version: 1.0.0
---

# Langfuse Observability for Hermes

Traces every conversation, LLM call, and tool usage to Langfuse. The plugin ships
bundled but is opt-in, and it **fails open** - when its SDK or credentials are
missing the hooks no-op silently, so "no traces" is almost always a dependency
problem rather than a config problem.

## Enable

```bash
hermes tools          # interactive: Langfuse Observability
```

That path collects credentials, provisions the `langfuse` extra into the
selected environment, and enables the plugin. Restart Hermes afterwards.

Non-interactive equivalent (same code path as the interactive UI, useful in
scripts and on headless boxes):

```bash
hermes tools post-setup langfuse
```

Do NOT install the SDK with pip into the environment Hermes runs from. Hermes
resolves dependencies through its package manager; a hand-installed package is
invisible to it and to the next environment sync.

## Credentials

Set in `~/.hermes/.env` (the interactive tool writes these for you):

```bash
HERMES_LANGFUSE_PUBLIC_KEY=pk-lf-...
HERMES_LANGFUSE_SECRET_KEY=sk-lf-...
HERMES_LANGFUSE_BASE_URL=https://cloud.langfuse.com   # or a self-hosted URL
```

Keep these in the environment or a secret store. They are write credentials for
your Langfuse project - never commit them, and never paste them into a repo
skill file.

## Silent tracing: the failure signature

The plugin logs one warning per gateway start and then goes quiet:

```
Langfuse plugin is enabled but the langfuse SDK is unavailable; tracing is disabled.
```

MCP calls to Langfuse still succeed in that state, because they authenticate
over HTTP. The exporter has a separate dependency: the `langfuse` Python
package inside the interpreter Hermes actually runs. A green `getHealth` with
zero new traces points at the SDK, not at credentials.

Confirm which case you have before changing anything:

```bash
hermes plugins list | grep langfuse          # should show "enabled"
```

- **shows enabled, no traces** -> SDK missing, continue below.
- **shows disabled** -> never enabled; run `hermes tools post-setup langfuse`.

## Fix

```bash
hermes tools post-setup langfuse   # provisions the extra into the committed env
hermes gateway restart
```

The restart matters: the exporter binds at process start, so a provisioned SDK
without one traces nothing. The extra is declared in Hermes' own dependency
set, which is why the package manager provisions it where pip does not.

## Verify with evidence

A restart is not proof. Fire a real turn, then read the trace back:

```bash
hermes chat -q "ping" --oneshot --max-turns 1
```

`--oneshot --max-turns 1` answers and exits without an interactive session.

Then confirm in Langfuse (a trace named `Hermes turn`, a minute old), or
query the API directly:

```bash
bu=$(grep '^HERMES_LANGFUSE_BASE_URL=' ~/.hermes/.env | cut -d= -f2 | tr -d '"')
pk=$(grep '^HERMES_LANGFUSE_PUBLIC_KEY=' ~/.hermes/.env | cut -d= -f2 | tr -d '"')
sk=$(grep '^HERMES_LANGFUSE_SECRET_KEY=' ~/.hermes/.env | cut -d= -f2 | tr -d '"')
curl -s -u "$pk:$sk" "$bu/api/public/traces?limit=5"
```

Read all three from `.env` rather than defaulting the host: Langfuse is
region-scoped, and credentials from a `us.cloud.langfuse.com` project return
401 against the global `cloud.langfuse.com` host. The `tr -d '"'` is needed
because `.env` values are often quote-wrapped, and literal quotes in the
Authorization header also produce 401.

What a healthy trace carries, confirmed on live runs:

| Field | Example value |
|---|---|
| `name` | `Hermes turn` |
| `tags` | `["hermes", "langfuse"]` |
| `metadata.platform` | `cli`, `a2a`, `webhook` - the originating platform |
| `metadata.capture_mode` | `sanitized` |
| `metadata.model` / `metadata.provider` | e.g. `glm-5.3-flash` / `ollama-cloud` |

`metadata.platform` records which ingress a turn arrived through. To confirm a
channel, send a turn through it and read that field back.

## Optional tuning

```bash
HERMES_LANGFUSE_ENV=production       # environment tag
HERMES_LANGFUSE_RELEASE=v1.0.0       # release tag
HERMES_LANGFUSE_SAMPLE_RATE=0.5      # sample a fraction of traces
HERMES_LANGFUSE_MAX_CHARS=12000      # per-field truncation (default 12000)
HERMES_LANGFUSE_MAX_DEPTH=4          # nested payload depth (default 4)
HERMES_LANGFUSE_CAPTURE=sanitized    # metadata | sanitized | full
HERMES_LANGFUSE_DEBUG=true           # verbose plugin logging
```

### Capture modes

Selected with `HERMES_LANGFUSE_CAPTURE`. Every mode captures structural data -
IDs, roles, tool names, token usage, cost, timing. They differ in how much
conversation *content* leaves the box.

| mode | behavior |
|---|---|
| `metadata` | No content. Fields become shape stubs (`{"omitted": true, "type": "text", "chars": N}`). |
| `sanitized` | Default. Content exported after secret-pattern redaction (API keys, tokens, JWTs, private keys, `password=`-style assignments) and truncation. Redaction runs before truncation. |
| `full` | Raw content, truncated only. Traces contain whatever passed through the conversation. Explicit opt-in. |

The active mode is recorded on every trace as `metadata.capture_mode`.

`sanitized` is pattern-based defense in depth, not a DLP guarantee. On a shared
Langfuse project prefer `metadata`.

## Coverage

- Failed model requests close their generation with `level=ERROR`, status code,
  retry counters, and a scrubbed message.
- Session end and finalize close still-open traces and flush queued events, so
  interrupted or tool-only turns do not dangle.

## Disable

```bash
hermes plugins disable observability/langfuse
```