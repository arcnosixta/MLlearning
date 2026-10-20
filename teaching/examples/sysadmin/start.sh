#!/usr/bin/env bash
set -eu
lab=$(mktemp -d)
trap 'rm -f "$lab/note.txt"; rmdir "$lab"' EXIT
printf 'hello
' > "$lab/note.txt"
cat "$lab/note.txt"
