#!/usr/bin/env bash
# Generate a fresh RSA keypair for MACRO_API_TOKEN_{PRIVATE_SECRET,PUBLIC}_KEY
# and print two ready-to-use dotenv lines (double-quoted, newlines escaped as
# literal \n — dotenvy's multiline-in-double-quotes convention, matching how
# the repo's own xtask writes these files).
#
# These are parsed as real PEM by jsonwebtoken's RS256 encode/decode
# (crates/macro_auth/src/middleware/decode_jwt.rs), so a plain placeholder
# string boots the service but panics the first time a token is actually
# signed or verified — must be real, just doesn't need to be secret since
# this never leaves localhost.
#
# Usage: generate_jwt_keypair.sh >> local.env
set -euo pipefail

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

openssl genrsa -out "$tmpdir/private.pem" 2048 2>/dev/null
openssl rsa -in "$tmpdir/private.pem" -pubout -out "$tmpdir/public.pem" 2>/dev/null

escape_pem() {
  # Join lines with literal \n, strip the resulting trailing \n
  python3 -c "
import sys
content = open(sys.argv[1]).read().strip()
print(content.replace(chr(10), '\\\\n'))
" "$1"
}

priv_escaped=$(escape_pem "$tmpdir/private.pem")
pub_escaped=$(escape_pem "$tmpdir/public.pem")

echo "MACRO_API_TOKEN_PRIVATE_SECRET_KEY=\"${priv_escaped}\""
echo "MACRO_API_TOKEN_PUBLIC_KEY=\"${pub_escaped}\""
