#!/usr/bin/env bash
set -euo pipefail
matches_policy() { [[ $1 == 10.10.0.0/24 && $2 == 10.20.0.0/24 ]]; }
for pair in '10.10.0.0/24 10.20.0.0/24' '10.10.0.0/24 10.30.0.0/24'; do
  read -r source destination <<< "$pair"
  if matches_policy "$source" "$destination"; then result=protected; else result=outside-policy; fi
  printf '%s -> %s: %s\n' "$source" "$destination" "$result"
done
