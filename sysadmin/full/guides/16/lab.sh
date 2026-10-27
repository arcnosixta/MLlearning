#!/usr/bin/env bash
set -euo pipefail
lab_base=${TMPDIR:-/tmp}
lab_base=${lab_base%/}
lab_dir=$(mktemp -d "$lab_base/im-sysadmin-16.XXXXXX")
case "$lab_dir" in "$lab_base"/im-sysadmin-16.*) ;; *) exit 2 ;; esac
cleanup() {
  rm -f -- "$lab_dir/source.csv" "$lab_dir/backup.csv" "$lab_dir/restored.csv"
  rmdir -- "$lab_dir"
}
trap cleanup EXIT
printf '1,80\n2,90\n' > "$lab_dir/source.csv"
cp -- "$lab_dir/source.csv" "$lab_dir/backup.csv"
printf 'broken\n' > "$lab_dir/source.csv"
cp -- "$lab_dir/backup.csv" "$lab_dir/restored.csv"
cmp -s -- "$lab_dir/backup.csv" "$lab_dir/restored.csv"
rows=0
total=0
while IFS=, read -r ident grade; do
  [[ $ident =~ ^[0-9]+$ && $grade =~ ^[0-9]+$ ]]
  rows=$((rows + 1))
  total=$((total + grade))
done < "$lab_dir/restored.csv"
printf 'restore=identical\nrows=%s\ngrade-total=%s\n' "$rows" "$total"
