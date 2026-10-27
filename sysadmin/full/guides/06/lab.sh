#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' '# example port=80' 'port=80' 'host=127.0.0.1' |
  sed 's/^port=80$/port=8080/'
