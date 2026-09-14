# PROMPT — Use the GSI agent-qa MCP (paste for any coding agent)

You have access to a shared QA runtime for Good Shepherd Insights web projects. Use it to verify UI changes, run sizing/accessibility passes, and read real run evidence. Everything below is verified live.

## 1. Fetch the skill (do this first)

Fetch the canonical skill and load it before acting:

```bash
curl -fsSL https://raw.githubusercontent.com/good-shepherd-insights/skills/main/skills/agent-qa-mcp/SKILL.md -o /tmp/SKILL-agent-qa-mcp.md
```

Read it fully. Its references (same directory on GitHub): `references/tool-catalog.md` (all 33 MCP tools with server-provided descriptions) and `references/test-yaml-shape.md` (canonical test YAML + rules). Do not proceed without reading the SKILL.md.

## 2. Install the runtime (only if not already present)

The harness lives at /home/dev/Projects/qa-harness. If it exists, use it — never reinstall over it.

```bash
git clone https://github.com/good-shepherd-insights/skills.git /tmp/skills
# agent-qa itself (if missing):
cd /home/dev/Projects/qa-harness && npm install -D agent-qa@0.1.21
```

Environment requirements (verified): Node >= 24 (export PATH=~/.local/node24/bin:$PATH — the box default node is 22 and FAILS); Chromium via symlinked ~/.cache/ms-playwright/chromium-1243 (agent-qa install-browsers fails on ubuntu26.04 — use the existing symlink); LLM credential in ~/.agent-qa/auth.json (never put keys in repo files, shell args, or logs).

Verify readiness: `cd /home/dev/Projects/qa-harness && npx agent-qa doctor` — all checks must pass before running tests.

## 3. Use the MCP (preferred) or CLI

- MCP server: http://127.0.0.1:3471/mcp — NO auth, no handshake required. JSON-RPC 2.0 over HTTP POST. Responses are SSE-framed; use the exact parse pattern in the skill (naive SSE parsing fails on 1.2MB step payloads).
- Start with `agent_qa_discover`, then `agent_qa_get_config` for targets.
- Workflow: get_config → author/validate test (agent_qa_validate_test) → agent_qa_enqueue_test_run → poll agent_qa_get_run → agent_qa_get_run_artifact → on FAIL, agent_qa_classify_failure.
- CLI equivalent: cd /home/dev/Projects/qa-harness && npx agent-qa run tests/<file>.yaml --headless --junit-output .agent-qa/<name>.junit.xml
- Dashboard (human viewing): http://192.168.1.174:3470

## 4. Rules that are not negotiable

- Validate every test before running. Never weaken an assertion to force a pass.
- ALWAYS read accessibilityViolations from agent_qa_get_run_steps even when the test PASSES — failOnViolation is false and serious WCAG violations have been recorded on passing runs (verified: 10 color-contrast violations on wrightway-live).
- agent-qa has NO Figma integration and NO pixel-diff. Design intent must be encoded as explicit assertions (exact px/colors via DOM), not left to the model's eye.
- Targets live in agent-qa.config.yaml (cupscakes, wrightway, wrightway-live, example-web). Reuse them; add new ones only when needed.
- Secrets stay in ~/.agent-qa/. Runtime artifacts (.agent-qa/) are gitignored — never commit them.
- Distinguish app bugs from test authoring/environment errors before reporting. Report app bugs with evidence, do not fix without authorization.
- A skipped, interrupted, or unexecuted test is not a pass. Do not claim success without a run ID and terminal status.

## 5. Reporting

Report: run ID, verdict, per-step results, accessibility violations with selectors, evidence locations (.agent-qa/artifacts/<runId>/), and the exact rerun command.
