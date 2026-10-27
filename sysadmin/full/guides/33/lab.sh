#!/usr/bin/env bash
set -euo pipefail
capacity=100
tokens=$capacity
refill=50
previous=0
accepted=0
dropped=0
while read -r time size; do
  tokens=$((tokens + (time - previous) * refill))
  ((tokens <= capacity)) || tokens=$capacity
  previous=$time
  if ((size <= tokens)); then tokens=$((tokens - size)); accepted=$((accepted + 1));
  else dropped=$((dropped + 1)); fi
done <<'EVENTS'
0 80
0 80
1 20
EVENTS
printf 'accepted=%s\ndropped=%s\ntokens=%s\n' "$accepted" "$dropped" "$tokens"
