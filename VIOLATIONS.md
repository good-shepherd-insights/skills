# Violations — magic-string/literal audit definition (drop-in template)

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

## NO EXCEPTIONS

Category 2 has **no component-local or single-file carve-out**. If an
internal constant carries project-specific meaning — including timing
values, DOM ids referenced by logic, and action identifiers — it lives in
a `constants/*.ts` file, **even if** it is used only within one file,
even if it is already a named constant, even if the component "owns" it.
"Named constant in the wrong file" is still a violation. The
presentation-only exemption covers meaning-free style values only; it
does not cover behavioral timing, identifiers, or copy.

### Vendor-generated source — same rules, applied at scaffold

Some tooling (UI kit generators, SDK scaffolding CLIs, codegen) copies
vendor-authored source directly into the app tree (e.g. a components
directory checked into the repo rather than pulled from `node_modules`).
Generated files are still application code and get the same audit:
rendered copy (JSX text, aria-labels, placeholders, log/error strings)
moves to the project's `strings.ts`/`messages.ts`; behavioral timing and
logic-driving values move to `constants/*.ts`. Two scoped exemptions
apply to vendor-generated files specifically:
- **Vendor wire-format literals inside type definitions** (string
  unions/enums the vendor's SDK defines for event types, message types,
  roles, statuses) are the vendor's typed contract — TypeScript checks
  them at every use site, matching the general "typed SDK's own shape"
  exemption. They are not duplicated copy as long as each string appears
  exactly once in its type union.
- **Single-use vendor contract literal in a comparison** (e.g. a filter
  matching a vendor-defined type/role string) — same typed-shape
  reasoning, record it here rather than extracting it if it's genuinely
  single-use and typed.

- **Vendor-generated artwork** (inline hex fills/strokes/paths in
  vendor-supplied icon/illustration SVGs) — meaning-free vendor artwork:
  presentation-only, exempt. Document rather than silently rely on it.

## Current status

Fill in after each audit pass:
- Date/method of last audit (e.g. "fresh subagent against files on disk",
  "manual pass against PLAN.md checklist").
- Whether it found zero violations or a list of open ones.
- Pointer to wherever the full audit trail lives in this repo (a
  `PLAN.md`, an audit log, PR description), rather than duplicating it
  here.

## Known open items — not violations, but real gaps

Track non-violation findings surfaced during the audit that still need
following up, using this shape per item:
- **What was assumed vs. what's actually true**, and how it was
  confirmed — prefer "verified against the live API/service" over "per
  the docs," since vendor docs are a secondary source per the project's
  own verification rules.
- **Duplicate-meaning constants** — two separately-named constants that
  turned out to hold the same value for the same reason (collapse to one
  unless they represent genuinely different vendors' wire contracts that
  happen to coincide).
- **Missing security control** the audit wasn't scoped to fix (e.g. no
  signature/authenticity verification on an inbound webhook) — flag as
  open rather than silently leaving it.
- **Blocking external dependency** that cannot be resolved by writing
  code (a required interactive login, a missing credential/deploy key,
  an account-side resource that must exist before the app can run) —
  mark it blocking and say exactly what a human needs to do.

## Functional bugs found during the audit (not magic-string violations,
tracked here since they block the app running)

Use this section for real defects the audit surfaces incidentally —
wiring/config problems that would fail at runtime or build time, not
literal/constant-extraction issues. Typical shapes to watch for:
- A provider/context (DB client, auth, state) defined but never mounted
  anywhere consumers can reach it.
- A framework-required file missing entirely (e.g. a root layout/entry
  point the framework assumes exists).
- A dependency imported somewhere but absent from the manifest
  (`package.json`/equivalent).
- Required environment/config values read as if guaranteed present but
  absent from the local env file — especially account-specific values
  that can't be fabricated and must come from the user.
- Missing build/tooling config (e.g. no `tsconfig.json`/path resolution)
  that bare-specifier imports depend on.
