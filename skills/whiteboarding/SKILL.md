---
name: whiteboarding
description: >-
  Populate and iteratively review mechanically supplied, project-first execution plans before repository changes. Use for features, fixes, docs, styles, refactors, performance, tests, build, CI, chores, or reverts. Require repository evidence, exact unified diffs for every affected file, iterative correction, and explicit approval before implementation.
license: MIT
metadata:
  version: 1
---

# Whiteboarding

Plan before implementation. The plan file may change before approval; implementation files may not. A whiteboard is an implementation document, not a summary: it must make execution mechanical by stating the exact code or content added, removed, or replaced in every affected file. Never substitute generic framework or language patterns for the repository's established structure and conventions.

## Modes and Status

- **Scaffold:** When the supplied plan document has no substantive plan yet, inspect the repository and populate it. End with `Status: Scaffolded — review required.`
- **Review:** When a plan exists or the user says `review` or `continue`, reread the complete plan, original goal, current repository, and worktree. Do not rely on prior conversation memory.
- **Implement:** Begin only after the user explicitly approves a `Prepared` plan. If requirements or repository facts change, revise and reapprove first.

Every review pass must have exactly one result:

- Fix one or more concrete issues, record them in the Review Log, and end `Status: Revised — review again.`
- Find no material issue after a complete check, record the evidence, and end `Status: Prepared — awaiting explicit approval.`

Never revise and claim `Prepared` in the same pass. A later pass must independently verify the revision.

`Scaffolded` does not permit vague file descriptions. The first plan must already contain exact changes wherever repository evidence is available. If exact changes cannot be written, record the missing evidence or decision as a blocker; never replace code with intentions.

The plan document is supplied mechanically. Never create, move, rename, or choose the location or filename of a plan document. If none is available, stop and report that the required document was not supplied.

## Project-First Gate

Do not choose a solution and retrofit it onto the project. Before proposing code:

1. Read applicable repository instructions and inspect worktree state.
2. Find the closest comparable implementation and trace its definitions, callers, consumers, types, state, configuration, errors, tests, and build/deployment effects.
3. Search every symbol, route, event, schema key, configuration key, and data shape expected to change.
4. Verify dependencies, versions, and project-native commands from manifests, lockfiles, source, or authoritative documentation.

The Pattern Audit must cite concrete repository-relative paths and symbols and explain the constraint each source establishes. A file list is not evidence. If no precedent exists, record what was searched and justify the smallest compatible addition. Never invent structure, APIs, code, commands, versions, or project behavior.

**Weak:** “Follow the existing service pattern.”

**Acceptable form:** “`path/to/file:symbol` owns X; `path/to/caller:symbol` depends on Y; `path/to/test:test name` proves Z. Therefore the plan extends X here, preserves Y, and validates Z this way.”

## Workflow

### 1. Establish the User Contract

State the purpose and user-visible outcome. Convert the request into numbered acceptance criteria, constraints, exclusions, and behavior that must remain unchanged. Ask only when an unresolved user decision would materially change architecture, behavior, data, or scope.

### 2. Research Before Writing

Map the affected subsystem from entry point to observable output. Inspect comparable implementations and their full responsibility chains. Record material decisions in an evidence ledger:

| Decision | Repository or explicit-user evidence | Constraint learned | Reuse or deviation |
|---|---|---|---|

Generic best practices and agent preference are not evidence.

### 3. Scaffold or Correct the Plan

Populate or correct the supplied plan document. Keep it self-contained: a new contributor must understand the goal, repository context, decisions, steps, and proof without prior chat history.

Map every acceptance criterion to affected files, a plan step, exact file changes, and observable validation. Include adjacent files only when research shows impact. Prefer the smallest repository-aligned change.

### 4. Specify Every File Exactly

For every implementation file in the directory map, provide the applicable exact-change artifact defined below. Intent, signatures, algorithms, bullet lists, or symbol names never substitute for code or content. Do not defer choices to implementation.

### 5. Review Against Reality

Search outward again from every changed contract and symbol. Check the plan against the current goal and repository, not against its own claims. Reverify every removal and context line against the worktree and inspect every addition for complete imports, identifiers, callers, consumers, tests, and configuration. Correct omissions, unsupported choices, stale code, scope drift, hidden edits, unsafe sequencing, and weak validation.

### 6. Record the Pass and Stop

Append the date, result, issues found or checks completed, corrections made, and evidence consulted to the Review Log. Set the required status and stop; do not implement.

## Plan Contract

Write these sections in order:

1. **Status** — Current scaffold/review result.
2. **Purpose / Big Picture** — Why the change matters and what becomes observable.
3. **User Contract** — Numbered acceptance criteria, constraints, exclusions, invariants, and assumptions.
4. **Acceptance Coverage** — Map every criterion to files, plan steps, and validation.
5. **Context and Orientation** — Explain relevant modules, responsibilities, data flow, and unfamiliar terms using precise paths and symbols.
6. **Directory Map and Modification Table** — List every created, modified, moved, generated, or deleted implementation file and why.
7. **Pattern Audit and Evidence Ledger** — Show comparable implementations, learned constraints, and justified choices or deviations.
8. **Interfaces and Dependencies** — Specify affected contracts, types, schemas, signatures, packages, configuration, and compatibility requirements.
9. **Plan of Work** — Use dependency-ordered, independently verifiable milestones; state each outcome, edits, and proof.
10. **Exact File Changes** — For every touched file, give its action, reason, impact, and its own exact unified diff required below.
11. **Concrete Steps** — Give working directories, exact commands, and concise expected results.
12. **Validation and Acceptance** — Prove user-visible behavior plus relevant success, failure, boundary, regression, and compatibility cases.
13. **Idempotence and Recovery** — Explain safe retries, migrations, generated artifacts, rollback, and cleanup when applicable.
14. **Risks and Decisions** — Record material risks and a dated decision log with rationale.
15. **Review Log** — Preserve every review pass, findings, changes, evidence, and result.
16. **Approval** — State that implementation awaits explicit approval of a `Prepared` plan.

The directory map, modification table, milestones, and exact-file sections must contain the same implementation files exactly once.

## Exact-Change Contract

Give each touched file its own fenced `diff` block containing a valid Git-style unified diff. Never combine multiple files in one block.

- **Create:** diff from `/dev/null` to `b/path` and show every final line with `+`, regardless of file size.
- **Modify:** diff `a/path` to `b/path`; use valid hunk headers and enough unchanged context for stable application. Show every removed and added line across all hunks.
- **Delete:** diff `a/path` to `/dev/null` and show every current line with `-`; list affected references in the reasoning.
- **Move:** use exact `rename from` and `rename to` metadata. If content changes, include complete unified hunks in the same file block and show every changed line.
- **Generate:** give the exact working directory and generator command, then provide an exact unified diff for every committed generated file. Obtain output with a non-mutating dry run or temporary copy; if that is impossible, stop with a blocker. Never predict generated bytes.

Diffs are executable specifications, not illustrations. Removal and context lines must match the current worktree. Hunk ranges must be valid. Never use pseudocode, placeholders, TODOs, prose-only logic, omitted imports, unresolved identifiers, or omission ellipses. There is no large-file, complex-file, unstable-code, generated-file, or "implementation detail" exception. If the exact diff is not yet supportable, the plan is incomplete: inspect further or state the blocker.

Use this format for each file:

````markdown
### `path/to/file`
**Action:** Modify  
**Why:** ...  
**Impact:** ...

```diff
diff --git a/path/to/file b/path/to/file
--- a/path/to/file
+++ b/path/to/file
@@ -10,3 +10,4 @@
 unchanged context
-removed line
+added line
+another added line
 unchanged context
```

#### Reasoning
- Evidence-backed reason for this exact change.
````

The exact changes are the execution source of truth. An implementer may copy them mechanically and must not design, infer, or improvise missing behavior.

### Worked Example

A complete, valid entry — real diff content, not placeholders. Hunk header line counts are computed from the actual before/after content, not estimated:

````markdown
### `src/lib/constants.ts`
**Action:** Modify  
**Why:** `RETRY_DELAY_MS` is referenced in `src/lib/http-client.ts:41` but does not exist yet, so retries currently fire with no delay.  
**Impact:** New exported constant; no existing export changes shape, so no caller updates required beyond the one that already expects it.

```diff
diff --git a/src/lib/constants.ts b/src/lib/constants.ts
--- a/src/lib/constants.ts
+++ b/src/lib/constants.ts
@@ -1,3 +1,4 @@
 export const MAX_RETRIES = 3;
+export const RETRY_DELAY_MS = 250;
 export const TIMEOUT_MS = 5000;
 export const API_VERSION = "v1";
```

#### Reasoning
- `src/lib/http-client.ts:41` already imports `RETRY_DELAY_MS`; this is the missing definition, not a new call site.
- Placed next to `MAX_RETRIES` to match this file's existing grouping of retry-related constants over alphabetical or append-only ordering.
````

### Producing Each Diff Mechanically

Never hand-type a hunk header or count context/added/removed lines by eye — line-count arithmetic done freehand is a known source of silently wrong diffs. Produce every diff by running `scripts/make-diff.sh`, bundled with this skill:

```
scripts/make-diff.sh create <repo-relative-path> <scratch-file>
scripts/make-diff.sh modify <repo-relative-path> <scratch-file>
scripts/make-diff.sh delete <repo-relative-path>
scripts/make-diff.sh move   <old-repo-relative-path> <new-repo-relative-path> [<scratch-file>]
```

Write the file's complete proposed content to a scratch path **outside the repository** first — never write proposed content into the repository itself, since implementation files may not change during planning. Then call the script with the appropriate action.

The script sets its own diff header paths directly (no rewrite step exists to have a bug in), and fails closed: it runs `git apply --check` on its own output before printing anything, so a diff that would not apply cleanly is never emitted. Its exit code is the signal — 0 means the diff on stdout is verified and ready to paste into the plan; any non-zero exit means stop, read the error on stderr, and treat it as a blocker rather than hand-authoring that file's diff instead.

`Generate` (per the Exact-Change Contract) is not a separate mode: run the generator into a scratch file yourself first, then call `create` or `modify` with that output, the same as any other proposed content.

## Review Gate

Before declaring `Prepared`, confirm:

- the plan still matches the user's goal and every acceptance criterion;
- a newcomer can understand the context and execute it without prior conversation;
- every material choice has concrete evidence or an explicit user requirement;
- all definitions, callers, consumers, interfaces, dependencies, and affected files are covered;
- every listed file has its own exact unified diff, every removal and context line matches the current worktree, and every addition is complete and internally consistent;
- for every diff block, the `diff --git a/<path> b/<path>` line and the `--- a/<path>` / `+++ b/<path>` lines use the exact same repo-relative path as the file entry's own heading on both sides (Move/Rename excepted, where `a/` and `b/` legitimately differ) — checked by reading the header text itself, independently of whether `git apply --check` passes, since a malformed path can still pass that check;
- extract every diff block from the plan in file order, concatenate into a single patch, and run `git apply --check <patch>` from the repository root; record the exact command and its result (pass, or the literal error text) in the Review Log — a `Prepared` status requires this to have been run and passed on the current pass, not inferred from an earlier one;
- milestones are safely ordered, incrementally observable, and recoverable;
- commands include their working directory and expected result;
- validation demonstrates behavior, not merely compilation;
- no unsupported claim, unresolved identifier, hidden edit, prose substituted for code, scope expansion, or unexplained deviation remains.

If any check fails, correct the plan and return `Revised`; do not describe the issue without fixing it. If required evidence is unavailable or a user decision blocks correctness, state the blocker instead of fabricating a complete plan.
