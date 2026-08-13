#!/usr/bin/env bash
# make-diff.sh — mechanically generate one Exact-Change Contract diff block.
# Never hand-type a hunk header. This is the only source of diff text.
# Fails closed: verifies with `git apply --check` before ever printing a diff.
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage:
  make-diff.sh create <repo-relative-path> <scratch-file>
  make-diff.sh modify <repo-relative-path> <scratch-file>
  make-diff.sh delete <repo-relative-path>
  make-diff.sh move   <old-repo-relative-path> <new-repo-relative-path> [<scratch-file>]

Prints the verified unified diff to stdout on success.
"Generate" (per the Exact-Change Contract) is not a distinct mode here:
run the generator into a scratch file yourself, then call create/modify
with that scratch file, same as any other proposed content.
EOF
}

ACTION="${1:-}"
[[ -z "$ACTION" ]] && { usage; exit 1; }
shift

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

SCRATCH_REPO=""
CHECK_FILE=""
cleanup() {
  [[ -n "$SCRATCH_REPO" && -d "$SCRATCH_REPO" ]] && rm -rf "$SCRATCH_REPO"
  [[ -n "$CHECK_FILE" && -f "$CHECK_FILE" ]] && rm -f "$CHECK_FILE"
}
trap cleanup EXIT

DIFF=""

case "$ACTION" in
  create)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    REPO_PATH="$1"; SCRATCH="$2"
    [[ -e "$REPO_PATH" ]] && { echo "ERROR: $REPO_PATH already exists — not a create" >&2; exit 1; }
    [[ -f "$SCRATCH" ]] || { echo "ERROR: scratch file not found: $SCRATCH" >&2; exit 1; }
    DIFF=$(diff -u -L "a/$REPO_PATH" -L "b/$REPO_PATH" /dev/null "$SCRATCH" || true)
    ;;
  modify)
    [[ $# -eq 2 ]] || { usage; exit 1; }
    REPO_PATH="$1"; SCRATCH="$2"
    [[ -f "$REPO_PATH" ]] || { echo "ERROR: $REPO_PATH does not exist — not a modify" >&2; exit 1; }
    [[ -f "$SCRATCH" ]] || { echo "ERROR: scratch file not found: $SCRATCH" >&2; exit 1; }
    DIFF=$(diff -u -L "a/$REPO_PATH" -L "b/$REPO_PATH" "$REPO_PATH" "$SCRATCH" || true)
    ;;
  delete)
    [[ $# -eq 1 ]] || { usage; exit 1; }
    REPO_PATH="$1"
    [[ -f "$REPO_PATH" ]] || { echo "ERROR: $REPO_PATH does not exist — nothing to delete" >&2; exit 1; }
    DIFF=$(diff -u -L "a/$REPO_PATH" -L "b/$REPO_PATH" "$REPO_PATH" /dev/null || true)
    ;;
  move)
    [[ $# -eq 2 || $# -eq 3 ]] || { usage; exit 1; }
    OLD_PATH="$1"; NEW_PATH="$2"; SCRATCH="${3:-}"
    [[ -f "$OLD_PATH" ]] || { echo "ERROR: $OLD_PATH does not exist — nothing to move" >&2; exit 1; }
    [[ -e "$NEW_PATH" ]] && { echo "ERROR: $NEW_PATH already exists — move target occupied" >&2; exit 1; }
    [[ -n "$SCRATCH" && ! -f "$SCRATCH" ]] && { echo "ERROR: scratch file not found: $SCRATCH" >&2; exit 1; }

    SCRATCH_REPO="$(mktemp -d)"
    git init -q "$SCRATCH_REPO"
    mkdir -p "$SCRATCH_REPO/$(dirname "$OLD_PATH")"
    cp "$OLD_PATH" "$SCRATCH_REPO/$OLD_PATH"
    ( cd "$SCRATCH_REPO" && git add -A && git commit -q -m init )
    mkdir -p "$SCRATCH_REPO/$(dirname "$NEW_PATH")"
    ( cd "$SCRATCH_REPO" && git mv "$OLD_PATH" "$NEW_PATH" )
    [[ -n "$SCRATCH" ]] && cp "$SCRATCH" "$SCRATCH_REPO/$NEW_PATH"
    ( cd "$SCRATCH_REPO" && git add -A )
    DIFF=$( cd "$SCRATCH_REPO" && git diff --staged -M --src-prefix=a/ --dst-prefix=b/ )
    ;;
  *)
    usage; exit 1
    ;;
esac

if [[ -z "$DIFF" ]]; then
  echo "ERROR: generated diff is empty — no actual difference" >&2
  exit 1
fi

CHECK_FILE="$(mktemp)"
printf '%s\n' "$DIFF" > "$CHECK_FILE"
if ! git apply --check "$CHECK_FILE" 2>"$CHECK_FILE.err"; then
  echo "ERROR: generated diff does not pass 'git apply --check' — refusing to emit it" >&2
  cat "$CHECK_FILE.err" >&2
  rm -f "$CHECK_FILE.err"
  exit 1
fi
rm -f "$CHECK_FILE.err"

printf '%s\n' "$DIFF"
