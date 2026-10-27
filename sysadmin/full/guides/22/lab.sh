#!/usr/bin/env bash
set -euo pipefail
fixture=$'# comment\nport=22\nname=lab'
printf '%s\n' "$fixture" | sed -e '/^#/d' -e 's/^port=22$/port=2222/'
printf 'selected:\n'
printf '%s\n' "$fixture" | sed -n '2p'
