#!/usr/bin/env bash
set -euo pipefail
disks=4
disk_gib=10
printf 'raid0=%s GiB\n' "$((disks * disk_gib))"
printf 'raid1=%s GiB\n' "$disk_gib"
printf 'raid5=%s GiB\n' "$(((disks - 1) * disk_gib))"
vg_extents=100
first_lv=40
second_lv=35
free=$((vg_extents - first_lv - second_lv))
((free >= 0))
printf 'vg-free=%s extents\n' "$free"
requested=30
if ((requested > free)); then printf '%s\n' 'allocation=rejected'; else printf '%s\n' 'allocation=accepted'; fi
