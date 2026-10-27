#!/usr/bin/env bash
set -euo pipefail
declare -A ready=([database]=1 [cache]=1 [application]=0)
if [[ ${ready[database]} -eq 1 && ${ready[cache]} -eq 1 ]]; then ready[application]=1; fi
printf 'application=%s\n' "${ready[application]}"
ready[database]=0
if [[ ${ready[database]} -eq 0 ]]; then printf 'acceptance=blocked\n'; fi
