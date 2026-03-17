#!/bin/sh
set -e

aquifer meter poll --record --watch &
POLL_PID=$!

# If the poller exits unexpectedly, stop the container
( wait "$POLL_PID"; kill -TERM $$ ) &

aquifer dashboard --host 0.0.0.0
