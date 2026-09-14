---
name: agent-qa-mcp
description: Use when any agent needs to run, author, inspect, or triage QA tests for GSI web projects via the agent-qa MCP server on this box (localhost:3471/mcp) — verifying a change against a live site, checking a UI flow, sizing/accessibility passes, or reading run evidence. Covers the verified transport shape (SSE-framed JSON-RPC, 1.2MB payloads, no auth), the 33 tools, the run workflow, and the evidence fields agents can rely on.
---

# agent-qa MCP — shared QA runtime for GSI agents

The QA harness lives in its own repo: /home/dev/Projects/qa-harness (agent-qa 0.1.21, npm latest, committed). One workspace, multiple project targets. All facts below were verified live against the running server on 2026-09-14 (tools/list + a real run's artifact bundle) — not copied from docs.

## Endpoints (this box)

| Service | URL | Auth | Binding |
|---|---|---|---|
| MCP server | http://127.0.0.1:3471/mcp | NONE (bare JSON-RPC accepted, no init handshake needed) | localhost-only (LAN probe → connection refused) |
| Dashboard UI | http://192.168.1.174:3470 (LAN) / http://127.0.0.1:3470 | none | all interfaces — anyone on LAN can see run history |
| Hosted docs MCP (read-only reference) | https://vostride.com/mcp | none | tools: search_agent_qa_docs, search_agent_qa_library, read_agent_qa_page |

The MCP only works while its server is up. It auto-starts when `agent-qa run` executes (side effect), but the reliable path is explicit. If 3471 is down, start services from the workspace:

    export PATH=~/.local/node24/bin:$PATH
    cd /home/dev/Projects/qa-harness
    setsid nohup npx agent-qa dashboard --port 3470 > /tmp/agentqa-dashboard.log 2>&1 < /dev/null &
    # MCP: either an `agent-qa run` boots it, or check `npx agent-qa mcp --help` for a standalone command

ALWAYS set PATH first: the box's default node is v22; agent-qa requires 24+ (installed at ~/.local/node24). Without it, better-sqlite3 fails with ERR_DLOPEN_FAILED.

## Transport: how to actually call it (verified, non-obvious)

JSON-RPC 2.0 over HTTP POST to /mcp. Response is SSE-framed: `event: message` + ONE `data:` line containing the envelope. The 1.2MB step payloads make naive SSE parsing fail — the data line contains pretty-printed JSON with literal newlines inside strings. Working parse (Python):

    req = urllib.request.Request("http://127.0.0.1:3471/mcp", data=json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":...,"arguments":{...}}}).encode(), headers={"Content-Type":"application/json","Accept":"application/json, text/event-stream"})
    raw = urllib.request.urlopen(req, timeout=30).read().decode()
    start = raw.find('data: {"result"'); end = raw.rfind('"jsonrpc":"2.0","id":1}')
    env = json.loads(raw[start+6:end+24].replace("\n\n", ""))
    result = json.loads(env["result"]["content"][0]["text"])  # tools return JSON-as-text

No auth header, no initialize required — though a clean client does initialize first (protocolVersion "2024-11-05").

## The 33 tools (verified live)

Discover/config: agent_qa_discover, agent_qa_get_config, agent_qa_schema_reference, agent_qa_validate_definition, agent_qa_generate_id, agent_qa_validate_id
Tests CRUD: agent_qa_list_tests, read_test, validate_test, create_test, update_test, delete_test
Suites CRUD: agent_qa_list_suites, read_suite, validate_suite, create_suite, update_suite, delete_suite
Hooks: agent_qa_list_hooks, read_hook, create_hook, update_hook, delete_hook, run_hook
Runs: agent_qa_enqueue_test_run, agent_qa_enqueue_suite_run, get_run, get_run_steps, get_run_logs, get_run_execution_logs, get_run_artifact, cancel_run, classify_failure

Key argument shapes (verified): run tools take {"runId": "r_..."}; test tools take canonical test-id (t_...) or path; enqueue returns the canonical run ID. agent_qa_discover is the safe first call for any agent unsure where to start.

## The standard agent workflow (verified end-to-end)

1. agent_qa_get_config → confirm target exists (targets: example-web, cupscakes→localhost:4321, wrightway→www.wrightwaymoves.com, wrightway-live→wrightway-website.goodshepherdinsights.com)
2. Author test → agent_qa_validate_test (schema check; schema reference via agent_qa_schema_reference)
3. agent_qa_enqueue_test_run {runId} → poll agent_qa_get_run until terminal status
4. agent_qa_get_run_artifact → verdict, evidence, video, JUnit
5. On FAIL: agent_qa_classify_failure → app bug vs test authoring vs environment. Report bugs with evidence; never weaken an assertion to force a pass.

CLI equivalent (same workspace, same evidence): npx agent-qa run tests/<file>.yaml --headless --junit-output .agent-qa/<name>.junit.xml

## What a run's evidence contains (verified from run r_clang-left-edith-ben-vertex-lift-duck-azine-market-formed)

Per step: status, duration, the agent's reasoning text, the concrete action (type/condition/selector), full DOM+accessibility-tree context before/after, screenshot path, console+network logs, healing attempts, confidence, token usage, and accessibilityViolations[] — each with ruleId, impact, description, helpUrl, and exact offending HTML+CSS selector per node.
Per run: verdict, video (webm), the exact test YAML source, testId, timestamps, memory-curator log, failure summary/error log.
IMPORTANT gotcha learned the hard way: config has accessibility.failOnViolation: false — the test can PASS while the axe scanner recorded serious WCAG 2 AA violations (e.g. 10 color-contrast violations on wrightway-live: .wct-navbar-services, .wct-navbar-call, .wct-hero-review-button, the 6 .wct-services-overview-pill buttons, .wct-shs-cta-call). ALWAYS read accessibilityViolations from get_run_steps regardless of verdict. Never report "zero violations" without checking the scanner data.

## What the evidence is (and is not)

Machine-verified: axe scans, overflow checks, computed DOM/CSS values, network/console logs, exact selectors.
Agent-judged: natural-language assertions ("legible contrast", "matches design"), visual similarity to a Figma frame. agent-qa has NO Figma integration and NO pixel-diff engine (verified: package source + 33 MCP tools + llms.txt). Design intent must come from outside: export the frame, hard-code design values as explicit assertions (exact px/colors via DOM), let agent-qa verify deterministically.

## Environment facts (why these exact steps)

- Node 24 required (doctor FAILs on 22): export PATH=~/.local/node24/bin:$PATH
- Playwright chromium: symlinked ~/.cache/ms-playwright/chromium-1243 → chromium-1217 (+ headless_shell) because ubuntu26.04-x64 has no official build
- LLM: config "qa" = openai-compatible google/gemini-2.5-flash via Kilo gateway; key in ~/.agent-qa/auth.json (0600) — NEVER in repo files
- Known defect: memory curator fails ("No object generated: response did not match schema") with Gemini via Kilo — runs pass, memory not distilled yet
- Planner cap: long pages need use.planner.maxSubActions >= 25 (10 caused a false-failure on wrightway)
- Services run from /home/dev/Projects/qa-harness; dashboard default db is its own runs.db — restart dashboard from the workspace root to bind the right db

## Official docs (treat as reference)

- Quickstart: https://vostride.com/docs/agent-qa/agent-quickstart.md
- Index (all pages): https://vostride.com/llms.txt
- Config: configuration.md · Tests: tests.md · MCP: mcp.md · CLI: cli.md
- Version-specific: 0.1.21 init has only --dir/--platform/--skip-install/--force (no --yes/--provider/--model); config init defaults anthropic-subscription + adds @vostride/agent-qa-subscription-auth (removed here deliberately; we use API-key auth)

## Writing a new test for a project (canonical shape)

    test-id: t_<canonical-id>   # generate via agent_qa_generate_id
    name: <human name>
    target: <target-name from config>
    context: >  # optional — tells the agent the focus
    steps:
      - <natural language action + expected outcome>
      - Verify <observable assertion>, not just clicks

Validate before running. Reuse existing targets before adding new ones. Keep runtime artifacts (.agent-qa/) out of commits — they are gitignored.
