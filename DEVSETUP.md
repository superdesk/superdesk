# Local development setup

This document covers the two supported local development workflows. For
the bare-minimum quick-start (single `docker compose up`), see
[README.md](./README.md) — that's the "I want to see Superdesk running"
path and doesn't require cloning any other repos.

This document is for development work, where you need your edits to a
sibling checkout (e.g. `superdesk-client-core`) to take effect.

## Prerequisites

Install / set up these before running anything:

- **Docker Desktop installed and running.** All backend services run in
  containers.
- **[Volta](https://volta.sh) installed.** Node version is pinned via
  Volta from `client/package.json`; this skips the "which Node?" question
  entirely.
- **Sibling repos cloned in the same parent directory as this one.**
  `superdesk-client-core` and `superdesk-planning` are **required**;
  `superdesk-analytics` and `superdesk-publisher` are optional.

  ```
  ~/code/
    superdesk/                  <-- this repo
    superdesk-client-core/      (required)
    superdesk-planning/         (required)
    superdesk-analytics/        (optional)
    superdesk-publisher/        (optional)
  ```

  The dev tooling discovers siblings by name in the parent dir.

## First-run validation checklist

Once the prerequisites above are in place, walk through these steps in
order to confirm everything works end to end. Each step has a single
clear success signal; if one fails, stop and fix it before moving on.

1. **Docker is running.** `docker info` exits 0 and prints daemon details.
   If it errors, start Docker Desktop and wait for the whale icon to stop
   animating.

2. **Volta is installed.** `volta --version` prints a version. If not,
   install from [volta.sh](https://volta.sh) — Node version is pinned
   through it, and `npm run start` will use the wrong Node without it.

3. **Sibling layout is right.** From this repo's root,
   `ls ../superdesk-client-core/package.json ../superdesk-planning/package.json`
   both exist. (Optional siblings:
   `superdesk-analytics`, `superdesk-publisher`.)

4. **Setup runs clean.** `./scripts/dev/setup.sh` completes with the
   "setup complete" banner. The script prints the exact server URL it
   chose — default `http://localhost:5000/api/` on Linux, or
   `http://localhost:5001/api/` on macOS (auto-picked to avoid AirPlay
   Receiver which holds :5000). To override either default:
   `SUPERDESK_PORT=5070 ./scripts/dev/setup.sh`. First run is slow
   (cold-cache `npm install`, image pulls, DB init). Re-runs are fast.

5. **Server responds correctly.** `curl -s -o /dev/null -w '%{http_code}'`
   against the URL setup printed should return `200`, `401`, or `403`
   — any of those means a real Superdesk server is answering. Anything
   else (timeout, 5xx) means it hasn't come up yet.

6. **Client comes up.** `./scripts/dev/up.sh` waits, then prints
   `client: http://localhost:9000/`. Open it in a browser. The Superdesk
   login screen renders.

7. **Login works.** Sign in with `admin` / `admin`. You land on the
   monitoring view.

8. **Watch picks up sibling edits.** In `../superdesk-client-core`, make a
   trivial visible change (e.g. edit a label in
   `scripts/apps/dashboard/...`). Wait ~5–10s; the browser auto-reloads
   and your change is visible. This is the whole point of the workflow.

9. **Extension toggle works.** `./scripts/dev/extension.sh enable
   helloWorld` succeeds. The browser reloads after a few seconds and the
   helloWorld extension's UI shows up. Disable it with
   `./scripts/dev/extension.sh disable helloWorld` to leave the repo in
   the state you found it.

10. **Down is clean.** `./scripts/dev/down.sh` stops both grunt and the
    compose stack, and prints the Docker Desktop reminder. Quit Docker
    Desktop from the menu bar.

If you got through all ten, your dev environment is real. If something
broke at step N, the [Troubleshooting](#troubleshooting) section at the
bottom covers the most common causes.

## Choosing a workflow

| Workflow | Best for | Iteration speed | Setup complexity |
|---|---|---|---|
| **A. Fully containerised** | Showing the app to someone, occasional changes | Slow (container rebuild on every edit) | Low |
| **B. Server in Docker, client native** | Daily frontend / extension work | Fast (grunt watch picks up edits instantly) | Medium (one-time setup) |

If you're a UI designer or you'll be editing the client / extensions
frequently, use workflow B. Otherwise A is simpler.

---

## Workflow A — fully containerised

The existing `docker-compose.yml` runs everything (server + client + DBs)
in containers. The client image is rebuilt on each `up`.

```sh
docker compose up -d
```

App available at `http://localhost:8080`. First-run admin / data init per
the README. Stop with `docker compose stop`.

This workflow does **not** pick up edits to sibling checkouts. If you need
that, use workflow B.

---

## Workflow B — server in Docker, client native

Backend services (server + MongoDB + Redis + Elasticsearch) run via
`docker-compose.dev.yml`. The client runs natively on your host through
`npm run start` (grunt with file watch), and your sibling checkouts of
`superdesk-client-core` / `superdesk-planning` are symlinked into
`node_modules` via `npm run devlink` so edits take effect immediately.

Three scripts under `scripts/dev/` cover the lifecycle:

```sh
./scripts/dev/setup.sh   # first-time install + link siblings + init DB
./scripts/dev/up.sh      # start the stack (daily)
./scripts/dev/down.sh    # stop the stack (data preserved)
```

A fourth script toggles in-tree extensions in / out of the running stack:

```sh
./scripts/dev/extension.sh list                  # see what's available / enabled
./scripts/dev/extension.sh enable <name>         # add an in-tree extension
./scripts/dev/extension.sh disable <name>        # remove one
```

After setup, the app is available at `http://localhost:9000`. Login with
admin / admin. The server API defaults to `http://localhost:5000/api/`
on Linux, or `http://localhost:5001/api/` on macOS (where :5000 is
reserved for AirPlay Receiver — auto-detected). Override with
`SUPERDESK_PORT=<port>` before invoking the scripts.

### Setup details

`setup.sh` does, in order:

1. Validates Docker is running and Volta is installed.
2. Auto-discovers sibling repos under the parent directory.
3. Runs `npm install` in `./client`.
4. Runs `npm run devlink` against the discovered siblings (replaces
   the GitHub-pulled copies in `node_modules` with symlinks). The
   [`dev-link` command](https://github.com/superdesk/superdesk-client-core/pull/5180)
   in `@superdesk/build-tools` handles this idempotently.
5. Starts `docker-compose.dev.yml` and waits for the server to be ready.
6. On first run, executes `python manage.py app:initialize_data` and
   creates the admin / admin user. A sentinel at
   `scripts/dev/.run/.setup-done` records that this is done so subsequent
   runs skip it.

Flags:

- `--only NAME[,NAME]` — link only the specified siblings.
- `--skip NAME[,NAME]` — link all discovered siblings except these.
- `--link /abs/path` — link an explicit path (e.g. a fork outside the
  parent dir). Repeatable.
- `--reinit` — force re-run of the first-run DB init.

### Extensions

In-tree extensions live under `superdesk-client-core/scripts/extensions/`.
[PR #5177](https://github.com/superdesk/superdesk-client-core/pull/5177)
migrated 11 of them to a source-build path that works with symlinked
local development. One (`auto-tagging-widget`) is still on the legacy
compile path and is not yet safe to enable in a dev-link setup —
`extension.sh` refuses with a clear message.

The script edits a marked region in `client/index.ts`:

```ts
// extensions:start (managed by scripts/dev/extension.sh — do not edit by hand)
{
    id: 'NAME',
    load: () => import('superdesk-core/scripts/extensions/NAME'),
},
// ...
// extensions:end
```

Entries outside that region (`planning-extension`, `broadcasting`,
anything with custom `load` logic) are manually managed; the script does
not touch them.

### Stopping

`down.sh` runs `docker compose stop` — the named volumes for MongoDB and
Elasticsearch are preserved, so your test data survives restarts.

If you want a clean wipe: `./scripts/dev/down.sh --volumes`. This drops
the volumes and resets the setup sentinel; the next `setup.sh` will
re-run the first-time DB init.

**Important:** stopping the compose stack does NOT stop Docker Desktop
itself. Docker keeps running in the background until you quit it
manually from the menu bar (Cmd-Q on the Docker icon). The script
reminds you of this on each stop.

### Using Claude Code

The scripts have two Claude Code wrappers, both shipped in this repo.

**Slash commands** (explicit, fast — no confirmation roundtrip):

- `/superdesk-setup` → `scripts/dev/setup.sh` (supports `--only`, `--skip`, `--link`, `--reinit`)
- `/superdesk-up` → `scripts/dev/up.sh` (supports `--rebuild-server`)
- `/superdesk-down` → `scripts/dev/down.sh` (supports `--volumes`)
- `/superdesk-ext list | enable NAME | disable NAME` → `scripts/dev/extension.sh`

Slash commands run the underlying script directly. The only confirmation
prompt is `/superdesk-down --volumes`, which is destructive (drops DB
state).

**Natural-language skill** (forgiving, catches phrasings):

The [`superdesk-dev` skill](./.claude/skills/superdesk-dev/SKILL.md)
catches phrasings like "set up the dev environment", "start Superdesk",
"enable helloWorld", etc. It confirms intent with you before running
anything — useful as a safety net when the matcher might fire on
something you didn't intend.

Pick whichever fits how you work. Both invoke the same scripts and the
underlying behaviour is identical. The scripts also work standalone
without Claude.

---

## End-to-end tests

The Playwright e2e suite lives in `superdesk-client-core` and has its own
stack (`e2e/scripts/e2e-up.sh` in that repo). The dev compose here and
the e2e compose there both publish a Superdesk backend on a host port
(by default :5000, or :5001 on macOS), so they cannot run at the same
time without explicit `SUPERDESK_PORT` overrides — stop one before
bringing up the other.

## Troubleshooting

Quick lookup for the most common failures, cross-referenced with the
[first-run checklist](#first-run-validation-checklist).

**"Docker is installed but not running" (step 1).** Open Docker Desktop
and wait for the whale icon to stop animating. On Apple Silicon, the first
launch after a reboot can take 30–60s.

**`npm run devlink` fails with "Missing script: devlink" (step 4).**
The host repo's `client/package.json` doesn't have the `devlink`
script registered yet — your checkout pre-dates the dev-tooling
addition. Pull the latest `develop` and try again.

**`npm run devlink` fails with "no such file or directory" (step 4).**
A sibling repo path doesn't exist or is misspelled. Re-check the
parent directory layout — siblings live next to this repo, not inside
it.

**`devlink` fails with "unknown command" or similar (step 4).** The
installed `@superdesk/build-tools` is older than 1.1.0 (where the
`dev-link` command was added). Clean reinstall:

```sh
rm -rf client/node_modules client/package-lock.json
./scripts/dev/setup.sh
```

If that doesn't pull a newer build-tools, the host's pinned range
needs bumping — escalate to a developer.

**Step 5 returns 200 instead of 401/403.** Something else (often macOS
AirPlay Receiver on :5000, or a leftover container) is on the port. Run
`lsof -i :<port> -sTCP:LISTEN` (where `<port>` is the one the setup
script printed) to identify, then stop the holder.

**Step 6 hangs longer than 5 minutes.** The grunt cold build is slow but
should not exceed 3 minutes on a recent machine. Check
`scripts/dev/.run/grunt-server.log` for the actual error.

**Step 7 fails with "invalid credentials".** First-run init didn't run, or
ran against a different DB. Run `./scripts/dev/setup.sh --reinit` to
force re-init. If you nuked the volumes with `down.sh --volumes` since
setup, `--reinit` is required anyway.

**Step 8 doesn't reload after edits.** Grunt's watch is running but the
file isn't in a watched path. Confirm the edit is inside a sibling
checkout that was actually dev-linked (run `./scripts/dev/setup.sh` with
no flags to see the link summary). Symlinks: if your shell follows them
strangely, the issue may be that grunt is watching the original path,
not the symlinked one.

**Step 9 reports "is on the legacy compile-and-correct build path".** You
tried to enable `auto-tagging-widget`. That extension isn't yet on the
source-build path (PR #5177); enabling it will break the build. Leave it
alone until the underlying migration lands.

**Anything else.** Capture the error verbatim and ask in
#superdesk-frontend, or open a developer ticket. Don't guess at fixes —
the underlying tooling (`@superdesk/build-tools`, grunt, Volta) is doing
real work and band-aid fixes pile up.
