#!/usr/bin/env bash
set -euo pipefail
allow() { [[ $1 == valid && $2 == valid ]]; }
for pair in 'valid valid' 'valid invalid' 'invalid valid' 'invalid invalid'; do
  read -r first second <<< "$pair"
  if allow "$first" "$second"; then result=allow; else result=deny; fi
  printf '%s+%s=%s\n' "$first" "$second" "$result"
done
