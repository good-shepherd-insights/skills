# Test YAML — canonical shape (validated live with `agent-qa validate`)

```yaml
test-id: t_quiet-river-noble-panda-ember-falcon-garden-harbor-island-jungle
name: Wright Way live - sizing and accessibility pass
target: wrightway-live

context: >
  QA pass over the deployed Wright Way homepage. Focus: (1) responsive sizing -
  no horizontal overflow, no clipped or overlapping content, legible text.
  (2) Accessibility - alt text, heading hierarchy, contrast, tappable controls.
  Scan the full page including content revealed by scrolling.

steps:
  - Verify the page loads fully with visible navigation, a hero section, and main content
  - Verify there is no horizontal scrolling or horizontal overflow on the page
  - Scroll to the bottom of the page, then verify every image seen on the page has meaningful alt text and none appears broken
  - Verify headings on the page form a sensible hierarchy with exactly one h1
  - Verify all visible text is legible against its background (no obviously low-contrast text)
  - Verify links and buttons are large enough to tap or click comfortably
```

## Rules

- test-id: canonical t_ id (11 words) — generate via agent_qa_generate_id, never invent
- target: must exist in agent-qa.config.yaml registry.targets (get it via agent_qa_get_config)
- steps: natural language, action + EXPECTED OUTCOME in each. Assertions about observable outcomes, never just clicks.
- context: free text the planning agent reads first — scope long pages here ("Scan the full page including content revealed by scrolling")
- Long pages: bump use.planner.maxSubActions (>= 25) in agent-qa.config.yaml or the agent dies at 10 actions scrolling
- Validate before every run: agent_qa_validate_test {testId|path}
- Never weaken an assertion or change expected behavior to force a pass
