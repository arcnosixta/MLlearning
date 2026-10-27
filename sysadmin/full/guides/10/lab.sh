#!/usr/bin/env bash
set -euo pipefail
address=$(((192 << 24) | (0 << 16) | (2 << 8) | 77))
mask=$((0xffffff00)); network=$((address & mask))
printf 'network=%d.%d.%d.%d/24\n' "$(((network >> 24) & 255))" "$(((network >> 16) & 255))" "$(((network >> 8) & 255))" "$((network & 255))"
printf 'host-part=%d\n' "$((address & 255))"
