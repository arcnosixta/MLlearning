#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'coreutils|install ok installed|9.0' 'old-demo|deinstall ok config-files|1.0' 'bash|install ok installed|5.2' |
  awk -F'|' '$2=="install ok installed"{print $1 "=" $3; count++} END{print "installed=" count}'
