#!/usr/bin/env bash
#
# Set up the local development environment for the first time (or after a
# fresh clone). Installs client dependencies, links sibling repos that are
# cloned alongside this one, brings up the backend services in Docker, and
# initialises the database on first run.
#
# Expected layout: this repo (superdesk/) is cloned alongside its siblings
# under a single parent directory, e.g.
#
#   ~/code/
#     superdesk/                  <-- you are here
#     superdesk-client-core/
#     superdesk-planning/
#     superdesk-analytics/        (optional)
#     superdesk-publisher/        (optional)
#
# Usage:
#   ./setup.sh                       # auto-discover all siblings
#   ./setup.sh --only NAME[,NAME]    # link only these (exact directory names)
#   ./setup.sh --skip NAME[,NAME]    # link all except these
#   ./setup.sh --link /abs/path      # explicitly link a path (repeatable)
#   ./setup.sh --reinit              # force first-run DB init even if already done
#
# Prerequisites (validated by this script):
#   * Docker Desktop installed and running.
#   * Volta installed (Node version is pinned via Volta).
#   * Sibling repos cloned in the parent directory of this one.

set -euo pipefail

ONLY=""
SKIP=""
EXPLICIT_LINKS=()
REINIT=false

while [ $# -gt 0 ]; do
    case "$1" in
        --only)    ONLY="$2"; shift 2 ;;
        --skip)    SKIP="$2"; shift 2 ;;
        --link)    EXPLICIT_LINKS+=("$2"); shift 2 ;;
        --reinit)  REINIT=true; shift ;;
        *) echo "unknown argument: $1" >&2; exit 2 ;;
    esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PARENT_DIR="$(cd "$REPO_ROOT/.." && pwd)"
CLIENT_DIR="$REPO_ROOT/client"
COMPOSE_FILE="$REPO_ROOT/docker-compose.dev.yml"
RUN_DIR="$SCRIPT_DIR/.run"
SETUP_SENTINEL="$RUN_DIR/.setup-done"

# Resolve the host port the server binds to. Default 5000 (matches
# upstream Superdesk). On macOS, auto-override to 5001 because :5000 is
# reserved for AirPlay Receiver, which silently answers HTTP and would
# mask a missing server. Explicit SUPERDESK_PORT in the environment
# overrides both defaults.
if [ -n "${SUPERDESK_PORT:-}" ]; then
    SERVER_PORT="$SUPERDESK_PORT"
elif [ "$(uname -s)" = "Darwin" ]; then
    SERVER_PORT=5001
else
    SERVER_PORT=5000
fi
SERVER_URL="http://localhost:${SERVER_PORT}/api/"
# Export so docker compose substitution sees them and any child process
# (like grunt during up.sh) inherits the right URL — overriding any stale
# value the user may have in their shell.
export SUPERDESK_PORT="$SERVER_PORT"
export SUPERDESK_URL="${SERVER_URL%/}"

ADMIN_USER="admin"
ADMIN_PASS="admin"
ADMIN_EMAIL="admin@example.com"

# Siblings the host links. The first two are REQUIRED — the host can't
# run meaningfully without them. The rest are optional and skipped
# silently if not cloned.
REQUIRED_SIBLINGS=(
    "superdesk-client-core"
    "superdesk-planning"
)
OPTIONAL_SIBLINGS=(
    "superdesk-analytics"
    "superdesk-publisher"
)
KNOWN_SIBLINGS=("${REQUIRED_SIBLINGS[@]}" "${OPTIONAL_SIBLINGS[@]}")

mkdir -p "$RUN_DIR"

log()  { printf '\n[dev-setup] %s\n' "$*"; }
fail() { printf '\n[dev-setup] ERROR: %s\n' "$*" >&2; exit 1; }

server_reachable() {
    # Any 2xx / 401 / 403 means "something is answering on this port that
    # *looks like* a working HTTP service" — good enough as a readiness
    # signal. Connection refused, timeouts, and 5xx are treated as "not
    # up yet" and the wait-loop keeps polling.
    #
    # Caveat: this does NOT distinguish a real Superdesk server from
    # another HTTP service that happens to answer on the same port (e.g.
    # macOS AirPlay Receiver on :5000 returns 200). We accept that risk
    # because the script's default port choice (5000 on Linux, 5001 on
    # macOS) avoids the known collision; a user overriding
    # SUPERDESK_PORT=5000 on macOS is explicitly opting in.
    local status
    status=$(curl -sS -o /dev/null -w '%{http_code}' --max-time 2 "$1" 2>/dev/null) || return 1
    case "$status" in
        2??|401|403) return 0 ;;
        *) return 1 ;;
    esac
}

# Comma-separated list contains a value? (helper for --only / --skip).
csv_contains() {
    local csv="$1" needle="$2"
    [ -z "$csv" ] && return 1
    case ",$csv," in *",$needle,"*) return 0 ;; esac
    return 1
}

# ---- Prerequisite checks ----

[ -f "$COMPOSE_FILE" ] || fail "$COMPOSE_FILE not found — run this from inside the superdesk/ host repo."
[ -d "$CLIENT_DIR" ]  || fail "$CLIENT_DIR not found — run this from inside the superdesk/ host repo."

command -v docker > /dev/null || fail "Docker is not installed. Install Docker Desktop first."
docker info > /dev/null 2>&1 || fail "Docker is installed but not running. Start Docker Desktop and try again."

# Surface the port choice so the user knows where to expect the server.
log "backend will publish on host port $SERVER_PORT (server URL: $SERVER_URL)"
case "$SERVER_PORT" in
    5001) log "  (auto-picked 5001 on macOS to avoid AirPlay Receiver on :5000)" ;;
esac

command -v volta > /dev/null || fail "Volta is not installed. See https://volta.sh — Node version is pinned through it."
command -v curl  > /dev/null || fail "curl is not installed."

# ---- Discover siblings ----

log "discovering sibling repos under $PARENT_DIR"

declare -a TO_LINK=()
declare -a SUMMARY_FOUND=()
declare -a SUMMARY_MISSING=()
declare -a SUMMARY_SKIPPED=()

for name in "${KNOWN_SIBLINGS[@]}"; do
    path="$PARENT_DIR/$name"
    if [ ! -d "$path" ]; then
        SUMMARY_MISSING+=("$name")
        continue
    fi
    if [ -n "$ONLY" ] && ! csv_contains "$ONLY" "$name"; then
        SUMMARY_SKIPPED+=("$name (not in --only)")
        continue
    fi
    if [ -n "$SKIP" ] && csv_contains "$SKIP" "$name"; then
        SUMMARY_SKIPPED+=("$name (in --skip)")
        continue
    fi
    TO_LINK+=("$path")
    SUMMARY_FOUND+=("$name")
done

# Add explicit --link paths. Warn if they're outside the parent dir.
for path in "${EXPLICIT_LINKS[@]+"${EXPLICIT_LINKS[@]}"}"; do
    if [ ! -d "$path" ]; then
        fail "--link path does not exist: $path"
    fi
    if [ ! -f "$path/package.json" ]; then
        fail "--link path has no package.json: $path"
    fi
    abs_path="$(cd "$path" && pwd)"
    if [ "$(dirname "$abs_path")" != "$PARENT_DIR" ]; then
        log "WARNING: --link path is outside the sibling parent ($PARENT_DIR):"
        log "  $abs_path"
        log "Linking it anyway (you passed --link explicitly)."
    fi
    TO_LINK+=("$abs_path")
    SUMMARY_FOUND+=("$(basename "$abs_path") (via --link)")
done

# Print the summary.
log "link summary:"
if [ "${#SUMMARY_FOUND[@]}" -gt 0 ]; then
    printf '  found and will link:\n'
    for s in "${SUMMARY_FOUND[@]}"; do printf '    - %s\n' "$s"; done
fi
if [ "${#SUMMARY_MISSING[@]}" -gt 0 ]; then
    printf '  not present (skipped):\n'
    for s in "${SUMMARY_MISSING[@]}"; do printf '    - %s\n' "$s"; done
fi
if [ "${#SUMMARY_SKIPPED[@]}" -gt 0 ]; then
    printf '  excluded by flags:\n'
    for s in "${SUMMARY_SKIPPED[@]}"; do printf '    - %s\n' "$s"; done
fi

# Refuse to proceed if any required sibling is not being linked. Without
# them the host can't run meaningfully.
missing_required=()
for req in "${REQUIRED_SIBLINGS[@]}"; do
    if ! printf '%s\n' "${TO_LINK[@]:-}" | grep -qE "/${req}\$"; then
        missing_required+=("$req")
    fi
done

if [ "${#missing_required[@]}" -gt 0 ]; then
    cat >&2 <<EOF

[dev-setup] ERROR: Required sibling repo(s) are missing.

[dev-setup] These must be cloned as siblings of this repo (in
[dev-setup] $PARENT_DIR/):

EOF
    for m in "${missing_required[@]}"; do
        echo "[dev-setup]   - $m" >&2
    done
    cat >&2 <<EOF

[dev-setup] To clone them, from $PARENT_DIR:

EOF
    for m in "${missing_required[@]}"; do
        echo "[dev-setup]   git clone https://github.com/superdesk/$m.git" >&2
    done
    cat >&2 <<EOF

[dev-setup] Then re-run this script.

[dev-setup] If you intentionally excluded one via --skip, this script
[dev-setup] refuses to proceed — both superdesk-client-core and
[dev-setup] superdesk-planning are required.

EOF
    exit 1
fi

# ---- 1. Install host client deps ----

log "installing client dependencies in $CLIENT_DIR (this is the slow step on a cold cache)"
(cd "$CLIENT_DIR" && npm install)

# ---- 2. dev-link sibling repos ----

log "running dev-link against ${#TO_LINK[@]} sibling(s)"
(cd "$CLIENT_DIR" && npm run devlink -- "${TO_LINK[@]}")

# ---- 3. Bring up backend services ----

log "starting backend services via docker compose"
(cd "$REPO_ROOT" && docker compose -f "$COMPOSE_FILE" up -d)

log "waiting for server at $SERVER_URL (cold start can take ~60s)"
elapsed=0
until server_reachable "$SERVER_URL"; do
    if [ "$elapsed" -ge 300 ]; then
        fail "server didn't come up within 5 minutes — check 'docker compose -f docker-compose.dev.yml logs superdesk-server'"
    fi
    sleep 3
    elapsed=$((elapsed + 3))
done
log "server reachable at $SERVER_URL"

# ---- 4. First-run DB init ----

if [ "$REINIT" = true ] || [ ! -f "$SETUP_SENTINEL" ]; then
    log "running first-run DB init (app:initialize_data + users:create admin/admin)"
    (cd "$REPO_ROOT" && docker compose -f "$COMPOSE_FILE" exec -T superdesk-server \
        python manage.py app:initialize_data) || fail "app:initialize_data failed — see compose logs"
    (cd "$REPO_ROOT" && docker compose -f "$COMPOSE_FILE" exec -T superdesk-server \
        python manage.py users:create -u "$ADMIN_USER" -p "$ADMIN_PASS" -e "$ADMIN_EMAIL" --admin) || true
        # users:create returns non-zero if the user already exists; that's
        # fine if --reinit was passed against an existing DB.
    touch "$SETUP_SENTINEL"
    log "DB initialised. Admin user: $ADMIN_USER / $ADMIN_PASS"
else
    log "DB already initialised (sentinel at $SETUP_SENTINEL); skipping init"
    log "Pass --reinit to force re-running app:initialize_data + users:create."
fi

log "setup complete"
log ""
log "  backend running on $SERVER_URL"
log "  start the client dev server with: ./scripts/dev/up.sh"
log "  stop everything with:             ./scripts/dev/down.sh"
