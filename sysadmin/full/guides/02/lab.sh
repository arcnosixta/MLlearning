#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' java linux java | sort | uniq -c | awk '{print $2 "=" $1}'
set +e
(set -o pipefail; false | cat >/dev/null)
result=$?
set -e
printf 'pipeline=%s\n' "$result"
