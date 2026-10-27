#!/usr/bin/env bash
set -euo pipefail
(exit 7) &
worker=$!
if wait "$worker"; then
  status=0
else
  status=$?
fi
printf 'worker-status=%s\n' "$status"
signal_count=0
trap 'signal_count=$((signal_count + 1))' USR1
kill -s USR1 "$BASHPID"
printf 'handled-signals=%s\n' "$signal_count"
trap - USR1
