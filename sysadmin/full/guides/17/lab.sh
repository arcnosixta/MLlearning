#!/usr/bin/env bash
set -euo pipefail
data=$'Aida,91\nArman,59\nDana,75'
passed=0
while IFS=, read -r name grade; do
  [[ $grade =~ ^[0-9]{1,3}$ ]]
  value=$((10#$grade))
  (( value <= 100 ))
  if (( value >= 60 )); then
    result=pass
    passed=$((passed + 1))
  else
    result=retry
  fi
  printf '%s:%s\n' "$name" "$result"
done <<< "$data"
printf 'passed=%s\n' "$passed"
