#!/usr/bin/env bash
set -euo pipefail
inventory=$'server|192.0.2.10|internal\nclient|192.0.2.20|internal'
printf '%s\n' "$inventory" | awk -F'|' 'NF!=3 {exit 1} {if(names[$1]++ || ips[$2]++) exit 2; count++} END {if(count!=2) exit 3; print "machines="count}'
printf '%s\n' "$inventory" | awk -F'|' '$3=="internal"{count++} END{print "isolated="count}'
