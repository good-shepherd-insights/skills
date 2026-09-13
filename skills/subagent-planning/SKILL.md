---
name: subagent-planning
description: Break a task into conflict-resistant parallel tickets for independent agents in isolated worktrees, landing through one coordinator-owned branch and PR. Use when the user wants to split work across subagents, parallelize implementation, fan out to N agents, or prepare a breakdown before spawning agents.
---

# Subagent Planning

Break work into self-contained tickets that start from one frozen commit, edit disjoint scope in separate worktrees, and converge through one coordinator. Share only the outcome and integration mechanics each agent needs; never copy other agents' tickets into its prompt.

The plan document is supplied mechanically. Never create, move, rename, or choose the location or filename of a plan document. If none is available, stop and report that the required document was not supplied.

## Process

1. **Inspect before splitting.** Trace the affected files, symbols, callers, shared contracts, generated artifacts, tests, and configuration. Derive N from independent seams, not a requested number. Reduce N when slices share files, depend on another slice's output, or are sequential phases disguised as parallel work.
2. **Freeze one integration contract.** Record the observable outcome, base branch and exact commit SHA, integration branch, and global acceptance checks. After approval, the contract is read-only; material changes invalidate approval and require a revised plan.
3. **Make ownership disjoint.** Assign exact files or exclusive responsibilities. Include tests, types, exports, registries, schemas, migrations, manifests, lockfiles, generated files, and docs when affected. A shared file belongs to one ticket or a coordinator-owned integration step—never two agents.
4. **Make every ticket self-contained.** Give it an objective, repository evidence, exact ownership, prohibited scope, concrete requirements, observable acceptance criteria, project-native validation, a unique worker branch, and a commit handoff. No ticket may require another ticket's block to understand or finish its work.
5. **Require approval before execution.** Write the complete Shared Contract, every ticket, and Coordinator Integration section to the supplied plan document, then stop. Require explicit user approval given after review of the complete plan. Do not dispatch agents, create worktrees or branches, or modify the repository before approval. A request to plan or parallelize is not approval to execute.
6. **Use isolated branches after approval.** Give every writing agent its own worktree and worker branch at the frozen SHA. Agents never check out or push the integration branch and never open separate PRs. Only the coordinator updates the integration branch and shared PR.
7. **Stop on invalidation.** If an agent needs an unowned file, discovers a cross-ticket dependency, or cannot meet acceptance independently, it must stop and report the exact issue. Do not expand scope or resolve integration conflicts silently. Revise the affected contract or tickets and obtain new approval before resuming.

## Output Template

Write the completed plan, in this structure, to the supplied plan document:

```markdown
## Shared Contract
Outcome: <one observable result all tickets contribute to>
Base: <branch> at <full commit SHA>
Integration: <integration branch>; coordinator alone updates it and maintains one PR
Isolation: one worktree and unique worker branch per writing agent
Scope rule: edit only Owns; otherwise stop and report
Global acceptance:
- [ ] <combined observable behavior>
- [ ] <project-wide validation command and expected result>

## Agent 1 of N — <slice name>
Objective: <complete result this agent owns and why it matters>
Repository evidence: <exact paths, symbols, tests, or configuration establishing the approach>
Owns: <exact files or exclusive responsibility>
Must not touch: <other tickets' scope and shared integration files>
Requirements:
- <concrete requirement>
Acceptance criteria:
- [ ] <observable check>
Validation:
- `<command>` — <expected result>
Worker branch: <unique branch created from the frozen SHA>
Handoff: return commit SHA, changed-file list, validation results, acceptance evidence, and blockers or deviations

## Agent 2 of N — <slice name>
<same fields, fully expanded>

## Agent N of N — <slice name>
<same fields, fully expanded>

## Coordinator Integration
1. Collect every agent's commit SHA and evidence; do not accept uncommitted work.
2. Verify `git diff --name-only <base-sha>...<agent-sha>` is a subset of that ticket's Owns. Reject scope drift.
3. Integrate accepted commits serially into the integration branch in the declared order. A conflict invalidates the split: stop and revise the plan rather than improvising ownership.
4. Run every ticket validation plus Global acceptance against the combined tree. File-level separation does not replace integration testing.
5. Review the cumulative diff against the Outcome, push the integration branch, and create or update one PR. Cite the plan and report each ticket's acceptance evidence.
```

After writing the complete plan to the supplied document, state `Approval required before agent dispatch or repository changes` and stop. Proceed only after the user explicitly approves that version.

After approval, the copy-paste prompt for an agent is the complete `Shared Contract` plus that agent's fully expanded block. Do not include other tickets. The plan is the coordinator's source of truth; worker commits and evidence are its integration inputs.
