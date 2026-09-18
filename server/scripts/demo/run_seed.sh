#!/usr/bin/env bash
# Seeds the Briefdesk demo once per database, as the `seed:` entry of server/Procfile.
#
# This process must never exit. Honcho stops every process of the Procfile as soon as one of them
# ends, and the systemd unit then restarts the whole instance in a loop. Every path below
# therefore finishes in sleep_forever, including failures, and an EXIT trap catches anything that
# slips through (an unbound variable, a typo).

set -u

# Bump to seed again on a database that was already seeded.
SEED_VERSION="v1"

# Honcho gives the first Procfile entry (`rest`) port 5000 and hypercorn_config.py binds to $PORT.
# The seed talks to it directly, so it needs neither the public name nor a TLS certificate.
LOCAL_API_URL="${BRIEFDESK_LOCAL_API_URL:-http://localhost:5000/api}"

DEFAULT_PORTAL_URL="https://nra-hgbriefdeskportaldemo.test.superdesk.org"

API_WAIT_SECONDS=900
PORTAL_WAIT_SECONDS=300
POLL_SECONDS=10

cd "$(dirname "$0")/../.." || true

log() {
    echo "[briefdesk-seed] $*"
}

SLEEPER_PID=""

# Sleeps in the background and waits for it, because a trap only runs between foreground commands
# and the process manager's TERM has to end this script at once.
sleep_forever() {
    trap 'trap - EXIT; [ -z "$SLEEPER_PID" ] || kill "$SLEEPER_PID" 2>/dev/null; exit 0' TERM INT
    while :; do
        sleep 3600 &
        SLEEPER_PID=$!
        wait "$SLEEPER_PID"
    done
}

trap 'log "unexpected exit of run_seed.sh, idling so the instance stays up"; sleep_forever' EXIT

# Any HTTP answer, error statuses included, counts as "reachable".
http_up() {
    python3 - "$1" <<'PY'
import sys
import urllib.error
import urllib.request

try:
    urllib.request.urlopen(sys.argv[1], timeout=8)
except urllib.error.HTTPError:
    sys.exit(0)
except Exception:
    sys.exit(1)
sys.exit(0)
PY
}

# marker check | marker write
marker() {
    python3 - "$1" "$SEED_VERSION" <<'PY'
import datetime
import os
import sys

from pymongo import MongoClient

action, version = sys.argv[1], sys.argv[2]
collection = MongoClient(os.environ["MONGO_URI"], serverSelectionTimeoutMS=10000).get_database()["briefdesk_seed"]

if action == "check":
    sys.exit(0 if collection.find_one({"_id": version}) else 1)

collection.replace_one(
    {"_id": version},
    {"_id": version, "seeded_at": datetime.datetime.now(datetime.timezone.utc)},
    upsert=True,
)
PY
}

if [ "${BRIEFDESK_SEED:-1}" = "0" ]; then
    log "BRIEFDESK_SEED=0, not seeding"
    sleep_forever
fi

# Fireq exports DB_NAME next to MONGO_URI and the Docker setups of this repository do not, which
# is what tells a deployed test instance from a developer's stack. A developer's data stays
# untouched unless BRIEFDESK_SEED=1 is set or seed_superdesk.py is run by hand.
if [ "${BRIEFDESK_SEED:-}" != "1" ] && [ -z "${DB_NAME:-}" ]; then
    log "DB_NAME is not set, this does not look like a Fireq instance, not seeding (BRIEFDESK_SEED=1 forces it)"
    sleep_forever
fi

if [ -z "${MONGO_URI:-}" ]; then
    log "MONGO_URI is not set, so the seed marker cannot be read, not seeding"
    sleep_forever
fi

if marker check; then
    log "database already seeded ($SEED_VERSION), nothing to do"
    sleep_forever
fi

api_url="$LOCAL_API_URL"
log "waiting for the API at $api_url"
waited=0
until http_up "$api_url"; do
    if [ "$waited" -ge "$API_WAIT_SECONDS" ]; then
        if [ "$api_url" = "$LOCAL_API_URL" ] && [ -n "${SUPERDESK_URL:-}" ]; then
            log "no answer from $api_url after ${waited}s, trying $SUPERDESK_URL"
            api_url="$SUPERDESK_URL"
            waited=0
            continue
        fi
        log "the API never answered, giving up. Restart the instance to try again."
        sleep_forever
    fi
    sleep "$POLL_SECONDS"
    waited=$((waited + POLL_SECONDS))
done
log "API is up"

portal_url="${PORTAL_URL:-$DEFAULT_PORTAL_URL}"
portal_url="${portal_url%/}"

# Two instances on the same host may not reach each other through their public names, so the push
# destination falls back to the portal container's internal name. Browsers keep the public URL.
portal_host="${portal_url#*://}"
portal_host="${portal_host%%/*}"
internal_portal_url="http://${portal_host%%.*}"

push_url="${PORTAL_PUSH_URL:-}"
if [ -z "$push_url" ]; then
    log "looking for the portal at $portal_url and $internal_portal_url"
    waited=0
    while [ -z "$push_url" ]; do
        if http_up "$portal_url/login"; then
            push_url="$portal_url"
        elif http_up "$internal_portal_url/login"; then
            push_url="$internal_portal_url"
        elif [ "$waited" -ge "$PORTAL_WAIT_SECONDS" ]; then
            push_url="$portal_url"
            log "the portal did not answer on either address, keeping $push_url."
            log "If pushes fail, edit the Briefdesk Portal recipient in Settings once the portal is up."
        else
            sleep "$POLL_SECONDS"
            waited=$((waited + POLL_SECONDS))
        fi
    done
fi
log "push destination: $push_url"

export SUPERDESK_URL="$api_url"
export SUPERDESK_USER="${SUPERDESK_USER:-admin}"
export SUPERDESK_PASSWORD="${SUPERDESK_PASSWORD:-admin}"
export PORTAL_URL="$portal_url"
export PORTAL_PUSH_URL="$push_url"

log "running seed_superdesk.py"
if python3 -u scripts/demo/seed_superdesk.py; then
    if marker write; then
        log "seeded, marker $SEED_VERSION written"
    else
        log "seeded, but the marker could not be written, so the next restart seeds again (harmless, the seed is idempotent)"
    fi
else
    log "seed_superdesk.py failed, see the output above. Restart the instance to try again."
fi

sleep_forever
