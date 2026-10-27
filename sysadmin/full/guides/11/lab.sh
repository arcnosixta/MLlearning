#!/usr/bin/env bash
set -euo pipefail
printf '%s\n' 'lab.test. SOA ns.lab.test.' 'lab.test. NS ns.lab.test.' 'ns.lab.test. A 192.0.2.10' 'client.lab.test. A 192.0.2.20' |
  awk '$2=="SOA"{soa++} $2=="NS"{ns++} $2=="A"{addresses++} END{if(soa!=1 || ns<1)exit 1;print "soa="soa;print "nameservers="ns;print "addresses="addresses}'
