# Violations — magic-string/literal audit definition (drop-in template)

Violation: a literal in an app file (not `constants/*.ts`) that is —

1. **Secret/vendor ID** (API key, tenant ID, auth token) inline instead of `process.env`.
2. **Internal constant** used 2+ times, or project-meaningful (status, event tag, route, file extension, poll interval) — not imported from `constants/*.ts`.
3. **Vendor API contract literal** (JSON field to/from an external API/SDK) — not imported, even though vendor-fixed.
4. **Protocol/platform keyword** (HTTP method, MIME type, status code, iframe `allow`) — platform-fixed, still shouldn't be typed inline.
5. **Human-readable text** (UI copy, log/error message) — not imported from `strings.ts`/`messages.ts`.
6. **Duplicated literal** across 2+ files, no shared constant — strongest signal, any category.

## Not a violation

- Presentation-only value (inline CSS `width`/`height`/`border`) — meaningless, single-use.
- Language/framework-forced literal (e.g. `"use client"`) — not extractable.
- Typed SDK's own param/response field — compiler catches typos. Prefer a named constant, but not a hard violation — unlike untyped `fetch()`/webhook JSON fields, which are hard violations (no compiler protection).

## No exceptions

Category 2 has no single-file/component-local carve-out. A project-meaningful constant — including timing values, DOM ids, action identifiers — goes in `constants/*.ts` even if single-use, already named, or "owned" by one component. Presentation-only exemption covers style only, never behavior, identifiers, or copy.

### Vendor-generated source (scaffolded/codegen files)

Vendor-authored files copied into the repo (UI-kit generators, SDK scaffolds) are still application code — same audit applies. Rendered copy → `strings.ts`; timing/logic values → `constants/*.ts`. Exceptions:

- Vendor's own typed string unions/enums (event/message/role/status types) — typed-shape exemption; not duplicated copy if each string appears once in its union.
- Single-use vendor literal in a typed comparison — same reasoning.
- Vendor-supplied artwork (inline SVG hex fills) — presentation-only, exempt.

## Current status

Fill in per audit: date/method, zero-violations or list of open ones, pointer to the audit trail (don't duplicate it here).

## Known open items (not violations)

- Assumption vs. confirmed truth, and how confirmed — live-test beats docs.
- Duplicate-meaning constants → collapse to one, unless they're genuinely different vendors' wire contracts that happen to coincide.
- Known missing security control (e.g. no webhook signature check) — flag it, don't leave it silent.
- Blocking external dependency (interactive login, missing credential/deploy key) — name exactly what a human must do.

## Functional bugs (not magic-string issues, found incidentally)

- Provider/context defined but never mounted where consumers can reach it.
- Framework-required file missing entirely (e.g. root layout).
- Dependency imported somewhere but absent from the manifest.
- Env var read as guaranteed present but absent locally.
- Missing build/tooling config (e.g. `tsconfig.json`/path resolution) that imports depend on.
