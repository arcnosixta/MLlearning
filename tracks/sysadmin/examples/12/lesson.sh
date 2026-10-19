#!/usr/bin/env bash
set -eu
lab=$(mktemp -d)
trap 'rm -f "$lab/source" "$lab/restored"; rmdir "$lab"' EXIT
printf 'lesson-data
' > "$lab/source"
cp "$lab/source" "$lab/restored"
cmp "$lab/source" "$lab/restored"
printf 'restore verified
'
