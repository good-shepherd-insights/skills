# agent-qa — install, understand, use

agent-qa is a self-improving QA agent by Vostride (github.com/vostride/agent-qa). You write tests in plain-English YAML files. At runtime an LLM looks at real screenshots of your app and drives a real browser (Chromium/Playwright) to execute each step and check each expected outcome. Every run records evidence: per-step screenshots, the DOM, the agent's reasoning, WCAG violations, console/network logs, and a video. After runs, it stores what it learned about your app in a memory directory, so future runs are faster and more accurate. No test scripts are generated or compiled — the YAML is the test.

Good Shepherd Insights runs one shared installation for all web projects at /home/dev/Projects/qa-harness. Multiple projects are targets inside it (cupscakes, wrightway, wrightway-live). The skill explaining the MCP interface in depth is in this repo at skills/agent-qa-mcp/SKILL.md.

## What actually happens when a test runs

1. The planner reads your test YAML and the app's current page (screenshot + DOM).
2. For each step it decides concrete actions (click, scroll, assert), takes them, and compares observed outcomes against the step's expected outcome.
3. A rule-based WCAG scanner (axe) runs after each step and records violations with exact CSS selectors — independently of the LLM's judgment.
4. Results, screenshots, video, logs, and violations are stored in .agent-qa/ and visible via dashboard or MCP.

## Install (fresh machine)

```bash
# 1. Node 24+ (agent-qa fails on older node)
curl -fsSL https://nodejs.org/dist/v24.10.0/node-v24.10.0-linux-x64.tar.xz | tar -xJ -C ~/.local --strip-components=1 --one-top-level=node24
export PATH=~/.local/node24/bin:$PATH

# 2. Create the workspace and install agent-qa
mkdir -p ~/Projects/qa-harness && cd ~/Projects/qa-harness
npm init -y && npm install -D agent-qa@0.1.21
npx agent-qa init --platform web --dir .

# 3. Browser: on Ubuntu 26.04 install-browsers fails; reuse any existing
#    ~/.cache/ms-playwright/chromium-*/ build by symlinking it to the version
#    agent-qa's playwright-core expects (check: node -e "require('playwright-core').chromium.executablePath()")

# 4. LLM credential: agent-qa needs a vision-capable model. Store the key OUTSIDE the repo:
#    ~/.agent-qa/auth.json, chmod 600. Configure the LLM in agent-qa.config.yaml (registry.llms).
#    Example config used here: openai-compatible, google/gemini-2.5-flash via the Kilo gateway.

# 5. Verify everything
npx agent-qa doctor        # all checks must pass
npx agent-qa auth test     # real model call, proves the LLM works
```

## Configure (agent-qa.config.yaml)

Three things matter: which LLM (registry.llms), which apps to test (registry.targets), and budgets (use.planner.maxSubActions — long pages need 25+, the default 10 causes false failures when a step must scroll a lot).

```yaml
registry:
  llms:
    - name: qa
      provider: openai-compatible
      model: google/gemini-2.5-flash
      baseURL: https://api.kilo.ai/api/gateway/v1
  targets:
    my-site:
      platform: web
      url: https://mysite.com
use:
  planner:
    maxSubActions: 25
  llm: qa
```

## Use

Write a test (tests/<name>.yaml):

```yaml
test-id: t_<canonical-id>          # never invent: generate via MCP tool agent_qa_generate_id
name: Homepage loads and is accessible
target: my-site
steps:
  - Verify the page loads with visible navigation and main content
  - Verify there is no horizontal overflow at desktop width
  - Verify every image has alt text
```

Run and check:

```bash
npx agent-qa validate tests/homepage.yaml                    # schema check — always do this first
npx agent-qa run tests/homepage.yaml --headless --junit-output .agent-qa/homepage.junit.xml
```

Read results: verdict, per-step pass/fail, screenshots and video in .agent-qa/artifacts/<run-id>/. ALWAYS also read the axe violations per step (JUnit or MCP get_run_steps): a test can PASS while serious WCAG violations were recorded — failOnViolation is false by default. Never report "no accessibility issues" without checking that data.

## MCP (for agents driving QA programmatically)

The MCP server (http://127.0.0.1:3471/mcp, no auth, JSON-RPC 2.0 over HTTP POST) exposes 33 tools covering: discover/config/schema, full CRUD on tests/suites/hooks, enqueue runs, read runs/steps/logs/artifacts, cancel, and classify_failure (sorts app bug vs test authoring vs environment). Full catalog: skills/agent-qa-mcp/references/tool-catalog.md. Transport details and a working parse pattern for the large SSE responses: skills/agent-qa-mcp/SKILL.md.

## Rules

- Validate before every run. Never weaken an assertion to force a pass.
- Check accessibilityViolations on every run, pass or fail.
- No Figma/pixel-diff capability: design conformance must be encoded as explicit assertions (exact px/colors read from the DOM), not left to the model's judgment.
- Secrets live in ~/.agent-qa/ (never in the repo); .agent-qa/ is gitignored.
- Report run ID, verdict, violations with selectors, and the exact rerun command. A skipped or interrupted run is not a pass.
