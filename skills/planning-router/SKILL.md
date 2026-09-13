---
name: planning-router
description: >-
  Assess code-related work and select exactly one planning workflow: whiteboarding for coupled, uncertain, high-attention, or single-threaded work; subagent-planning only for proven independent parallel slices. Use whenever a plan is needed for a feature, fix, refactor, migration, performance or security change, test, build, CI, code-linked documentation, or other repository change and the planning method must be chosen and explained.
---

# Planning Router

Select exactly one destination from repository evidence: `whiteboarding` or `subagent-planning`. Explain the decision, invoke only the selected skill, and end the routing workflow. Never select, invoke, sequence, or recommend both skills for one routing decision.

Do not draft the plan, create planning artifacts, or implement code. Complexity alone never decides the route: whiteboarding controls coupling and uncertainty; subagent planning requires proven concurrency.

## Understand the Work

Before deciding:

1. State the requested outcome, acceptance signals, constraints, and unresolved decisions.
2. Read applicable repository instructions and inspect worktree state.
3. Trace the closest affected definitions, callers, consumers, shared contracts, tests, configuration, generated surfaces, and likely ownership.
4. Distinguish genuinely concurrent implementation slices from sequential phases or arbitrary file groups.

Inspect enough evidence to decide. Never classify from request wording, estimated effort, or file count alone.

## Make the Binary Decision

Evaluate every subagent eligibility condition below:

1. The outcome, acceptance criteria, architecture, behavior, data, APIs, schemas, migrations, security, permissions, and compatibility decisions are settled.
2. At least two independent implementation slices can start from the same frozen commit and finish concurrently. A slice being small — down to a single file — is not a disqualifier; a simple, self-contained one-file change is often the ideal unit of ownership per agent, usually one file per agent. What disqualifies a slice is coupling, an unsettled design, or a dependency on another slice, never its size.
3. No slice requires another slice's unfinished output, a sequential handoff, or edits to the same implementation file.
4. Ownership is exact and disjoint, including tests, types, exports, registries, schemas, manifests, lockfiles, generated files, and documentation.
5. Shared interfaces and integration behavior already exist or are fully stable; no worker must design or change them independently.
6. Every slice has self-contained acceptance criteria and project-native validation, with a clear combined integration check.
7. Parallel progress materially exceeds coordination and integration cost.
8. Safe planning does not require whiteboarding's exact file-by-file unified diffs to settle implementation details before execution.

Choose `subagent-planning` only when repository evidence proves **all eight** conditions.

Choose `whiteboarding` when **any one** condition fails or remains unknown. This includes complex or high-risk changes, unresolved decisions, shared contracts, coupled call paths, overlapping ownership, sequential work, and tasks where fewer than two genuinely independent slices exist at all — not tasks whose slices happen to be small. Several simple, independent one-file (or few-file) changes are a strong `subagent-planning` fit precisely because each is simple; a single complex integration spanning many interacting files, or a task with only one independent unit of work regardless of file count, is not.

There is no third result. Never choose one skill as preparation for the other. When uncertain, inspect further; if independence still cannot be proven, choose `whiteboarding`.

## Explain the Decision

Report this decision before invoking the selected skill:

```text
Selected skill: <whiteboarding | subagent-planning>
Goal: <one-sentence observable outcome>
Evidence: <concrete paths, symbols, contracts, dependencies, and candidate seams>
Subagent eligibility: <all eight proven | failed or unknown conditions with evidence>
Why selected: <decisive repository-backed reason>
Why rejected: <why the other skill does not fit>
Next action: Invoke only <selected skill>.
```

Keep the explanation concise and causal. Cite concrete repository evidence when a repository exists. Never claim that work is parallelizable, coupled, safer, or high-risk without stating why.

## Enforce the Handoff

1. Read the selected skill completely before acting.
2. Follow only that skill without weakening its entry conditions, approval gates, ownership rules, artifacts, or validation.
3. Do not invoke or recommend the rejected skill during the selected planning workflow.
4. If later evidence invalidates the selected workflow, stop and report the contradiction. Do not switch skills automatically; only a new user-requested routing decision may select a workflow again.

## Examples

- Authentication work spanning middleware, session contracts, guards, and shared tests fails the independence gate: select only `whiteboarding`.
- Three adapters implementing an already-stable provider interface in disjoint source and test files pass every gate: select only `subagent-planning`.
- Five independent, fully-specified one-file tweaks (e.g. a copy change, a prop rename, a style adjustment) in five different components, each with no shared contract and no cross-file coupling: select only `subagent-planning`, one agent per file — small, simple, disjoint slices are the ideal case, not an exception.
- A new subsystem with undecided API, UI, and migration contracts fails the settled-contract gate: select only `whiteboarding`, regardless of possible future seams.
- A single bug fix or feature that only ever resolves to one independent unit of work — whether it touches one file or many coupled files — fails the at-least-two-slices gate: select only `whiteboarding`. Having one file is not itself disqualifying; having only one independent slice is.
