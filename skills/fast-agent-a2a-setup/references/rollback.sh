#!/usr/bin/env bash
# Idempotent rollback. Uses the latest backup pointer under ~/.fast-agent/backups/<label>-latest.
# Reference: fast-agent-a2a-setup skill.
set -euo pipefail

LABEL="${LABEL:-com.goodshepherd.fast-agent-a2a}"
LABEL_GATEWAY="${LABEL_GATEWAY:-com.goodshepherd.fast-agent-a2a-gateway}"
BACKUP_POINTER="${BACKUP_POINTER:-/Users/dev/.fast-agent/backups/a2a-latest}"
HOST_UID=$(id -u)

backup_dir=$(cat "$BACKUP_POINTER")
echo "rollback from: $backup_dir"
[ -d "$backup_dir" ] || { echo "FAIL: backup dir missing"; exit 1; }

launchctl bootout "gui/$HOST_UID/${LABEL_GATEWAY}" 2>/dev/null || true
launchctl bootout "gui/$HOST_UID/${LABEL}" 2>/dev/null || true

# Restore mutable files
[ -f "$backup_dir/dev.md" ]     && cp "$backup_dir/dev.md"     /Users/dev/.fast-agent/agent-cards/dev.md
[ -f "$backup_dir/${LABEL}.plist" ] && cp "$backup_dir/${LABEL}.plist" "/Users/dev/Library/LaunchAgents/${LABEL}.plist"

# Remove artifacts introduced by the gateway
rm -f /Users/dev/.fast-agent/agent-cards/manager.md
rm -f /Users/dev/.fast-agent/a2a_bearer_gateway.py
rm -f /Users/dev/.fast-agent/tests/test_a2a_bearer_gateway.py
rm -f "/Users/dev/Library/LaunchAgents/${LABEL_GATEWAY}.plist"

# Bring upstream back up (gateway artifacts gone, so no gateway to start)
launchctl bootstrap "gui/$HOST_UID" "/Users/dev/Library/LaunchAgents/${LABEL}.plist"
for _ in {1..40}; do
  curl -fsS --max-time 1 http://127.0.0.1:8001/.well-known/agent-card.json >/dev/null && break
  sleep 0.25
done

echo "ROLLBACK PASS"
echo "NOTE: bearer key at /Users/dev/.fast-agent/secrets/a2a-bearer-key was retained; delete it manually only after confirming no future reuse."
