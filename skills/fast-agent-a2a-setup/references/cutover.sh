#!/usr/bin/env bash
# Idempotent cutover for a fast-agent A2A service.
# Validates files first, then boots upstream, then boots gateway.
# Reference: fast-agent-a2a-setup skill.
set -euo pipefail

LABEL="${LABEL:-com.goodshepherd.fast-agent-a2a}"
LABEL_GATEWAY="${LABEL_GATEWAY:-com.goodshepherd.fast-agent-a2a-gateway}"
HOST_UID=$(id -u)
PYTHON=/Users/dev/.local/share/uv/tools/fast-agent-mcp/bin/python

echo "=== 1. lint plists ==="
plutil -lint \
  "/Users/dev/Library/LaunchAgents/${LABEL}.plist" \
  "/Users/dev/Library/LaunchAgents/${LABEL_GATEWAY}.plist"

echo "=== 2. compile + test gateway ==="
cd /Users/dev/.fast-agent
"$PYTHON" -m py_compile a2a_bearer_gateway.py tests/test_a2a_bearer_gateway.py
"$PYTHON" -m unittest -v tests.test_a2a_bearer_gateway

echo "=== 3. resolve cards ==="
"$PYTHON" - <<'PY'
from pathlib import Path
from fast_agent.core.agent_card_loader import load_agent_cards
from fast_agent.core.validation import get_dependencies_groups
cards = load_agent_cards(Path('/Users/dev/.fast-agent/agent-cards'))
for c in cards:
    timeout = c.agent_data['config'].default_request_params.streaming_timeout
    default = c.agent_data['config'].default
    print(f"  {c.name}: default={default} streaming_timeout={timeout}")
print("  dependency_groups=", get_dependencies_groups({c.name: c.agent_data for c in cards}))
PY

echo "=== 4. bootout upstream, bootstrap new ==="
launchctl bootout "gui/$HOST_UID/${LABEL}" 2>/dev/null || true
sleep 1
launchctl bootstrap "gui/$HOST_UID" "/Users/dev/Library/LaunchAgents/${LABEL}.plist"
for _ in {1..40}; do
  curl -fsS --max-time 1 http://127.0.0.1:8001/.well-known/agent-card.json >/dev/null && break
  sleep 0.25
done
curl -fsS --max-time 2 http://127.0.0.1:8001/.well-known/agent-card.json >/dev/null

echo "=== 5. bootstrap gateway ==="
launchctl bootstrap "gui/$HOST_UID" "/Users/dev/Library/LaunchAgents/${LABEL_GATEWAY}.plist"
for _ in {1..40}; do
  curl -fsS --max-time 1 http://127.0.0.1:8000/.well-known/agent-card.json >/dev/null && break
  sleep 0.25
done
curl -fsS --max-time 2 http://127.0.0.1:8000/.well-known/agent-card.json >/dev/null

echo "=== 6. verify listeners ==="
lsof -nP -iTCP:8000 -iTCP:8001 -sTCP:LISTEN

echo "=== 7. verify auth ==="
[ "$(curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/a2a)" = 401 ] || { echo "FAIL: /a2a boundary not protected"; exit 1; }
A2A_KEY=$(tr -d '\n' < /Users/dev/.fast-agent/secrets/a2a-bearer-key)
status=$(curl -sS -o /dev/null -w '%{http_code}' -X POST -H "Authorization: Bearer $A2A_KEY" -H 'Content-Type: application/json' --data '{}' http://127.0.0.1:8000/a2a/jsonrpc)
unset A2A_KEY
if [ "$status" = 401 ] || [ "$status" = 502 ]; then
  echo "FAIL: valid key got $status"; exit 1
fi

echo "CUTOVER PASS"