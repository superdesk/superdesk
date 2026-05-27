---
description: Start the local Superdesk dev stack (backend in Docker, client native via grunt watch).
---

Run `./scripts/dev/up.sh $ARGUMENTS` and relay its output.

The script accepts `--rebuild-server` to force a docker compose rebuild
of the server image — pass it through if the user mentioned needing a
rebuild.

If the script tells the user to run `setup.sh` first, route to
`/superdesk-setup`. Other failure modes (port conflicts, slow first
build): see `.claude/skills/superdesk-dev/SKILL.md`.

On success: tell the user the app is at `http://localhost:9000`, login
admin / admin. Mention that grunt watch is active — edits to sibling
checkouts auto-reload the browser.
