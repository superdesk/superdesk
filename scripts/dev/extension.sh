#!/usr/bin/env bash
#
# Enable or disable an in-tree extension from superdesk-client-core.
#
# Usage:
#   ./extension.sh list
#   ./extension.sh enable  <name>
#   ./extension.sh disable <name>
#
# This script edits the standard-template region of client/index.ts marked
# by // extensions:start / // extensions:end. Entries outside that region
# (planning-extension, broadcasting, anything with custom load logic) are
# manually managed — not touched by this script.
#
# Grunt's watch will pick up the index.ts change automatically; no restart
# is required if the dev stack is already running via ./up.sh.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PARENT_DIR="$(cd "$REPO_ROOT/.." && pwd)"
INDEX_FILE="$REPO_ROOT/client/index.ts"
EDITOR_PY="$SCRIPT_DIR/extension-edit.py"
EXTENSIONS_DIR="$PARENT_DIR/superdesk-client-core/scripts/extensions"

# In-tree extensions that PR #5177 migrated to the source-build path. Adding
# any of these via this script is safe.
MIGRATED_EXTENSIONS=(
    "ai-widget"
    "annotationsLibrary"
    "availability-manager"
    "broadcasting"
    "datetimeField"
    "helloWorld"
    "markForUser"
    "predefinedTextField"
    "sams"
    "usageMetrics"
    "videoEditor"
)

# Migrated extensions that need custom load logic (e.g. setCustomizations
# call, .then chain). These live OUTSIDE the // extensions:start /
# // extensions:end markers in client/index.ts because the script's editor
# only handles the standard `{id, load: () => import(...)}` template. To
# enable/disable any of these, edit client/index.ts directly.
CUSTOM_LOAD_EXTENSIONS=(
    "broadcasting"
)

# Still on the legacy compile-and-correct path. Linking these into a
# dev-link setup breaks the build until they're migrated.
LEGACY_EXTENSIONS=(
    "auto-tagging-widget"
)

fail() { printf '\n[dev-extension] ERROR: %s\n' "$*" >&2; exit 1; }

is_in_list() {
    local needle="$1"; shift
    for x in "$@"; do
        [ "$x" = "$needle" ] && return 0
    done
    return 1
}

print_list() {
    # Bucket the MIGRATED list: toggleable here vs. requires-manual-edit.
    local toggleable=() custom=()
    local m
    for m in "${MIGRATED_EXTENSIONS[@]}"; do
        if is_in_list "$m" "${CUSTOM_LOAD_EXTENSIONS[@]}"; then
            custom+=("$m")
        else
            toggleable+=("$m")
        fi
    done

    printf '\n[dev-extension] Toggleable via this script (enable/disable):\n'
    for x in "${toggleable[@]}"; do printf '  - %s\n' "$x"; done

    if [ "${#custom[@]}" -gt 0 ]; then
        printf '\n[dev-extension] Migrated but require manual editing of client/index.ts\n'
        printf '[dev-extension] (custom load logic — outside the // extensions:start markers):\n'
        for x in "${custom[@]}"; do printf '  - %s\n' "$x"; done
    fi

    printf '\n[dev-extension] On legacy build path (do NOT enable yet):\n'
    for x in "${LEGACY_EXTENSIONS[@]}"; do printf '  - %s\n' "$x"; done

    printf '\n[dev-extension] Currently enabled in client/index.ts:\n'
    # Use POSIX [[:space:]] (not \s) — BSD sed on macOS does not support \s.
    grep -E "id:[[:space:]]*'[^']+'" "$INDEX_FILE" \
        | sed -E "s/.*id:[[:space:]]*'([^']+)'.*/  - \1/"
    printf '\n'
}

# ---- main ----

[ $# -ge 1 ] || fail "usage: $0 <list|enable|disable> [name]"

MODE="$1"

[ -f "$INDEX_FILE" ] || fail "$INDEX_FILE not found — run from inside the superdesk/ host repo."

case "$MODE" in
    list)
        print_list
        exit 0
        ;;
    enable|disable) ;;
    *) fail "mode must be 'list', 'enable', or 'disable' (got '$MODE')" ;;
esac

[ $# -ge 2 ] || fail "usage: $0 $MODE <name>"
NAME="$2"

# Sibling check: only required for enable (need to verify the dir exists in
# client-core). For disable we don't need client-core present.
if [ "$MODE" = "enable" ]; then
    [ -d "$EXTENSIONS_DIR" ] || fail "$EXTENSIONS_DIR not found. Run ./setup.sh first."
    [ -d "$EXTENSIONS_DIR/$NAME" ] || {
        echo "[dev-extension] ERROR: '$NAME' is not an in-tree extension in $EXTENSIONS_DIR." >&2
        print_list
        exit 1
    }
fi

if is_in_list "$NAME" "${CUSTOM_LOAD_EXTENSIONS[@]}"; then
    cat >&2 <<EOF

[dev-extension] '$NAME' has custom load logic in client/index.ts and lives
[dev-extension] OUTSIDE the // extensions:start markers. This script only
[dev-extension] manages standard-template entries.

[dev-extension] To toggle '$NAME', edit client/index.ts directly — find
[dev-extension] the entry above the markers and comment it out (to
[dev-extension] disable) or restore it (to enable).

EOF
    exit 1
fi

if is_in_list "$NAME" "${LEGACY_EXTENSIONS[@]}"; then
    cat >&2 <<EOF

[dev-extension] ERROR: '$NAME' is on the legacy compile-and-correct build path.

Linking it into a dev-link setup will produce recursive 'dist/superdesk/client/...'
paths and a broken build (this is the exact class of problem PR #5177 fixed
for the migrated extensions).

This script refuses to enable it until the underlying migration lands. For
now, do not enable '$NAME' via the dev skill — coordinate with a developer
if you genuinely need it locally.

EOF
    exit 1
fi

# For enable, validate it's on the known-good list. For disable, allow any
# name (the user might be cleaning up an entry that's no longer in the list).
if [ "$MODE" = "enable" ] && ! is_in_list "$NAME" "${MIGRATED_EXTENSIONS[@]}"; then
    echo "[dev-extension] ERROR: '$NAME' is not on the skill-managed list." >&2
    echo "If it's a newly-migrated in-tree extension, add it to MIGRATED_EXTENSIONS in this script." >&2
    exit 1
fi

command -v python3 > /dev/null || fail "python3 is required."

python3 "$EDITOR_PY" "$MODE" "$NAME" "$INDEX_FILE"
