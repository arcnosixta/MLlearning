#!/usr/bin/env bash
set -euo pipefail
lab_base=${TMPDIR:-/tmp}
lab_base=${lab_base%/}
lab_dir=$(mktemp -d "$lab_base/im-sysadmin-18.XXXXXX")
case "$lab_dir" in "$lab_base"/im-sysadmin-18.*) ;; *) exit 2 ;; esac
cleanup() {
  exec 3<&-
  rm -f -- "$lab_dir/data.txt" "$lab_dir/error.txt"
  rmdir -- "$lab_dir"
}
trap cleanup EXIT
emit() { printf 'result=42\n'; printf 'notice=checked\n' >&2; }
emit > "$lab_dir/data.txt" 2> "$lab_dir/error.txt"
exec 3< "$lab_dir/data.txt"
IFS= read -r line <&3
printf 'stdout:%s\n' "$line"
IFS= read -r line < "$lab_dir/error.txt"
printf 'stderr:%s\n' "$line"
