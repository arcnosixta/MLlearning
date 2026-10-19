#!/usr/bin/env bash
set -eu
printf '%s
' 'health=ok' 'backup=verified' 'alert=configured' | awk -F= '$1=="health"&&$2=="ok"{h=1}$1=="backup"&&$2=="verified"{b=1}$1=="alert"&&$2=="configured"{a=1}END{if(h&&b&&a)print "ready";else{print "incomplete";exit 1}}'
