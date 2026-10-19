#!/usr/bin/env bash
set -eu
printf '%s
' 200 500 200 503 | awk '{n++; if($1>=500)e++} END {printf "errors=%d total=%d
",e,n}'
