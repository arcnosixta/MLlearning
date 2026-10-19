#!/usr/bin/env bash
set -eu
# Offline fixture, not the actual capacity of this host.
used_percent=72
threshold=80
if [ "$used_percent" -ge "$threshold" ]; then
    printf 'ALERT\n'
    exit 1
fi
printf 'OK\n'
