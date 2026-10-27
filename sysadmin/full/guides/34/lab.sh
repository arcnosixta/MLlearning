#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
awk '
  $1=="FROM" {print "base=" $2}
  $1=="USER" {user=$2}
  $1=="CMD" && index($0,"[") {execform=1}
  END {print "user=" user; print "exec-command=" (execform ? "yes" : "no"); if(user=="" || user=="root" || !execform) exit 1}
' <<'DOCKERFILE'
FROM example/runtime@sha256:demo-fixture
WORKDIR /app
COPY app /app/app
USER 10001
CMD ["/app/app"]
DOCKERFILE
