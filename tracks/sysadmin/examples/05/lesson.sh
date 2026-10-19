#!/usr/bin/env bash
set -eu
lab=$(mktemp -d)
trap 'rm -f "$lab/authorized_keys"; rmdir "$lab"' EXIT
chmod 700 "$lab"
printf '# empty teaching fixture\n' > "$lab/authorized_keys"
chmod 600 "$lab/authorized_keys"
stat -c '%a' "$lab"
stat -c '%a' "$lab/authorized_keys"
