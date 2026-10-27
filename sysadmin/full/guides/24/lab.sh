#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
accepted=0
for value in CSC-101 CSC-10 XCSC-101 CSC-101x; do
  if grep -Eq '^[A-Z]{3}-[0-9]{3}$' <<< "$value"; then
    printf 'accepted:%s\n' "$value"
    accepted=$((accepted + 1))
  fi
done
printf 'accepted-count=%s\n' "$accepted"
