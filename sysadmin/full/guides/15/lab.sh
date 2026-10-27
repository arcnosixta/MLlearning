#!/usr/bin/env bash
set -euo pipefail
decision() {
  local dac=$1 mac=$2 result=deny
  if [[ $dac == allow && $mac == allow ]]; then result=allow; fi
  printf 'dac=%s mac=%s result=%s\n' "$dac" "$mac" "$result"
}
decision allow allow
decision allow deny
decision deny allow
