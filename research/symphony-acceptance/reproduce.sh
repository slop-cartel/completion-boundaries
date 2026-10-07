#!/usr/bin/env bash
set -euo pipefail
HERE=$(cd -- "$(dirname -- "$0")" && pwd)
BIN="$HERE/../_sandbox/bin/symphony-v0.0.3-linux_x86_64"
mkdir -p "$(dirname -- "$BIN")"
URL=https://github.com/openai/symphony/releases/download/v0.0.3
if [ ! -f "$BIN" ]; then curl -fLsS "$URL/$(basename -- "$BIN")" -o "$BIN"; fi
# Pin the observed released binary, not a mutable latest release.
EXPECTED=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["sha256"])' "$HERE/sources/executable.json")
printf '%s  %s\n' "$EXPECTED" "$BIN" | sha256sum --check
chmod +x "$BIN"
exec python3 "$HERE/probe.py" --binary "$BIN" "$@"
