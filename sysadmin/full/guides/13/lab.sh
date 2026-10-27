#!/usr/bin/env bash
set -euo pipefail
config=$'Host lab-server\n  HostName 192.0.2.10\n  User trainee\n  StrictHostKeyChecking yes\nHost lab-backup\n  HostName 192.0.2.11\n  User trainee\n'
hosts=0
strict=no
while read -r key value; do
  case "$key" in
    Host) hosts=$((hosts + 1)) ;;
    StrictHostKeyChecking) strict=$value ;;
  esac
done <<< "$config"
[[ $hosts == 2 && $strict == yes ]]
printf 'hosts=%s\nstrict-host-checking=%s\n' "$hosts" "$strict"
