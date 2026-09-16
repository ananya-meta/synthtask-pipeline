#!/bin/sh
# Hourly sweep driver. Kept dumb on purpose: every policy decision lives in
# `synthtask sweep`, so this only fixes up the environment cron does not provide
# and keeps the log from growing without bound.
set -u

here=$(dirname "$(readlink -f "$0")")
repo=$(dirname "$here")
log=${SYNTHTASK_SWEEP_LOG:-$HOME/logs/synthtask-sweep.log}
max_bytes=${SYNTHTASK_SWEEP_LOG_MAX:-5242880}

# cron starts from a near-empty environment; codimango lives under ~/.local/bin.
PATH="$HOME/.local/bin:/usr/local/bin:/usr/bin:/bin"
export PATH

mkdir -p "$(dirname "$log")"
if [ -f "$log" ] && [ "$(wc -c < "$log")" -gt "$max_bytes" ]; then
    mv -f "$log" "$log.1"
fi

"$repo/bin/synthtask" sweep "$@" >>"$log" 2>&1
status=$?

if [ "$status" -ne 0 ]; then
    printf '%s sweep exited %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$status" >>"$log"
fi

exit "$status"
