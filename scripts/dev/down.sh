#!/usr/bin/env bash
#
# Tear down the local development stack started by up.sh: kill the grunt
# server on :9000 and stop the docker compose backend.
#
# Usage:
#   ./down.sh             # stop services (data preserved in named volumes)
#   ./down.sh --volumes   # also drop named volumes (NUCLEAR: wipes DB state)
#
# Always exits 0 even if some pieces were already stopped. Idempotent.
#
# Note: stopping the compose stack does NOT stop Docker Desktop itself.
# This script prints a reminder at the end — designers need to quit Docker
# Desktop manually to fully free RAM/battery.

set -euo pipefail

VOLUMES=false

for arg in "$@"; do
    case "$arg" in
        --volumes) VOLUMES=true ;;
        *) echo "unknown argument: $arg" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker-compose.dev.yml"
RUN_DIR="$SCRIPT_DIR/.run"
GRUNT_PIDFILE="$RUN_DIR/grunt-server.pid"
SETUP_SENTINEL="$RUN_DIR/.setup-done"

log() { printf '\n[dev-down] %s\n' "$*"; }

# 1. Grunt server. Prefer the pidfile; fall back to lsof on the port if the
# pidfile is missing or stale (e.g. up.sh was started in another shell or
# the pidfile got nuked).
if [ -f "$GRUNT_PIDFILE" ]; then
    grunt_pid="$(cat "$GRUNT_PIDFILE")"
    if kill -0 "$grunt_pid" 2>/dev/null; then
        log "stopping grunt server (pid: $grunt_pid)"
        kill "$grunt_pid" 2>/dev/null || true
        # grunt forks; clean up anything still on :9000 just in case.
        sleep 1
    else
        log "grunt pidfile is stale; removing"
    fi
    rm -f "$GRUNT_PIDFILE"
fi

if command -v lsof > /dev/null; then
    if pids=$(lsof -ti:9000 -sTCP:LISTEN 2>/dev/null); then
        log "stopping leftover processes on :9000 (pids: $pids)"
        kill $pids 2>/dev/null || true
    fi
fi

# 2. Docker compose backend.
if [ -f "$COMPOSE_FILE" ]; then
    if [ "$VOLUMES" = true ]; then
        log "docker compose down -v (volumes removed; DB state dropped)"
        (cd "$REPO_ROOT" && docker compose -f "$COMPOSE_FILE" down -v)
        # The DB is gone; the next setup.sh must re-run init.
        rm -f "$SETUP_SENTINEL"
    else
        log "docker compose stop (data preserved in named volumes)"
        (cd "$REPO_ROOT" && docker compose -f "$COMPOSE_FILE" stop)
    fi
else
    log "$COMPOSE_FILE not found; nothing to stop"
fi

log "services stopped"
log ""
log "Docker Desktop is still running. To fully free RAM/battery, quit it"
log "manually from the menu bar (Cmd-Q on the Docker icon)."
