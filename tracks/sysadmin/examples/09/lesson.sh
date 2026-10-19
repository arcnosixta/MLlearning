#!/usr/bin/env bash
set -eu
spec='image=app:1.0
storage=volume
memory=256m'
printf '%s
' "$spec" | awk -F= '$1=="storage" {print $2}'
