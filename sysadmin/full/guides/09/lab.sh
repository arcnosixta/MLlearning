#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' '101 1 S' '102 1 R' '103 101 Z' |
  awk '{total++;if($3=="Z") zombies++;if($3=="R") running++} END{print "processes="total;print "runnable="running;print "zombies="zombies}'
