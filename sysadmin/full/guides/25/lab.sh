#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
printf '%s\n' '192.0.2.10 failed' '192.0.2.11 success' '192.0.2.10 failed' '192.0.2.12 failed' |
awk '$2=="failed" {count[$1]++} END {for(ip in count) if(count[ip]>=2) print ip, count[ip]}' |
sort
printf '%s\n' 'mode=offline-fixture'
