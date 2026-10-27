#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
fixture=$'group,grade\nA,80\nB,90\nA,100'
printf '%s\n' "$fixture" | awk -F, '
NR == 1 { next }
{ total[$1] += $2; count[$1]++ }
END {
  for (group in count)
    printf "%s count=%d average=%.1f\n", group, count[group], total[group] / count[group]
}' | sort
