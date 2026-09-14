# agent-qa QA runtime

WHAT: Vostride agent-qa — tests as plain-English YAML; LLM + real Chromium executes them, records evidence (screenshots, DOM, axe WCAG violations, logs, video), learns the app over time. The YAML is the test — nothing compiled.

INSTALL:
    export PATH=~/.local/node24/bin:$PATH   # Node 24+ required, v22 fails
    mkdir -p ~/Projects/qa-harness && cd ~/Projects/qa-harness
    npm init -y && npm install -D agent-qa@0.1.21
    npx agent-qa init --platform web --dir .
    ln -s ~/.cache/ms-playwright/chromium-1243 ~/.cache/ms-playwright/chromium-1217
    npx agent-qa doctor && npx agent-qa auth test

CONFIG (agent-qa.config.yaml): registry.llms (LLM; key in ~/.agent-qa/auth.json, never in repo) | registry.targets (app URLs) | use.planner.maxSubActions: 25

WRITE (tests/<name>.yaml):
    test-id: t_<id>            # via agent_qa_generate_id
    target: <target-name>
    steps:
      - Verify the page loads with nav and main content
      - Verify no horizontal overflow

USE:
    npx agent-qa validate tests/<name>.yaml
    npx agent-qa run tests/<name>.yaml --headless --junit-output .agent-qa/<name>.junit.xml

MCP: http://127.0.0.1:3471/mcp — no auth, JSON-RPC over POST. 33 tools: test/suite/hook CRUD, enqueue runs, read evidence, classify_failure. Dashboard: http://192.168.1.174:3470.

RULES: validate before run | check accessibilityViolations even on PASS (failOnViolation=false) | no Figma/pixel-diff — encode design as explicit assertions | secrets in ~/.agent-qa/, .agent-qa/ gitignored | skipped =/= pass; report run ID + violations + rerun command.
