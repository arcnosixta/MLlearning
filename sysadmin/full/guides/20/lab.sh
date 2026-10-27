#!/usr/bin/env bash
set -euo pipefail
sum() {
  local total=0 value
  for value in "$@"; do total=$((total + value)); done
  printf '%s\n' "$total"
}
contains() {
  local wanted=$1 value
  shift
  for value in "$@"; do [[ $value == "$wanted" ]] && return 0; done
  return 1
}
amounts=(2 3 5)
items=("" "two words" "last")
printf 'sum=%s\n' "$(sum "${amounts[@]}")"
printf 'items=%s\n' "${#items[@]}"
if contains "two words" "${items[@]}"; then printf 'found=yes\n'; fi
