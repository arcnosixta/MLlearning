#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk '
  $1=="SYSCALL" {user[$2]=$3; effective[$2]=$4; result[$2]=$5}
  $1=="PATH" {path[$2]=$3}
  END {for(id in user) print "event=" id, "auid=" user[id], "euid=" effective[id], "success=" result[id], "path=" path[id]}
' <<'AUDIT' | sort
SYSCALL 42 1001 0 yes
PATH 42 /srv/course/report.txt
SYSCALL 43 1002 1002 no
PATH 43 /srv/course/config.txt
AUDIT
