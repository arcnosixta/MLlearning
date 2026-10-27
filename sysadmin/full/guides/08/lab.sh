#!/usr/bin/env bash
set -euo pipefail
mode=$((8#640))
printf 'owner=%d\n' "$(((mode >> 6) & 7))"
printf 'group=%d\n' "$(((mode >> 3) & 7))"
printf 'other=%d\n' "$((mode & 7))"
requested=$((8#666)); mask=$((8#027))
printf 'new-file=%03o\n' "$((requested & ~mask & 8#777))"
