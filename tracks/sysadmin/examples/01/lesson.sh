#!/usr/bin/env bash
set -eu
lab=$(mktemp -d)
trap 'rm -f "$lab/report.txt"; rmdir "$lab"' EXIT
printf 'lesson\n' > "$lab/report.txt"
chmod 640 "$lab/report.txt"
stat -c '%a' "$lab/report.txt"
