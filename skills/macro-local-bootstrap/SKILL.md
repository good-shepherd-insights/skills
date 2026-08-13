---
name: macro-local-bootstrap
description: Bootstraps macro-inc/macro's full local dev stack (Rust backend services + SolidJS frontend + Postgres/Redis/Kafka/OpenSearch/FusionAuth via Docker) from a completely fresh clone on macOS, with zero dependencies pre-installed and no macro-inc Doppler org access. Encodes every real failure mode hit during a live bootstrap session — missing Nix cross-compile toolchain, undersized Docker VM causing OpenSearch OOM-kills, ~60 required-but-undocumented placeholder secrets across a dozen Rust services, a wasm-cache warmup trap that silently blows past the frontend's 36-second startup timeout, and more. Use this whenever the user asks to clone/run/test macro-inc/macro locally, "get Macro running", set up the macro dev environment, or debug a partially-working local Macro stack (containers crash-looping, frontend not loading, `just run_local` or `just stack up` failing) — even if they don't mention this skill by name. Always check host RAM/CPU dynamically before sizing the Docker VM; never assume the machine is under- or over-resourced.
---

# Macro local bootstrap

Gets `macro-inc/macro` running locally end to end: clone → toolchain → Docker
VM → placeholder secrets → full stack → verified working frontend + backend.
Every step below exists because it broke a specific way during a real,
several-hour live troubleshooting session — the "why" is included so you can
adapt if something's shifted since (repo updates, a different host, an
actual Doppler grant).

**Follow the steps in order.** Don't skip ahead to `just run_local` — the
ordering traps in steps 5-8 are what turn a 10-minute bootstrap into a
multi-hour one.

## Which secrets actually matter — read this before touching `local.env`

Step 7 bundles a placeholder value for ~60 required env vars so every
service *boots*. But "boots" and "is actually usable" are different bars —
know which gap you're accepting before you start:

- **Bootstrapping for local dev/testing only?** All ~60 placeholders are
  fine as-is. Don't go source real credentials for anything. To get a
  logged-in session without real Google OAuth, use
  `just seed-scenario apply --file seed/scenarios/<name>.json` after the
  stack is up — it seeds fake users/teams/data and prints direct login
  links, no OAuth round-trip needed. `just seed-scenario status` re-prints
  those links anytime.
- **Standing this up for someone to actually use day to day?** Two of the
  ~60 are not placeholder-safe — everything else genuinely is:
  - **`GOOGLE_CLIENT_ID` + `GOOGLE_CLIENT_SECRET_KEY`** — sign-up is Google
    OAuth *only* (no password auth exists), and email sync — the product's
    headline feature — rides the same OAuth grant via the Gmail API. Without
    a real Google Cloud OAuth app, no real person can sign in and no real
    mail ever syncs; the rest of the product has nothing to hang off of.
    Getting one requires a Google Cloud project + OAuth consent screen +
    redirect URI set to `http://localhost:8090/auth/callback` (already
    correct in the template), federated through the local FusionAuth
    instance — real setup work, not just dropping in a key.
  - **`ANTHROPIC_API_KEY`** — Agents, unified memory, and agentic editing are
    core product pillars per the README, not bolt-ons. Without a real key
    that whole surface is dead.
  - Everything else in the template — GitHub App sync, Slack MCP, Stripe,
    LiveKit calls, Apollo/OpenAI/Cohere enrichment — gates a specific
    integration, not core usability. Leave those as placeholders unless the
    user specifically asks for that feature to work.

If the user's goal is "actually use this," flag the Google OAuth setup
explicitly before declaring the bootstrap done — a fully green `docker ps`
with placeholder Google creds is a working *shell*, not a working product.

## 0. Before you start

Confirm with the user before installing Nix system-wide (creates `/nix`,
needs sudo) or resizing/restarting colima if one is already running with
containers on it (stops those containers). Everything else here — cloning,
`bun install`, writing `local.env`, starting a fresh colima — is safe to do
without asking.

**Check disk space before anything else** — a full disk fails mid-build with
a confusing "no space left on device" rather than a clean preflight error,
and this stack's footprint is bigger than it looks at a glance:

```bash
df -g . | awk 'NR==2 {print $4"GB free"}'
```

Real measured footprint from a full bring-up: ~14GB Rust `target/`, ~2GB
`.git`, ~1.5GB `node_modules`, ~1.5GB cargo registry, ~2GB nix store, plus
colima's own disk usage (17 Docker images ~22GB, build cache up to ~14GB
before reclaim, volumes ~3GB) — **~50GB total observed**. Budget 60GB+ free.
`scripts/compute_colima_resources.sh` (step 3) also checks this and warns on
stderr, but check it here too before spending time on steps 1-2 if it's
already tight.

## 1. Clone and preflight tool check

```bash
git clone https://github.com/macro-inc/macro.git
cd macro   # note this path — you will `cd` here explicitly in every later step, see step 4
```

Check what's already present — never assume:

```bash
which git docker colima nix bun cargo rustc zig sqlx just doppler
```

You need: `git`, a Docker daemon (colima preferred if nothing else is
running one), and `nix`. You do **not** need `bun`/`cargo`/`rustc`/`zig`/
`sqlx`/`just` on the host individually — `nix develop` provides all of them
from the repo's own `flake.nix`, and critically also provides the
**cross-compile sysroot** (curl/openssl/zlib headers for the
`aarch64-unknown-linux-gnu` target) that a manually-assembled host toolchain
does not have. Don't try to hand-install `cargo-zigbuild` + Zig + sqlx-cli
yourself and skip Nix — we tried that first and it fails opaquely deep into
a 10-minute build:

```
error: failed to run custom build command for `rdkafka-sys`
fatal error: 'curl/curl.h' file not found
```

That's macOS's system curl not covering the Linux cross target. `nix develop`
fixes it immediately because its shell bundles a matching cross sysroot.
**Always route Rust builds through `nix develop --command ...`, never bare
`cargo`/`just` on the host**, even after you've confirmed `cargo`/`rustc`
exist locally — an existing host Rust install still lacks the cross sysroot.

## 2. Install Nix if missing

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix -o /tmp/install-nix.sh
```

Read `/tmp/install-nix.sh` before running it (it's short, confirms it's the
real Determinate Systems installer). Then:

```bash
sh /tmp/install-nix.sh install --no-confirm
```

This needs `sudo` and an interactive password prompt — **it cannot be run
fully non-interactively**. If it fails with `sudo: a terminal is required to
read the password`, that's expected in an agent-driven shell: tell the user
to run the exact command themselves in their own terminal (or via Claude
Code's `!` prefix), then poll for completion rather than retrying it
yourself:

```bash
until [ -e /nix/var/nix/profiles/default/bin/nix ]; do sleep 5; done
```

**After install, the current shell session will NOT have `nix` on `PATH`** —
the shell snapshot predates the install. Every subsequent command in this
skill must start with:

```bash
source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
```

Don't assume this sourcing persists across separate tool calls if you're
running as an agent with per-command shell state — re-source it each time,
or fold it into a single `&&`-chained command per step.

## 3. Docker VM: size it off the real host, every time

Never hardcode a memory/CPU number. Run the bundled sizing script, which
reads `sysctl -n hw.memsize`/`hw.ncpu` and computes an allocation that leaves
the host OS headroom (the larger of 2GB or 25% of total RAM, at least 2
CPUs), with a 4GB floor for the VM itself since this stack (Postgres + Redis
+ Kafka + OpenSearch + LocalStack + ~15 Rust service containers) needs real
headroom — we watched OpenSearch get OOM-killed (exit 137) at colima's 2GB
default:

```bash
read -r vm_mem_gb vm_cpu < <(bash scripts/compute_colima_resources.sh)
```

(Run this from the skill directory, or reference it by its full path — it's
bundled at `scripts/compute_colima_resources.sh` alongside this file.)

If no Docker daemon is running:

```bash
colima start --memory "$vm_mem_gb" --cpu "$vm_cpu"
```

If colima is **already running**, check its current allocation with
`colima list`. If it's meaningfully under the freshly-computed numbers (e.g.
still at colima's 2GB default), confirm with the user, then:

```bash
colima stop && colima start --memory "$vm_mem_gb" --cpu "$vm_cpu"
```

**Always export `DOCKER_HOST` explicitly afterward, for every command that
touches Docker for the rest of this bootstrap:**

```bash
export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock
```

Without this, the repo's own Rust tooling (`bollard`'s
`connect_with_local_defaults()`) fails with `Socket not found:
/var/run/docker.sock` even though the `docker` CLI itself works fine via
`docker context` — bollard doesn't auto-discover colima's non-standard
socket path, it only reads `DOCKER_HOST`.

## 4. Working-directory discipline

`cd` into the repo root **explicitly, in every command from here on** —
don't rely on a persisted shell working directory across separate tool
invocations. We lost real time to exactly this: a `cd` into an unrelated
scratch directory for one step silently reset the working directory for
every later command, and `nix develop` failed with `could not find a
flake.nix file` because it ran from the wrong place. If you're chaining
commands with `&&` in one shell call, the risk is low; if you're an agent
issuing separate tool calls, prefix every one with `cd /path/to/macro &&`.

## 5. Preflight sanity check

```bash
cd macro && source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' && export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock && nix develop --command just doctor-local
```

This checks docker/zig/bun/sqlx-cli/ports/toolchain versions all before
attempting the real thing. Fix anything it flags before moving on — don't
proceed past a failed doctor-local hoping it'll sort itself out downstream.

## 6. Install frontend deps + warm the wasm cache

Two separate traps live here, both worth doing proactively rather than
discovering live:

```bash
cd macro && source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' && nix develop --command bun install
```

Then **warm the WASM build cache** with a throwaway frontend start. The
frontend's `bun run --bun dev` triggers a one-time `just ensure-cache-wasm`
step (compiles a Rust crate to WASM via `wasm-bindgen`, downloading and
installing `wasm-bindgen-cli` on first run) that alone can take well over a
minute. The stack orchestrator's own frontend-readiness poll only waits 36
seconds (120 × 300ms) before giving up with a generic, unhelpful `frontend
dev server did not become ready` — it doesn't show the real cause because
the process hadn't exited, just hadn't bound the port yet. `bun install`
alone does not pre-warm this cache. Run once, let it finish, then kill it:

```bash
cd macro/apps/web && source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' && nix develop /path/to/macro --command bun run --bun dev > /tmp/frontend_warmup.log 2>&1 &
```

Poll the log for `VITE v... ready in ... ms` (can take a few minutes on
first run — it's compiling the wasm crate + installing wasm-bindgen-cli),
then:

```bash
pkill -f "vite -c vite.config.ts"
lsof -ti tcp:3000 | xargs -r kill -9
```

Skipping this step doesn't break anything permanently — it just means your
*first* real stack-up attempt in step 8 will fail on the frontend step with
the unhelpful timeout message above, and you'll need to retry once the cache
is warm anyway. Doing it here just avoids that wasted round-trip.

## 7. Write `local.env` with the full placeholder secret set

The repo's `local` Doppler project holds ~60 required secrets across a dozen
Rust services. Without macro-inc org access, `doppler login` will succeed
(if attempted) but `doppler projects` won't show `local` — that's expected,
not a bug. The repo's own env-resolution code
(`tooling/xtask/crates/xtask_local/src/local/env_layer.rs`, function
`pull_doppler`) already treats a failed/inaccessible Doppler pull as
non-fatal in local mode and proceeds without those secrets — so don't block
on Doppler access, just skip straight to the placeholder file.

Copy the bundled template (`assets/local.env.template`, next to this file)
into the repo root as `local.env`, then fill in the three runtime-only
values it can't ship with statically:

```bash
cp /path/to/this/skill/assets/local.env.template macro/local.env
```

**JWT keypair** (parsed as real PEM by `jsonwebtoken`'s RS256 decode/encode
in `crates/macro_auth/src/middleware/decode_jwt.rs` — a placeholder string
boots the service but panics the first time a token is actually signed or
verified):

```bash
bash /path/to/this/skill/scripts/generate_jwt_keypair.sh
```

Replace the `MACRO_API_TOKEN_PRIVATE_SECRET_KEY=__RUNTIME_JWT_PRIVATE_KEY__`
and `MACRO_API_TOKEN_PUBLIC_KEY=__RUNTIME_JWT_PUBLIC_KEY__` lines in
`local.env` with this script's two output lines.

**Database URL** — this one needs a first stack attempt to exist (see step
8), because the real Postgres user/password are code-generated per checkout
by the repo's own `LocalEnv`, not something you can predict up front. On the
*first* `just stack up` attempt, expect it to fail on DB-dependent services
with the literal placeholder `__RUNTIME_DATABASE_URL__` — that's fine, it's
the signal to do this:

```bash
real_db_url=$(grep '^DATABASE_URL=' infra/local/generated/*/local.generated.env | head -1 | cut -d= -f2-)
sed -i '' "s|__RUNTIME_DATABASE_URL__|${real_db_url}|g" local.env
```

Don't hardcode `postgres://postgres:postgres@postgres:5432/postgres` or
similar — we tried a guessed value and every DB-touching service failed with
`password authentication failed for user "postgres"`. The real generated
value looks like `postgres://user:password@postgres:5432/macrodb` — always
read it back from the generated file, never guess it.

Three of the placeholder values are validated at config-load time, not just
presence-checked — if you ever need to touch these, keep the exact format:
- `REDIS_HOST` must be a full `redis://host:port` URL despite its name —
  `connection_gateway` and `document_cognition_service` pass it straight
  into a Redis client URL parser, which rejects a bare hostname like `redis`
  with `InvalidClientConfig`. This is a different variable from `REDIS_URI`
  (which most other services use and which the repo's `LocalEnv` already
  sets correctly) — don't conflate them.
- `CAL_EVENT_TYPE_CONTENT_NAMES_KEY` is parsed as JSON — must stay `{}`, not
  an arbitrary string.
- `MCP_CREDENTIALS_KEY_SECRET_NAME` is base64-decoded at load — must stay
  valid base64.

## 8. Bring up the stack

**Use `just run_local` — this is the path actually proven end to end in the
session this skill is built from.** The repo also documents a headless
`just stack up` mode (static frontend bundle, no attached process) that
looks like a better fit for unattended/agent-driven bootstrap on paper, but
it was never actually exercised — everything below was verified live. If
you try `stack up` instead, don't assume the verification URLs in step 9
carry over unchanged; confirm the real ones with `just stack status --json`
first, and expect to work out any wrinkles the docs don't mention (we hit
several with `run_local` that its own docs didn't call out either).

```bash
cd macro && source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh' && export DOCKER_HOST=unix://$HOME/.colima/default/docker.sock && lsof -ti tcp:3000 | xargs -r kill -9 && nix develop --command just run_local --env-file ./local.env
```

The `lsof`/`kill` before every attempt matters — a leftover process on port
3000 from a previous failed attempt is the single most common re-run
failure (`frontend port 3000 is already in use`), and it produces a
misleading error that has nothing to do with whatever you actually changed.

**`run_local` is an attached process** with a hotkey loop (`r`/`q`) that
spawns the frontend dev server as its own direct child. If whatever ran the
command above is itself running as a background task that later gets
reaped (a coding agent's task manager killing a long-lived background
process, a closed terminal), the frontend dies with it while backend
containers silently keep running underneath — you'll see the backend health
check still pass but `localhost:3000` refuse connections. This happened live
in the session this skill is from. Recover by relaunching the frontend as a
fully detached process (not tied to whatever launched the stack), matching
the exact env vars the supervisor would have set:

```bash
cd macro/apps/web && source '/nix/var/nix/profiles/default/etc/profile.d/nix-daemon.sh'
export PORT=3000 VITE_LOCAL_SERVERS=ALL VITE_LOCAL_BACKEND_ORIGIN=http://localhost:8090 VITE_AI_EDITING_WORKER_URL=http://localhost:8090/ai-editing VITE_ENABLE_BROWSER_OTEL=false
nohup nix develop /path/to/macro --command bun run --bun dev > /tmp/frontend_persistent.log 2>&1 < /dev/null &
disown
```

`disown` matters — without it the process is still tied to the shell that
launched it and can die the same way. `VITE_LOCAL_BACKEND_ORIGIN` and the
port must match `docker/docker-compose.yml`'s proxy port (8090 by default)
and `instance.port(Port::Frontend)` (3000 by default) — if the instance is
named or the ports were overridden, pull the real values from `just
status_local` rather than assuming these defaults.

**If it fails with `missing required value: X` / `envvar not found: X`**
from a Rust service: the bundled template in step 7 already covers every
key discovered during the original live session, so this shouldn't happen
often. If it does (repo has moved on since), don't guess — read the failing
service's `services/<name>/src/config.rs`, find its `env_vars!` /
`maybe_env_vars!` macro blocks, and the struct fields *without* a
`#[macro_config_default(...)]` attribute are the required ones. Add the
missing key to `local.env` with a placeholder value, retry.

**Never hand-craft a manual `docker compose ... up -d <service>` command**
to "quickly" restart one crashed container — this repo's env injection into
containers goes through a `MACRO_ENV_FILE` indirection/mount (see the
docstring at the top of `tooling/xtask/crates/xtask_local/src/local/env_layer.rs`),
not the plain `env_file:` interpolation you'd expect from vanilla Docker
Compose. We tried this as a shortcut and it broke *more* containers than it
fixed — they came back up missing even basic vars like `ENVIRONMENT`.
Always go back through `just stack up` / `just stack update` / `just
run_local` for any env or container-recreation need.

## 9. Verify and report

These are the default-instance ports (`just run_local` with no `--instance`
flag) — if you named the instance or overrode ports, get the real ones from
`just status_local` first rather than assuming these:

```bash
curl -fsS -o /dev/null -w 'frontend: %{http_code}\n' http://localhost:3000/app
curl -fsS -o /dev/null -w 'backend:  %{http_code}\n' http://localhost:8090/auth/health
docker ps -a --format '{{.Names}}\t{{.Status}}' | grep -i exit || echo "no crashed containers"
```

Both curls should return `200`. If a handful of containers are still
`Exited`, check whether they're **`ai_editing_worker`** and/or
**`analytics_proxy`** — these two have a known, currently-unresolved
limitation unrelated to secrets: a cross-architecture native-binary
packaging issue baked into their Docker image (a `workerd`/`miniflare`
crash citing "unsupported platform" when Node tries to load the native
binary). No placeholder env value fixes this — recognize the signature and
report it as a known gap, don't iterate on it. Any *other* crashed container
is worth investigating per step 8's guidance.

Report to the user: frontend URL, whether both health checks passed,
container count, and which (if any) known-limitation containers are down.
