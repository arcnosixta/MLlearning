#!/usr/bin/env bash
set -eu
printf '%s
' '22 allow' '80 allow' '3306 deny' | awk '$2=="allow" {print $1}'
