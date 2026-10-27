#!/usr/bin/env bash
set -euo pipefail
allowed() { [[ "$#" -eq 2 && "$1" == /usr/bin/systemctl && "$2" == 'restart course-demo.service' ]]; }
if allowed /usr/bin/systemctl 'restart course-demo.service'; then printf 'demo=allow\n'; fi
if ! allowed /usr/bin/systemctl 'restart ssh.service'; then printf 'other=deny\n'; fi
if ! allowed /bin/bash root; then printf 'shell=deny\n'; fi
