#!/usr/bin/env bash
set -euo pipefail
active=no
enabled=no
unit_action() {
  case "$1" in
    start) active=yes ;;
    stop) active=no ;;
    enable) enabled=yes ;;
    disable) enabled=no ;;
    *) return 2 ;;
  esac
}
unit_action enable
printf 'after-enable: active=%s enabled=%s\n' "$active" "$enabled"
unit_action start
unit_action disable
printf 'after-disable: active=%s enabled=%s\n' "$active" "$enabled"
unit_action stop
printf 'after-stop: active=%s enabled=%s\n' "$active" "$enabled"
