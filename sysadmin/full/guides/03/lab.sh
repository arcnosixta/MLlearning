#!/usr/bin/env bash
set -euo pipefail
work=$(mktemp -d)
cleanup() { rm -f -- "$work/original" "$work/second"; rmdir -- "$work"; }
trap cleanup EXIT
printf 'first\n' >"$work/original"
ln -- "$work/original" "$work/second"
printf 'second\n' >>"$work/second"
cmp -- "$work/original" "$work/second"
awk 'END{print "lines=" NR}' "$work/original"
rm -- "$work/second"
if [[ -f "$work/original" ]]; then printf 'original=present\n'; fi
