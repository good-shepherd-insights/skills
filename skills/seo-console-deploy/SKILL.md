---
name: seo-console-deploy
description: Run OpenSEO's full Cloudflare self-hosting setup end to end — gather inputs, create uniquely-named Cloudflare resources, wire wrangler.jsonc bindings correctly, deploy, configure Cloudflare Access via the API including MCP client access via Managed OAuth, and set up required integrations (DataForSEO, OpenRouter/SAM, Google Search Console, Site Audit/Workers Paid). Use when a user asks to self-host OpenSEO on Cloudflare, stand up a new Cloudflare deployment, or debug a partial/broken self-host setup.
metadata:
  internal: true
---

# Self-host OpenSEO on Cloudflare

Execute steps 0–7 in order. Composes `docs/SELF_HOSTING_CLOUDFLARE_MANUAL.md` and `docs/SELF_HOSTING_GOOGLE_SEARCH_CONSOLE.md` with corrections from a real debugged deployment those docs don't have yet — where this conflicts with a doc, this wins.

- Confirm with the user before: creating Cloudflare resources (1), creating the Access Application/API token (4). Never touch billing or plan upgrades (6) — assume Workers Paid is already active. Reading/checking state needs no confirmation.
- Nothing is hardcoded to one project — every name/email/toggle comes from step 0. Never default the slug to `open-seo` (the Deploy-to-Cloudflare button's own default, per `docs/SELF_HOSTING_CLOUDFLARE.md` — reusing it risks colliding with resources from that flow, same root cause as the binding collision in step 1).
- Resumable: before each creating step, check whether it's already done and skip ahead.

## 0. Inputs

1. **Company name** — becomes the project slug as `<company-name>-seo-console` (e.g. `acme-seo-console`). Builds every resource name below, and the Worker's own name in step 2.
2. **Access email or email-domain** — who can log in.
3. **Google Search Console** — required, always set up.
4. **SAM (OpenRouter-powered agent)** — required, always set up.
5. **Site Audit / crawling** — required, always set up. Gates step 6.
6. **MCP client access (Claude Code, Codex CLI)** — required, always set up. Gates Managed OAuth in step 4.

Check: `wrangler whoami` is authenticated (if not, stop, tell the user to `wrangler login`); repo cloned with `corepack enable && pnpm install` run.

## 1. Create Cloudflare resources

Confirm with the user first — real, billable resources. If resuming, check first (`wrangler kv namespace list`, `wrangler d1 list`, `wrangler r2 bucket list`) for `<slug>-kv`/`<slug>-oauth-kv`/`<slug>-d1`/`<slug>-r2` before creating duplicates.

Resource *names* only need to be unique in the account; the *binding* names wired into `wrangler.jsonc` are hardcoded in the app (`env.KV`/`env.OAUTH_KV`/`env.DB`/`env.R2` — see `src/db/d1/client.ts`, `src/server/lib/r2.ts`, `src/server/lib/dataforseo/serp-locations.ts`, `src/server/lib/audit/progress-kv.ts`). Bindings must stay exactly `KV`, `OAUTH_KV`, `DB`, `R2` — never the auto-derived name a `wrangler ... create` command suggests; a name without a type suffix is how two different resources previously suggested the same binding.

```bash
pnpm exec wrangler kv namespace create <slug>-kv
pnpm exec wrangler kv namespace create <slug>-oauth-kv
pnpm exec wrangler d1 create <slug>-d1
pnpm exec wrangler r2 bucket create <slug>-r2
```

Don't add `--update-config` to any of these — it auto-writes the auto-derived (colliding) binding name into `wrangler.jsonc`. Save each command's output: two KV ids, the D1 `database_id`, the R2 bucket name.

## 2. Wire wrangler.jsonc

Hand-edit — `wrangler deploy` has no `--update-config` flag (that's step 1's commands, avoided there, not applicable here):

- `name` (top-level) → `<slug>`. Determines the deployed hostname (`<slug>.<subdomain>.workers.dev`); every later `<worker-name>` placeholder means this value.
- `kv_namespaces`: binding `KV` → `<slug>-kv` id; binding `OAUTH_KV` → `<slug>-oauth-kv` id.
- `d1_databases`: binding `DB`, `database_name` → `<slug>-d1`, `database_id` → returned id. Keep `"migrations_dir": "drizzle"`.
- `r2_buckets`: binding `R2`, `bucket_name` → `<slug>-r2`.

Leave everything else (workflows, durable_objects, migrations tags, crons, observability) untouched. Ignore the comment in `wrangler.jsonc` claiming all deployments go through Alchemy and never read these ids — it's stale; `alchemy.run.ts`'s own comment confirms self-host still deploys via `wrangler.jsonc` directly.

The repo ships placeholder ids that look real but aren't. If this step is skipped or half-done, deploy 404s on the migration step with "database could not be found" — that's the signal to finish this step, not a deploy bug.

## 3. Deploy

```bash
pnpm run deploy
```

Check `package.json`'s `deploy` script before trusting the sequence blindly (as of writing: `npm run db:migrate:prod && npm run build && wrangler deploy`, where `db:migrate:prod` = `wrangler d1 migrations apply DB --remote`). Capture `<subdomain>` from the printed deployed URL — needed in step 4. Give the user the deployed URL (`https://<worker-name>.<subdomain>.workers.dev`) as soon as this step succeeds — don't wait until step 7 to surface it.

## 4. Cloudflare Access (Zero Trust)

Confirm with the user first — account-level, not trivially reversible.

**a. Zero Trust team name.** If no Zero Trust org exists yet, there's no "Enable Cloudflare Access" control in the Workers dashboard. Pick a team name in the Zero Trust dashboard onboarding. `TEAM_DOMAIN` = `https://<team-name>.cloudflareaccess.com`.

**b. Create the Access Application via the API**, not the dashboard toggle (that toggle was absent/unreliable in real testing even with a team name set up). If resuming, `GET /accounts/<account_id>/access/apps` first and check for a match before duplicating.

```bash
curl -X POST "https://api.cloudflare.com/client/v4/accounts/<account_id>/access/apps" \
  -H "Authorization: Bearer <api_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "<worker-name>.<subdomain>.workers.dev",
    "type": "self_hosted",
    "name": "<worker-name>",
    "policies": [{
      "precedence": 1,
      "decision": "allow",
      "include": [{ "email": { "email": "<the-input-email>" } }]
    }]
  }'
```

Email-domain input → use `{ "email_domain": { "domain": "<domain>" } }` instead of `email`.

Add to the same request body (MCP client access is always set up):

```json
"oauth_configuration": {
  "enabled": true,
  "dynamic_client_registration": {
    "enabled": true,
    "allow_any_on_localhost": true,
    "allow_any_on_loopback": true
  }
}
```

This is Access's **Managed OAuth** (`docs/SELF_HOSTING_CLOUDFLARE_OPERATIONS.md`, named for "Codex CLI, Claude Code"); `allow_any_on_localhost`/`allow_any_on_loopback` let a CLI's `http://localhost:PORT/callback` work unregistered. Once enabled, the MCP client's own OAuth flow connects with zero application code changes — don't build a custom OAuth provider for this, it was tried and reverted as unnecessary. Verified live: create-then-`GET`-then-`PUT` with this field works end-to-end. Including it in the initial `POST` (as above) is unverified but schema-supported; if it doesn't take on create, `PUT` it in after, merging into the full existing body (not dropping `domain`/`policies` — `PUT` replaces the whole object).

Needs an API token — `wrangler login`'s session has no Access scope. Token needs `Account.Access: Apps and Policies` Edit permission. A "Read all resources"-template token authenticates GETs but fails this POST with a generic "Authentication error" (code 10000); fix is adding Edit permission, not re-debugging the body.

Response's `aud` field = `POLICY_AUD`.

**c. Set the secrets:**

```bash
pnpm exec wrangler secret put TEAM_DOMAIN    # https://<team-name>.cloudflareaccess.com
pnpm exec wrangler secret put POLICY_AUD     # the "aud" from step 4b's response
```

`wrangler secret put` deploys immediately — no separate restart.

**d. Connect it:**

```bash
claude mcp add --transport http --scope user <name> https://<worker-domain>/mcp
```

First real tool call triggers `authenticate`, returning a `https://<team-domain>.cloudflareaccess.com/cdn-cgi/access/oauth/authorization?...` URL — user opens it, logs in via the same Access policy as the browser app. If the `localhost` redirect shows a connection error (expected headless/remote), have them paste the address-bar URL back for `complete_authentication`. Verify with a real call (`whoami`, `list_projects`), not just a handshake.

## 5. Integrations

**DataForSEO — required, not gated by any step 0 answer** (see `docs/DATAFORSEO_API_KEY.md` — most of the app's SEO data depends on this one). Do this regardless of what step 0's yes/no answers were:
1. https://app.dataforseo.com/api-access → "Send by email" → copy the **Base64** credential.
2. Already `email:password` base64 — set as-is:
   ```bash
   pnpm exec wrangler secret put DATAFORSEO_API_KEY
   ```
3. Recommended: DataForSEO responses cache in R2 under `dataforseo-cache/` and accumulate without a cleanup rule:
   ```bash
   pnpm exec wrangler r2 bucket lifecycle add <slug>-r2 dataforseo-cache-expiry dataforseo-cache/ --expire-days 7
   ```

The rest of this section is required — set up all of the following.

**SAM/OpenRouter:**
1. Key from https://openrouter.ai/settings/keys.
2. ```bash
   pnpm exec wrangler secret put OPENROUTER_API_KEY
   ```

**Google Search Console** (base flow `docs/SELF_HOSTING_GOOGLE_SEARCH_CONSOLE.md`; corrections below aren't in that doc yet and are required for a working connection):

a. Create/select a Google Cloud project.
b. Explicitly enable the Google Search Console API (APIs & Services → Enabled APIs, or the [direct link](https://console.cloud.google.com/apis/library/searchconsole.googleapis.com)). Most common failure point: OAuth consent succeeds, tokens store fine, then every API call 403s with a generic "denied access to this property" in the app UI — the real Google-side error (`SERVICE_DISABLED`/`accessNotConfigured`) only shows server-side. Enabling can take a few minutes to propagate.
c. OAuth consent screen: External, fill app name/support/dev contact, add the connecting account as a **test user** while in Testing mode (or `access_denied`).
d. OAuth consent screen → Data access → Add or Remove Scopes: add all four the app requests — grep `src/shared/gsc.ts` for `GSC_OAUTH_SCOPES` rather than trusting a stale list (as of writing: `openid`, `email`, `profile`, `https://www.googleapis.com/auth/webmasters.readonly`). Not in the picker (only shows enabled APIs' scopes)? Use "Manually add scopes."
e. Create an OAuth 2.0 Client ID (Web application). Redirect URI must be exactly `https://<worker-domain>/api/gsc/oauth/callback` — no trailing slash, exact scheme/host/port, or `redirect_uri_mismatch`.
f. Set all three together (any one missing reports GSC as "not configured"):
   ```bash
   pnpm exec wrangler secret put GOOGLE_CLIENT_ID
   pnpm exec wrangler secret put GOOGLE_CLIENT_SECRET
   pnpm exec wrangler secret put BETTER_AUTH_SECRET   # openssl rand -base64 32, >=32 chars
   ```

## 6. Site Audit / Workers Paid

Required. Workers Free has a hard, non-configurable 10ms CPU-time-per-invocation ceiling; Site Audit's crawl step is CPU-heavy and fails every retry on Free with `Error: Worker exceeded CPU time limit.` — platform limit, not a bug to debug further. Assume the account is already on Workers Paid — do not touch billing or upgrade plans.

1. Add to `wrangler.jsonc`:
   ```jsonc
   "limits": { "cpu_ms": 300000 }   // platform max, 5 minutes
   ```
2. Redeploy: `pnpm run deploy` (a `wrangler.jsonc` edit needs redeploy; unlike a secret, it isn't automatic).

## 7. Verify

- Open the Worker's URL → Access login prompt → sign in as the configured email → app loads.
- GSC: Integrations → "Connect with Google" → complete the flow.
- Site Audit: run one, confirm it completes past the crawl step.
- MCP: already verified in step 4d.
