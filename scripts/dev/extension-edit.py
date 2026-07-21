#!/usr/bin/env python3
"""
Edit client/index.ts to enable or disable a standard-template extension.

Operates inside the region delimited by:

    // extensions:start (managed by scripts/dev/extension.sh — do not edit by hand)
    ...
    // extensions:end

Standard template per entry:

    {
        id: 'NAME',
        load: () => import('superdesk-core/scripts/extensions/NAME'),
    },

Custom-load entries (with .then / setCustomizations / multi-statement bodies)
should live OUTSIDE the markers; this script refuses to disable them and
prints a clear message instead.

Invoked by scripts/dev/extension.sh; not meant to be called directly.

Usage: extension-edit.py <enable|disable> <name> <path-to-index.ts>
"""

import re
import sys


def main():
    if len(sys.argv) != 4:
        print(__doc__, file=sys.stderr)
        sys.exit(2)

    mode, name, path = sys.argv[1], sys.argv[2], sys.argv[3]

    if mode not in ("enable", "disable"):
        print(f"ERROR: mode must be 'enable' or 'disable', got '{mode}'", file=sys.stderr)
        sys.exit(2)

    with open(path) as f:
        lines = f.readlines()

    start_idx = end_idx = None
    for i, line in enumerate(lines):
        if "// extensions:start" in line and start_idx is None:
            start_idx = i
        elif "// extensions:end" in line and start_idx is not None:
            end_idx = i
            break

    if start_idx is None or end_idx is None:
        print(
            f"ERROR: extension markers not found in {path}.\n"
            "Expected lines containing '// extensions:start' and '// extensions:end'.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Walk the lines between the markers, grouping into object entries.
    # An entry starts on a line whose stripped content is '{' and ends on
    # a line whose stripped content is '},'. Anything else (blank lines,
    # comments) is treated as a passthrough chunk between entries.
    region = lines[start_idx + 1 : end_idx]
    entries = []  # list of (kind, value): kind is 'entry' (list of lines) or 'other' (single line)
    current = None
    for line in region:
        stripped = line.strip()
        if current is None:
            if stripped == "{":
                current = [line]
            else:
                entries.append(("other", line))
        else:
            current.append(line)
            if stripped == "},":
                entries.append(("entry", current))
                current = None
    if current is not None:
        print(
            f"ERROR: unclosed entry inside extension markers in {path}",
            file=sys.stderr,
        )
        sys.exit(1)

    def entry_id(entry_lines):
        for l in entry_lines:
            m = re.search(r"id:\s*'([^']+)'", l)
            if m:
                return m.group(1)
        return None

    def is_standard_template(entry_lines):
        body = "".join(entry_lines)
        # Reject entries with custom-load shapes.
        forbidden = (".then(", "setCustomizations", "async ", "function")
        return not any(token in body for token in forbidden)

    if mode == "enable":
        for kind, value in entries:
            if kind == "entry" and entry_id(value) == name:
                print(f"INFO: '{name}' is already enabled — no change.", file=sys.stderr)
                sys.exit(0)
        # Build a fresh entry and insert before // extensions:end.
        new_entry = [
            "            {\n",
            f"                id: '{name}',\n",
            f"                load: () => import('superdesk-core/scripts/extensions/{name}'),\n",
            "            },\n",
        ]
        new_lines = lines[:end_idx] + new_entry + lines[end_idx:]

    else:  # disable
        found = False
        new_entries = []
        for kind, value in entries:
            if kind == "entry" and entry_id(value) == name:
                if not is_standard_template(value):
                    print(
                        f"ERROR: '{name}' inside the managed region has a custom-load "
                        f"shape (.then/setCustomizations/etc). Move it outside the "
                        f"// extensions:start … // extensions:end markers and edit it "
                        f"manually, then re-run this command.",
                        file=sys.stderr,
                    )
                    sys.exit(1)
                found = True
                continue  # drop it
            new_entries.append((kind, value))
        if not found:
            print(
                f"INFO: '{name}' is not in the managed region — no change.\n"
                f"  If it's enabled outside the markers (custom load), edit "
                f"client/index.ts manually.",
                file=sys.stderr,
            )
            sys.exit(0)
        new_region_lines = []
        for kind, value in new_entries:
            if kind == "entry":
                new_region_lines.extend(value)
            else:
                new_region_lines.append(value)
        new_lines = lines[: start_idx + 1] + new_region_lines + lines[end_idx:]

    with open(path, "w") as f:
        f.writelines(new_lines)
    print(f"OK: '{name}' {mode}d in {path}")


if __name__ == "__main__":
    main()
