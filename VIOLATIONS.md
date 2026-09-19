# Violations — definition, this project

A violation is any literal value in an application file (not a
`constants/*.ts` file) that falls into one of these categories:

1. **Secret or vendor ID** (API key, `face_id`, `pal_id`, `tenant_id`,
   auth token) written inline instead of read from `process.env`.
2. **Internal app constant used more than once, or carrying
   project-specific meaning** (status value, event tag, route path, file
   extension, poll interval) written inline instead of imported from a
   `constants/*.ts` file.
3. **Vendor API contract literal** (a JSON field name sent to or read
   from an external API/SDK — e.g. `"conversation_id"`, `"tenant_id"`)
   written inline instead of imported, even though the value itself is
   fixed by the vendor.
4. **Protocol/platform keyword** (HTTP method, MIME type, status code,
   iframe `allow` string) written inline instead of imported — the value
   is fixed by the platform, but it still doesn't get typed directly into
   application code.
5. **Human-readable text** (UI copy, log message, error message) written
   directly in a component/script instead of imported from a
   `strings.ts`/`messages.ts` file.
6. **A duplicated literal across two or more files** with no shared
   constant backing either occurrence — the strongest signal of a real
   violation, independent of category.

## Not a violation

- **Presentation-only values** (inline CSS: `width`, `height`, `border`)
  — meaning-free, single-use, left inline by design.
- A value required to be a literal by the language/framework itself
  (e.g. Next.js's `"use client"` directive) — not extractable, not a
  choice.
- A field accessed via a **typed SDK's own parameter/response shape**
  (TypeScript already catches a typo at compile time there) — still
  preferred as a named constant in this project for consistency, but not
  a hard violation if missed, unlike untyped `fetch()`/webhook JSON
  fields, which are a hard violation if inlined (zero compiler
  protection against a typo).

## NO EXCEPTIONS (decided 2026-09-08)

Category 2 has **no component-local or single-file carve-out**. If an
internal constant carries project-specific meaning — including timing
values, DOM ids referenced by logic, and action identifiers — it lives in
a `constants/*.ts` file, **even if** it is used only within one file,
even if it is already a named constant, even if the component "owns" it.
"Named constant in the wrong file" is still a violation. The
presentation-only exemption covers meaning-free style values only; it
does not cover behavioral timing, identifiers, or copy.

### Vendor-generated source (cvi-ui) — same rules, applied at scaffold

`@tavus/cvi-ui` copies vendor-authored React source into
`frontend/app/components/cvi/`. Generated files are application code and
get the same audit: rendered copy (JSX text, aria-labels, placeholders)
replaced with `frontend/constants/cviStrings.ts`; behavioral timing and
logic-driving values moved to `frontend/constants/cviTiming.ts`. Two
scoped clarifications for these files only:
- **Vendor wire-format literals inside type definitions** (the
  `event_type`/`message_type`/role string unions in
  `hooks/cvi-events-hooks.tsx`, `use-chat.tsx`) are the vendor's typed
  contract — TypeScript checks them at every use site, matching the
  existing "typed SDK's own shape" exemption. They are not duplicated
  copy; each string appears exactly once in its type union.
- **Participant-filter literal** `'tavus-replica'`
  (`hooks/use-replica-ids.tsx`) is a single-use vendor contract value in
  a comparison — same typed-shape reasoning, recorded here rather than
  extracted.

- **Vendor-generated SVG artwork** — inline hex fills/strokes in cvi-ui
  icon SVGs (`#020617`, `#2D65FF`, `white`) are meaning-free vendor
  artwork: presentation-only, exempt. Documented rather than silently
  relied on (reviewer flag, 2026-09-08).

## Current status (last audited: two independent fresh subagents, zero
violations found against the implemented files on disk)

No known open violations as of the last audit. See `PLAN.md` for the
full audit trail (2 rounds against pseudocode, 1 round in progress
against the real implemented files) and the specific fixes applied
(`FIELDS.CONVERSATION_ID`, `HYDRA_SDK_FIELDS.TOKEN`,
`TRANSCRIPT_FILE_EXTENSION`, `HYDRA_TENANT_POLL_INTERVAL_MS`).

## Known open items — not violations, but real gaps

- **RESOLVED via live API testing (not docs).** The HydraDB API question
  above is closed: `client.tenant.create()`/`client.upload.knowledge()`
  don't correspond to any real endpoint (`GET /tenant` → real 404,
  confirmed live). The real API is a plain REST API:
  `GET /databases`, `POST /context/ingest` (multipart, `database` +
  `app_knowledge` JSON array), `POST /query` (`database` + `query`).
  Full round-trip verified: ingested real text containing a unique
  marker, queried it back, got the exact text with a real relevancy
  score. `graph.ts` rewritten to call this REST API directly via
  `fetch`/`FormData` (same pattern as `sessions.ts`'s Tavus call), no SDK.
  `@hydradb/sdk` dependency removed. `scripts/setup-hydra-tenant.ts`
  deleted — no tenant-creation step exists or is needed; the `podcast`
  database already exists on the account.
- **RESOLVED via live API testing.** Tavus's create-conversation request
  fields are `replica_id`/`persona_id`, not `face_id`/`pal_id` as the
  docs claimed ("modern terminology") — confirmed by creating a real
  conversation with `replica_id`/`persona_id` (succeeded) and immediately
  ending it. Code and env vars updated to match.
- No webhook signature/authenticity verification on
  `/tavus-webhook` — not researched this session, still open.
- `TAVUS_RESPONSE_FIELDS.CONVERSATION_ID` and
  `TAVUS_WEBHOOK_FIELDS.CONVERSATION_ID` held the same string value as two
  separately-named constants — RESOLVED 2026-09-12: both now reference
  `TAVUS_CONVERSATION_ID_FIELD` (tavus.ts); `HYDRA_DOCUMENT_METADATA_FIELDS.CONVERSATION_ID`
  stays its own named constant (same string, different vendor's wire key).
- **BLOCKING, cannot be resolved without the user:** `npx convex dev`
  requires interactive browser OAuth login — confirmed by actually
  running it in this environment (`Cannot prompt for input in
  non-interactive terminals`). No `CONVEX_DEPLOY_KEY` exists yet. Until
  a human runs `npx convex dev` once from `backend/` (or supplies a
  deploy key), there is no live Convex deployment, `_generated/` doesn't
  exist, and nothing in this repo can actually execute — this is the one
  gap that isn't a code problem.

## Functional bugs found by the second implementation audit (not
magic-string violations, tracked here since they block the app running)

1. **HydraDB API shape possibly wrong** — see above, blocking.
2. `ConvexClientProvider` is defined but never mounted anywhere — no
   `frontend/app/layout.tsx` exists, so `useAction`/`useQuery` in
   `page.tsx` have no Convex client context and would throw at runtime.
3. No root `layout.tsx` — Next.js App Router requires one; build fails
   without it.
4. `@hydradb/sdk` is imported in `graph.ts` and the setup script but not
   listed in any `package.json`.
5. Required env vars (`SITE_URL`, `TAVUS_FACE_ID`, `TAVUS_PAL_ID`,
   `HYDRA_TENANT_ID`, `NEXT_PUBLIC_CONVEX_URL`) are read with `!` but not
   present in `.env.local` — real account-specific values, can't be
   fabricated, need to come from the user.
6. No `tsconfig.json` anywhere in the repo; `page.tsx`'s bare-specifier
   imports (`backend/convex/...`) have no path resolution configured
   beyond pnpm workspace symlinking.
