#!/usr/bin/env bash
#
# Bring up the local development stack: backend services in Docker, client
# dev server (grunt watch) on the host. Mirrors the workflow B path from
# DEVSETUP.md, with idempotence and health checks.
#
# Usage:
#   ./up.sh                    # bring up the stack
#   ./up.sh --rebuild-server   # force `docker compose build` for the server
#
# Exits 0 only when both the server (URL printed in the "ready" banner)
# and the client (http://localhost:9000/) respond. Otherwise exits non-zero
# with a clear error.
#
# Prerequisites (validate before calling this script — usually setup.sh):
#   * Docker Desktop running.
#   * Volta installed (Node version is pinned via package.json).
#   * `npm install` has been run in ./client at least once.

set -euo pipefail

REBUILD_SERVER=false

for arg in "$@"; do
    case "$arg" in
        --rebuild-server) REBUILD_SERVER=true ;;
        *) echo "unknown argument: $arg" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CLIENT_DIR="$REPO_ROOT/client"
COMPOSE_FILE="$REPO_ROOT/docker-compose.dev.yml"
RUN_DIR="$SCRIPT_DIR/.run"
GRUNT_PIDFILE="$RUN_DIR/grunt-server.pid"
GRUNT_LOGFILE="$RUN_DIR/grunt-server.log"

# Resolve the host port the server binds to. Same logic as setup.sh:
# default 5000, macOS → 5001 (AirPlay), explicit SUPERDESK_PORT overrides.
if [ -n "${SUPERDESK_PORT:-}" ]; then
    SERVER_PORT="$SUPERDESK_PORT"
elif [ "$(uname -s)" = "Darwin" ]; then
    SERVER_PORT=5001
else
    SERVER_PORT=5000
fi
SERVER_URL="http://localhost:${SERVER_PORT}/api/"
CLIENT_URL="http://localhost:9000/"

# Export so docker compose substitution sees them and — critically — the
# grunt subshell below inherits SUPERDESK_URL. The client's webpack.config
# reads process.env.SUPERDESK_URL to know where the backend is; without
# this export it falls back to its built-in default (or worse, picks up a
# stale value from the user's shell rc).
export SUPERDESK_PORT="$SERVER_PORT"
export SUPERDESK_URL="${SERVER_URL%/}"

mkdir -p "$RUN_DIR"

log()  { printf '\n[dev-up] %s\n' "$*"; }
fail() { printf '\n[dev-up] ERROR: %s\n' "$*" >&2; exit 1; }

# Reachability helpers.
#
# - `reachable` accepts any HTTP response. Use for the grunt client server,
#   which serves a real page on /.
# - `server_reachable` accepts any 2xx, 401, or 403 — those all mean "a
#   Superdesk server is answering". 5xx, connection refused, and 404 mean
#   "not up yet". The dev server returns 200 on /api/ today; 401/403 are
#   kept in the list in case auth config tightens.
reachable() {
    curl -sS --max-time 2 -o /dev/null "$1" 2>/dev/null
}

server_reachable() {
    local status
    status=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 2 "$1" 2>/dev/null) || return 1
    case "$status" in
        2??|401|403) return 0 ;;
        *) return 1 ;;
    esac
}

wait_until_reachable() {
    local url="$1"
    local name="$2"
    local check_fn="${3:-reachable}"
    local timeout="${4:-240}"
    local log_hint="${5:-}"
    local elapsed=0

    until "$check_fn" "$url"; do
        if [ "$elapsed" -ge "$timeout" ]; then
            local msg="$name not reachable at $url after ${timeout}s"
            [ -n "$log_hint" ] && msg="$msg (check $log_hint)"
            fail "$msg"
        fi
        sleep 2
        elapsed=$((elapsed + 2))
    done

    log "$name reachable at $url"
}

# Preflight: warn (don't fail) if something else is on the published ports.
# The dev stack uses bridge networking, so only the server port and
# 9000 (client) live on the host.
preflight_check_port() {
    local port="$1"
    local name="$2"
    if command -v lsof > /dev/null && lsof -ti:"$port" -sTCP:LISTEN > /dev/null 2>&1; then
        # Skip if our own stack already holds it.
        if [ "$port" = "$SERVER_PORT" ] && docker compose -p superdesk-dev -f "$COMPOSE_FILE" ps -q 2>/dev/null | grep -q .; then
            return 0
        fi
        if [ "$port" = "9000" ] && [ -f "$GRUNT_PIDFILE" ] && kill -0 "$(cat "$GRUNT_PIDFILE")" 2>/dev/null; then
            return 0
        fi
        local pids
        pids=$(lsof -ti:"$port" -sTCP:LISTEN 2>/dev/null)
        cat >&2 <<EOF

[dev-up] WARNING: Something is already listening on port $port ($name).
[dev-up] PIDs: $pids
[dev-up] If this is another Superdesk stack (e.g. e2e), stop it first.
[dev-up] Otherwise the conflict will block our $name.

EOF
        return 1
    fi
    return 0
}

# Sanity checks
[ -f "$COMPOSE_FILE" ] || fail "$COMPOSE_FILE not found — are you in the superdesk/ host repo?"
[ -d "$CLIENT_DIR" ]  || fail "$CLIENT_DIR not found — are you in the superdesk/ host repo?"
[ -d "$CLIENT_DIR/node_modules" ] || fail "Run ./scripts/dev/setup.sh first — client deps aren't installed."

log "backend port: $SERVER_PORT (server URL: $SERVER_URL)"
case "$SERVER_PORT" in
    5001) log "  (auto-picked 5001 on macOS to avoid AirPlay Receiver on :5000)" ;;
esac

# 1. Backend services (Docker)
preflight_check_port "$SERVER_PORT" "superdesk server" || true

if server_reachable "$SERVER_URL"; then
    log "server already reachable; skipping docker bring-up"
else
    log "bringing up backend services via docker compose"
    if [ "$REBUILD_SERVER" = true ]; then
        (cd "$REPO_ROOT" && docker compose -f "$COMPOSE_FILE" build superdesk-server)
    fi
    (cd "$REPO_ROOT" && docker compose -f "$COMPOSE_FILE" up -d)
    wait_until_reachable "$SERVER_URL" "server" server_reachable 240 \
        "docker compose -f docker-compose.dev.yml logs superdesk-server"
fi

# 2. Client dev server (grunt, background)
preflight_check_port 9000 "client dev server" || true

if reachable "$CLIENT_URL"; then
    log "client already reachable; skipping grunt server start"
else
    if [ -f "$GRUNT_PIDFILE" ] && kill -0 "$(cat "$GRUNT_PIDFILE")" 2>/dev/null; then
        log "grunt pidfile is live but $CLIENT_URL isn't responding yet; waiting"
    else
        log "starting grunt server in the background (logs: $GRUNT_LOGFILE)"
        log "  client will point at backend: $SUPERDESK_URL"
        # nohup so the process survives this shell exiting; the pidfile
        # makes it findable for down.sh regardless of who started it.
        # SUPERDESK_URL is set explicitly here as well as exported — the
        # explicit prefix documents the contract and guards against any
        # weird env-inheritance edge case.
        (cd "$CLIENT_DIR" && SUPERDESK_URL="$SUPERDESK_URL" nohup npm run start > "$GRUNT_LOGFILE" 2>&1 & echo $! > "$GRUNT_PIDFILE")
    fi
    # Grunt cold-build is the slow step (~60-120s). Long timeout, error
    # points at the grunt log specifically.
    wait_until_reachable "$CLIENT_URL" "client" reachable 300 "$GRUNT_LOGFILE"

    # The PID stored above was the npm-wrapper subshell, which exits as
    # soon as it forks grunt. Replace it with the actual listener PID so
    # down.sh can find the right process.
    if command -v lsof > /dev/null; then
        if listener_pid=$(lsof -ti:9000 -sTCP:LISTEN 2>/dev/null | head -1); then
            echo "$listener_pid" > "$GRUNT_PIDFILE"
        fi
    fi
fi

log "ready"
log "  server: $SERVER_URL"
log "  client: $CLIENT_URL  (login admin / admin)"
log "  grunt log: $GRUNT_LOGFILE"
log ""
log "Edit files in your sibling checkouts (superdesk-client-core, superdesk-planning)"
log "and grunt's watch will rebuild automatically. To stop: ./scripts/dev/down.sh"
