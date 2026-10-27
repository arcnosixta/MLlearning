#!/usr/bin/env bash
set -euo pipefail
policy() {
  local source=$1 port=$2 state=$3
  if [[ $state == ESTABLISHED || $state == RELATED ]]; then printf 'ACCEPT';
  elif [[ $source == 192.0.2.10 && $port == 22 && $state == NEW ]]; then printf 'ACCEPT';
  else printf 'DROP'; fi
}
printf 'admin-new=%s\n' "$(policy 192.0.2.10 22 NEW)"
printf 'other-new=%s\n' "$(policy 192.0.2.11 22 NEW)"
printf 'reply=%s\n' "$(policy 192.0.2.11 443 ESTABLISHED)"
