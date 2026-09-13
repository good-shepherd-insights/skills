---
name: pr
description: Create or update a ready-for-review GitHub pull request for the current repository. Use when the user asks to open, update, or publish a PR.
---

# Pull request workflow

Use this skill when the user asks to create or update a pull request.

1. Inspect the current branch, worktree, remotes, and recent commits. Preserve unrelated changes and never include them in the PR.
2. Confirm the intended branch flow from repository guidance. For Cups & Cakes, feature branches merge into `main`; production changes flow through a release branch from `main` and then a PR into `production`.
3. Run the repository's appropriate focused checks. Do not claim a check passed unless its output confirms it.
4. Commit only the requested changes with a concise message, push the feature branch, and check for an existing PR before opening another.
5. Open or update the PR against the requested base branch. Unless the user says otherwise, make it ready for review (not draft), include a useful summary and test evidence, and link the related Linear issue when one is supplied.
6. Report the PR URL, base/head branches, commit, and verification results. If a check or permission blocks the operation, report the exact blocker instead of guessing.

For project-specific conventions, read `.claude/skills/cupscakes-project-management/workflows/github/pull-request.md` and `branch-flow.md` when those files exist. This skill is the Codex entry point; it does not depend on Claude command files.
