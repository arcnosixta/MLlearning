#!/usr/bin/env bash
set -euo pipefail
fail_step() { return 5; }
if fail_step; then
  printf 'unexpected-success\n'
  exit 1
else
  code=$?
  printf 'explicit-status=%s\n' "$code"
fi
if false | true; then
  printf 'pipeline=missed\n'
  exit 1
else
  printf 'pipeline=detected\n'
fi
if diagnostic=$(bash -u -c 'unset lab_missing; printf "%s" "$lab_missing"' 2>&1); then
  printf 'nounset=missed\n'
  exit 1
else
  [[ $diagnostic == *lab_missing* ]]
  printf 'nounset=detected\n'
fi
