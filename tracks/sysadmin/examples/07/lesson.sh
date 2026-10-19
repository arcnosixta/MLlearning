#!/usr/bin/env bash
set -eu
unit='[Unit]
Description=Teaching report
[Service]
Type=oneshot
ExecStart=/usr/bin/true'
printf '%s
' "$unit" | awk -F= '$1=="Type" {print $2}'
