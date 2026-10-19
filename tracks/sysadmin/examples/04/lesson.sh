#!/usr/bin/env bash
set -eu
lab=$(mktemp -d)
trap 'rm -f "$lab/report.txt" "$lab/backup.tar" "$lab/restored/report.txt"; rmdir "$lab/restored" "$lab"' EXIT
mkdir "$lab/restored"
printf 'verified\n' > "$lab/report.txt"
tar -cf "$lab/backup.tar" -C "$lab" report.txt
tar -xf "$lab/backup.tar" -C "$lab/restored"
cmp "$lab/report.txt" "$lab/restored/report.txt"
printf 'restore verified\n'
