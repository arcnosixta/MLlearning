#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
command -v openssl >/dev/null
base=${TMPDIR:-/tmp}
base=${base%/}
work=$(mktemp -d "$base/sysadmin-tls.XXXXXX")
[[ $work == "$base"/sysadmin-tls.* && -d $work ]] || exit 1
touch "$work/.owned-lab"
cleanup() {
  [[ $work == "$base"/sysadmin-tls.* && -d $work && -f $work/.owned-lab ]] || return 1
  rm -f -- "$work/key.pem" "$work/cert.pem" "$work/.owned-lab"
  rmdir -- "$work"
}
trap cleanup EXIT
# Exclude only the subject from MSYS conversion; temporary file paths still convert.
MSYS2_ARG_CONV_EXCL='/CN=' openssl req -x509 -newkey rsa:2048 -nodes -days 1 \
  -subj '/CN=course.test' -addext 'subjectAltName=DNS:course.test' \
  -keyout "$work/key.pem" -out "$work/cert.pem" >/dev/null 2>&1
openssl verify -CAfile "$work/cert.pem" -verify_hostname course.test "$work/cert.pem" >/dev/null
printf '%s\n' 'trusted=yes'
if openssl verify -CAfile "$work/cert.pem" -verify_hostname other.test "$work/cert.pem" >/dev/null 2>&1; then
  printf '%s\n' 'unexpected hostname acceptance' >&2
  exit 1
fi
printf '%s\n' 'wrong-host=rejected'
