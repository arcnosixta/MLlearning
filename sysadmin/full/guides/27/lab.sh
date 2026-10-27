#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
printf '%s\n' 'call-a INVITE' 'call-a ANSWER' 'call-b INVITE' 'call-a BYE' |
awk '{if($2=="INVITE") state[$1]="ringing"; else if($2=="ANSWER") state[$1]="active"; else if($2=="BYE") state[$1]="ended"} END {for(id in state) print id, state[id]}' |
sort
