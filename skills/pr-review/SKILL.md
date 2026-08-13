---
name: pr-review
description: Inspect and address actionable GitHub pull-request review comments, then verify and report the result. Use when the user asks to review, fix, or resolve PR feedback.
---

# Pull request review workflow

Use this skill when the user asks to inspect or fix review feedback.

1. Identify the PR and inspect its base/head, changed files, checks, review state, and all unresolved review threads. Prefer the GitHub review-comment workflow and thread-aware GraphQL data over a flattened comment list.
2. Classify every unresolved item as actionable, informational, duplicate, or already addressed. Do not silently discard actionable feedback.
3. For requested fixes, edit the PR branch, keep changes scoped to the review, and run focused tests/typechecks/lint relevant to the touched code.
4. Commit and push the fixes to the same PR branch. Re-fetch the review threads after pushing.
5. Resolve a thread only when its requested change is implemented and verified; leave informational or unresolved threads open. Never claim all comments are resolved without checking thread state.
6. Report each addressed item, verification output, remaining unresolved threads, and the PR URL. If the user explicitly asks to resolve all actionable comments, do so only after the fixes are present on the remote branch.

For repository-specific conventions, read `.claude/skills/cupscakes-project-management/workflows/github/review-comments.md` and `verification.md` when available. This is the Codex skill entry point and does not require `.claude/commands` files.
