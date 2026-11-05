#!/usr/bin/env bash
# Seeds the documentation screenshot instance (SDESK-8055) as the `seed:` entry of server/Procfile and keeps
# the database snapshots the screenshot tooling restores through POST /api/restore_record. README.md next to
# this file explains the design.
#
# This process must never exit. Honcho stops every process of the Procfile as soon as one of them ends, and
# systemd then restarts the whole instance in a loop. Every path below therefore finishes in sleep_forever,
# failures included, and an EXIT trap catches anything that slips through (an unbound variable, a typo).

set -u

# Bump to wipe and seed again on a database that was already seeded, for example to pick up new seed data
# from the docs repository.
SEED_VERSION="v1"

# The seed scripts are fetched from the docs repository at run time, so it stays the only copy of the seed
# data. The ref is a branch or tag name (git clone --branch).
DOCS_REPO="${AUTODOCS_DOCS_REPO:-https://github.com/superdesk/superdesk-docs-user-guide.git}"
DOCS_REF="${AUTODOCS_DOCS_REF:-main}"
DOCS_PATH="${AUTODOCS_DOCS_PATH:-tools/screenshots}"

# Honcho gives the first Procfile entry (`rest`) port 5000 and hypercorn_config.py binds to $PORT, so the seed
# talks to the API directly and needs neither the public name nor TLS.
API_URL="${AUTODOCS_API_URL:-http://localhost:5000/api}"

# Both base datasets (the client-core e2e dump and the planning prepopulate profile) come with admin/admin,
# so other credentials only work together with other base data.
SEED_USER="${SUPERDESK_USER:-admin}"
SEED_PASSWORD="${SUPERDESK_PASSWORD:-admin}"

# Names passed to restore_record.
BASE_SNAPSHOT="autodocs-base"
CORE_SNAPSHOT="autodocs"
PLANNING_SNAPSHOT="autodocs-planning"

API_WAIT_SECONDS=900
POLL_SECONDS=10

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SERVER_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
HELPER="$SCRIPT_DIR/snapshots.py"

# The client build installs superdesk-client-core from git, e2e folder included. Its "main" dump is the data
# the screenshot seeds and manifests were written against (users samgamgee and frodobaggins, desk Sports, ...).
E2E_DUMP="${AUTODOCS_E2E_DUMP:-$SERVER_DIR/../client/node_modules/superdesk-core/e2e/server/dump/full/main}"

WORK_DIR="${AUTODOCS_WORK_DIR:-/var/tmp/superdesk-autodocs}"

log() {
    echo "[autodocs-seed] $*"
}

SLEEPER_PID=""

# Sleeps in the background and waits for it, because a trap only runs between foreground commands and the
# process manager's TERM has to end this script at once.
sleep_forever() {
    trap 'trap - EXIT; [ -z "$SLEEPER_PID" ] || kill "$SLEEPER_PID" 2>/dev/null; exit 0' TERM INT
    while :; do
        sleep 3600 &
        SLEEPER_PID=$!
        wait "$SLEEPER_PID"
    done
}

trap 'log "unexpected exit of run_seed.sh, idling so the instance stays up"; sleep_forever' EXIT

helper() {
    python3 -I "$HELPER" "$@"
}

api_up() {
    curl -s -o /dev/null -m 8 "$API_URL/"
}

# api_post <path> <json body>: prints the HTTP status, keeps the body in $WORK_DIR/response.txt
api_post() {
    curl -sS -m 900 -o "$WORK_DIR/response.txt" -w '%{http_code}' \
        -X POST -H 'Content-Type: application/json' -d "$2" "$API_URL$1"
}

restore_snapshot() {
    local status
    status="$(api_post /restore_record "{\"name\": \"$1\"}")"
    case "$status" in
        2??) return 0 ;;
    esac
    log "restore_record $1 answered ${status:-nothing}: $(head -c 500 "$WORK_DIR/response.txt" 2>/dev/null)"
    return 1
}

# storage:dump writes dump/full/<name>/<database>/ and refuses an existing folder, so it dumps under a
# temporary name that replaces the old snapshot only once the dump is complete.
take_snapshot() {
    local name="$1" tmp="$1.tmp-$$"
    rm -rf "dump/full/$tmp"
    if ! python3 manage.py storage:dump -n "$tmp" > "$WORK_DIR/dump-$name.log" 2>&1; then
        log "storage:dump for $name failed:"
        tail -n 20 "$WORK_DIR/dump-$name.log"
        rm -rf "dump/full/$tmp"
        return 1
    fi
    rm -rf "dump/full/$name"
    mv "dump/full/$tmp" "dump/full/$name"
    helper record "$name" && log "snapshot $name saved"
}

DOCS_SHA=""

fetch_docs() {
    local dest="$WORK_DIR/docs"
    export GIT_TERMINAL_PROMPT=0
    rm -rf "$dest"
    # A sparse, blobless clone skips the guide's images. Older git versions without those options fall back
    # to a plain shallow clone.
    if ! { git clone --quiet --depth 1 --branch "$DOCS_REF" --filter=blob:none --sparse "$DOCS_REPO" "$dest" \
            && git -C "$dest" sparse-checkout set "$DOCS_PATH"; }; then
        rm -rf "$dest"
        git clone --quiet --depth 1 --branch "$DOCS_REF" "$DOCS_REPO" "$dest" || return 1
    fi
    if [ ! -f "$dest/$DOCS_PATH/seed.py" ]; then
        log "$DOCS_REPO at $DOCS_REF has no $DOCS_PATH/seed.py"
        return 1
    fi
    DOCS_SHA="$(git -C "$dest" rev-parse HEAD)"
    TOOLS_DIR="$dest/$DOCS_PATH"
}

run_tool() {
    local script="$1"
    shift
    log "running $script $*"
    (cd "$TOOLS_DIR" && python3 -u "$script" --api-url "$API_URL" --user "$SEED_USER" --password "$SEED_PASSWORD" "$@")
}

if [ "${AUTODOCS_SEED:-}" = "0" ]; then
    log "AUTODOCS_SEED=0, not seeding"
    sleep_forever
fi

# Fireq exports DB_NAME next to MONGO_URI and the Docker setups of this repository do not, which is what
# tells a deployed test instance from a developer's stack. The seed wipes the database, so a developer's
# data stays untouched unless AUTODOCS_SEED=1 is set.
if [ "${AUTODOCS_SEED:-}" != "1" ] && [ -z "${DB_NAME:-}" ]; then
    log "DB_NAME is not set, this does not look like a Fireq instance, not seeding (AUTODOCS_SEED=1 forces it)"
    sleep_forever
fi

cd "$SERVER_DIR" || sleep_forever
mkdir -p "$WORK_DIR" dump/full dump/records || sleep_forever

# Only one run at a time. Child processes inherit the lock, so a run killed half way keeps it until its
# last seed script has ended.
if command -v flock > /dev/null; then
    exec 9> "$WORK_DIR/seed.lock"
    if ! flock -n 9; then
        log "another seed run still holds $WORK_DIR/seed.lock, idling"
        sleep_forever
    fi
fi

rm -rf dump/full/*.tmp-* dump/full/*.tmp

# The base snapshot is rebuilt from the client build on every start: it costs a few seconds and keeps it in
# line with the client-core version this deploy installed.
BASE_OK=1
if ! helper prepare-base "$E2E_DUMP" "$BASE_SNAPSHOT"; then
    BASE_OK=0
    log "could not prepare the $BASE_SNAPSHOT snapshot from $E2E_DUMP; seed.py needs it"
fi

log "waiting for the API at $API_URL"
waited=0
until api_up; do
    if [ "$waited" -ge "$API_WAIT_SECONDS" ]; then
        log "the API never answered, giving up. Restart the instance to try again."
        sleep_forever
    fi
    sleep "$POLL_SECONDS"
    waited=$((waited + POLL_SECONDS))
done
log "API is up"

# snapshots.py exits 1 for "no" and 2 for an error. Seeding wipes the database, so anything but a clear
# "no marker" or "no archive" stops here.
helper marker-check "$SEED_VERSION"
case $? in
    0)
        if helper has "$CORE_SNAPSHOT" "$PLANNING_SNAPSHOT"; then
            log "already seeded ($SEED_VERSION), snapshots on disk, nothing to do"
            sleep_forever
        fi
        # A redeploy replaces the container, and with it the server folder; the database keeps the archive.
        helper extract "$SEED_VERSION"
        case $? in
            0)
                log "already seeded ($SEED_VERSION), snapshots restored from the database"
                sleep_forever
                ;;
            1)
                log "seeded ($SEED_VERSION) but the snapshot archive is missing, seeding again"
                ;;
            *)
                log "could not restore the snapshots from the database, not seeding. Restart to try again."
                sleep_forever
                ;;
        esac
        ;;
    1)
        log "no seed marker for $SEED_VERSION, seeding"
        ;;
    *)
        log "could not read the seed marker, not seeding. Restart the instance to try again."
        sleep_forever
        ;;
esac

TOOLS_DIR=""
if ! fetch_docs; then
    log "could not get $DOCS_PATH from $DOCS_REPO at $DOCS_REF, not seeding. Fix the ref and restart."
    sleep_forever
fi
log "seed scripts from $DOCS_REPO $DOCS_REF ($DOCS_SHA)"

FAILED=""

# Planning first: its --reset wipes the database (prepopulate with remove_first), and the newsroom seeded
# after it is what the instance shows between screenshot runs.
if run_tool seed_planning.py --reset && take_snapshot "$PLANNING_SNAPSHOT"; then
    :
else
    FAILED="$FAILED planning"
fi

if [ "$BASE_OK" = "1" ] && restore_snapshot "$BASE_SNAPSHOT" \
    && run_tool seed.py \
    && run_tool seed_broadcasting.py \
    && take_snapshot "$CORE_SNAPSHOT"; then
    :
else
    FAILED="$FAILED newsroom"
fi

if [ -n "$FAILED" ]; then
    log "seeding failed for:$FAILED (see the output above). Restart the instance to try again."
    sleep_forever
fi

if helper archive "$SEED_VERSION" "$CORE_SNAPSHOT" "$PLANNING_SNAPSHOT" \
    && helper marker-write "$SEED_VERSION" "$DOCS_REF" "$DOCS_SHA"; then
    log "seeded, marker $SEED_VERSION written"
else
    log "seeded, but the snapshots could not be archived, so the next start seeds again"
fi

sleep_forever
