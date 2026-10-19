#!/usr/bin/env bash
set -eu
printf '%s\n' 'INFO ready' 'ERROR timeout' 'INFO retry' 'ERROR denied' |
    awk '$1 == "ERROR" { n++ } END { print n+0 }'
