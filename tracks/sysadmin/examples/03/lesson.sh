#!/usr/bin/env bash
set -eu
# Offline fixture: this does not perform real DNS resolution.
printf '%s\n' '127.0.0.1 localhost' '192.0.2.10 demo.example' |
    awk '$2 == "localhost" { print $1 }'
