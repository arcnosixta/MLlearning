#!/usr/bin/env bash
set -eu
printf '%s
' 'used 80' 'limit 100' | awk '$1=="used"{u=$2}$1=="limit"{l=$2}END{if(l>0 && u/l>=0.8)print "warning";else print "ok"}'
