#!/bin/sh
set -eu
capture_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec python3 "$capture_dir/capture.py" --spec "$capture_dir/capture.json" "$@"
