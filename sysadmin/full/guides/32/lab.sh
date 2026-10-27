#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
printf '%s\n' 'alice 2001' 'bob 2002' 'legacy-alice 2001' |
awk '{if($2 in owner && owner[$2]!=$1) print "uid-conflict=" $2 ":" owner[$2] "," $1; else owner[$2]=$1}'
printf '%s\n' 'alice operators' 'bob readers' |
awk '$2=="operators" {print "operator=" $1}'
