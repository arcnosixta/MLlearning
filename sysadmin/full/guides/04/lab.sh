#!/usr/bin/env bash
set -euo pipefail
record='UUID=demo-data /srv/data ext4 defaults,nosuid,nodev 0 2'
printf '%s\n' "$record" | awk 'NF!=6{exit 1} {print "mountpoint=" $2; print "filesystem=" $3; if($4 ~ /nosuid/ && $4 ~ /nodev/) print "barriers=2"; else exit 2}'
