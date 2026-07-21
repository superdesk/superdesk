---
name: superdesk-dev
description: |
  Run a local Superdesk development environment. Works only inside the
  `superdesk/` host repo, with sibling repos (superdesk-client-core,
  superdesk-planning, optionally superdesk-analytics / superdesk-publisher)
  cloned into the same parent directory. Wraps the dev scripts under
  `scripts/dev/` (setup, up, down, extension enable/disable) so non-experts
  don't have to remember Docker / npm / grunt commands.

  Invoke when the user wants to do any of:
  — "set up the local env", "first-time setup", "I just cloned the repo, get me running"
  — "start the app", "run superdesk locally", "spin up the dev environment"
  — "stop the app", "shut down the local environment"
  — "enable the X extension", "add the helloWorld extension", "turn on usageMetrics"
  — "disable the X extension", "remove the markForUser extension"
  — "list extensions", "which extensions are available", "what's enabled"

  Do not invoke for: the fully-containerised workflow (just `docker compose
  up` against the existing `docker-compose.yml` — no skill needed), running
  the e2e test suite (that lives in superdesk-client-core), Python/server
  code changes, production deploys, or work in any repo other than
  `superdesk/`.
---

# Running Superdesk locally

You are helping someone bring up a local Superdesk dev environment, or
toggle in-tree extensions in their running setup. The user may be a UI
designer (often without strong CLI experience) or a developer iterating
on the frontend. Communicate concretely: no Docker / npm / Volta jargon
unless they bring it up first. Explain what's happening at each step, and
hand control back at clear stopping points.

The skill does not write code, does not commit, does not open PRs. Its
output is a running stack (or a stopped one) and a short summary.

## Pre-approved commands

The project ships `.claude/settings.json` with an allow-list for the four
dev scripts (`setup.sh`, `up.sh`, `down.sh`, `extension.sh`) and a small
set of diagnostic helpers (`docker info`, `docker compose ... ps`,
`docker compose ... logs`, `lsof -i :5000` / `lsof -i :5001`, `lsof -i :9000`,
`volta --version`, `node --version`, `curl` for health checks, `cat`/
`tail` on the grunt log). Those commands run without per-command
approval — the user gave consent once when first opening the project.

If you find yourself wanting to run something that's not on that list
(e.g. `npm install` directly, `docker compose down -v` outside the
script's `--volumes` path, modifying files in `scripts/dev/`), STOP and
ask the user. The allowlist is deliberately narrow; broadening it is the
user's decision, not yours.

## Workflow

You arrived here because the user's natural-language phrasing matched
the skill description. That's the forgiving entry point — but it also
means there's a non-zero chance the matcher fired on something the user
didn't actually intend. Confirmation comes before action.

(If the user instead typed an explicit slash command —
`/superdesk-setup`, `/superdesk-up`, `/superdesk-down`,
`/superdesk-ext` — they bypassed this skill entirely and the command's
own prompt is running. Slash commands skip confirmation by design;
typing the command name *is* the confirmation.)

### 1. Identify the requested mode

The user's message implies one of five modes — pick one:

- **setup** — first-time or after a fresh clone / reset. Runs
  `scripts/dev/setup.sh`.
- **up** — start the stack day-to-day (after setup has been done at least
  once). Runs `scripts/dev/up.sh`.
- **down** — stop the running stack. Runs `scripts/dev/down.sh`.
- **extension** — enable / disable / list in-tree extensions. Runs
  `scripts/dev/extension.sh`.
- **status** — check what's currently running (no script; use `docker
  compose ps` against `docker-compose.dev.yml` and `lsof -i :9000`).

If the user's intent is ambiguous (e.g. "get me set up" right after they
ran setup last week — do they want setup again or just up?), use
`AskUserQuestion` with concrete options to disambiguate before going on.

### 2. Confirm intent before running anything

Before invoking any script, confirm with the user using
`AskUserQuestion` — even when the matched mode seems obvious. The cost
of one extra round-trip is small; the cost of running setup (slow), down
(stops things), or extension changes (modifies code) when the user
didn't intend it is much higher.

Format the confirmation concretely. State the action and the exact
command you're about to run, e.g.:

> "I think you want to set up the local dev environment. That means
> running `./scripts/dev/setup.sh` — `npm install`, link sibling repos,
> bring up Docker, init the database on first run. It takes a few
> minutes on first run. Continue?"

For **status** mode this confirmation step is unnecessary — it's read-
only. For everything else, confirm first.

If the user is doing something especially impactful — `down --volumes`,
`setup --reinit` against an existing DB, disabling an extension — spell
out the impact in plain language. Don't bury it in flag names.

If the user wants the explicit-command path going forward (less back-
and-forth), mention that the slash commands exist:
`/superdesk-setup`, `/superdesk-up`, `/superdesk-down`, `/superdesk-ext`.
They skip this confirmation step.

### 3. Verify the preconditions

Before running, three checks:

**3a. You're inside the `superdesk/` host repo.**

- `docker-compose.dev.yml` exists at the repo root, and
- `client/package.json`'s `name` field is `"superdesk"`.

If not, stop and tell the user: "This skill only works inside the
`superdesk/` host repo. The other repos (client-core, planning, analytics,
publisher) are siblings of it, not where this runs."

**3b. For setup mode only: required siblings exist.**

The dev workflow REQUIRES two sibling repos cloned as siblings of
this one: `superdesk-client-core` and `superdesk-planning`. Two more
are optional: `superdesk-analytics` and `superdesk-publisher`.

Before running setup, check:

```bash
ls ../superdesk-client-core/package.json ../superdesk-planning/package.json
```

If either is missing, STOP — do not run setup.sh, it will error out
after some work has already started. Instead, tell the user exactly
which sibling is missing and give them the exact git clone command
to copy-paste, e.g.:

> I can't set up the dev environment yet — the required sibling repos
> aren't cloned. From the parent directory of this repo, run:
>
> ```
> cd <parent>
> git clone https://github.com/superdesk/superdesk-client-core.git
> git clone https://github.com/superdesk/superdesk-planning.git
> ```
>
> Then run /superdesk-setup again. (Optional repos:
> superdesk-analytics, superdesk-publisher — skip those unless you
> know you need them.)

Use `AskUserQuestion` to ask the user whether they want you to wait
for them to clone, or whether they want to abort.

**3c. For up / down / extension modes:** the sibling check is not
required at the skill level — `up.sh` / `down.sh` are independent of
sibling state, and `extension.sh enable` will check that
`superdesk-client-core` exists itself.

### 4. Run the script for the chosen mode

#### setup mode

Run `./scripts/dev/setup.sh` (or with `--only` / `--skip` / `--link` /
`--reinit` if the user specified preferences — translate their phrasing).

Watch for these patterns in the output:

- **"Docker is installed but not running"** — tell the user to start Docker
  Desktop and re-run. Don't try to start it yourself.
- **"Volta is not installed"** — point them at https://volta.sh. The Node
  version is pinned through it; the dev stack will not work without it.
- **"Need at least superdesk-client-core linked"** — they haven't cloned
  client-core as a sibling. Tell them where it should go
  (`<parent>/superdesk-client-core/`) and stop.

On success, the script leaves the backend running and prints next steps
(run `up.sh`). Relay those to the user.

#### up mode

Run `./scripts/dev/up.sh`. Watch for:

- **"Run ./scripts/dev/setup.sh first"** — they haven't done setup. Route
  to setup mode.
- **"Something is already listening on port 5000/5001/9000"** — port conflict;
  the script names the holder. Tell the user; do not kill processes
  yourself.
- **Long wait on the client URL** — grunt's cold build is ~60–120s. Tell
  the user this is normal; if it exceeds 5 minutes, point them at the log
  file the script printed.

On success, hand off with the URL (`http://localhost:9000`, login admin /
admin) and a note that grunt's watch is active — they can edit sibling
checkouts and reload the browser to see changes.

#### down mode

Run `./scripts/dev/down.sh`. The only thing to relay is the Docker Desktop
reminder the script prints at the end — designers tend to forget Docker
keeps running as a separate process after the compose stack stops.

If the user asked for a full reset ("wipe everything", "fresh start"), run
`./scripts/dev/down.sh --volumes`. Warn them first that this drops all DB
state.

#### extension mode

For "what's available": `./scripts/dev/extension.sh list`.

For enable / disable: `./scripts/dev/extension.sh <enable|disable> <name>`.

Watch for:

- **"is on the legacy compile-and-correct build path"** — auto-tagging-
  widget. The script refuses; relay the reason as-is.
- **"is not an in-tree extension"** — typo or unknown name. Show the list
  output so the user picks a real name.
- **"is not in the managed region"** — they're trying to disable
  planning-extension or broadcasting, which live outside the script's
  region. Tell them this and offer to walk them through manual editing if
  they really need to.

Grunt watch picks up the `client/index.ts` change automatically; no
restart needed. Tell the user to refresh the browser after a few seconds.

## Failure modes

The script-level errors above cover most cases. Beyond those:

### The user has multiple Superdesk stacks running

E2E and dev both publish a Superdesk backend on the same default host
port (5000 on Linux, 5001 on macOS). If the user has the e2e stack from
`superdesk-client-core/e2e/scripts/e2e-up.sh` running, the dev stack will
fail to bind. The dev script's preflight names the conflict; tell the user
to stop the other stack first.

### npm install fails during setup

Usually one of: the wrong Node version (Volta not active in this shell),
corrupted `node_modules` from a previous half-done install, or a network
hiccup. Don't try fancy recovery — tell the user to:

1. Confirm Volta is active (`node --version` should show 22.x).
2. Delete `client/node_modules` and re-run setup.

If that fails, escalate to a developer; this skill doesn't debug npm.

### dev-link fails: "Missing script: devlink" or "unknown command"

setup.sh runs `npm run devlink -- <siblings>`, which delegates to
`@superdesk/build-tools dev-link`. Two distinct failure shapes:

- **"Missing script: devlink"** — the host repo's `client/package.json`
  does not have a `devlink` script registered. The script was added
  as part of the dev-tooling PR; if the user's host checkout pre-dates
  that PR, they need to `git pull` (or merge develop). This is the
  expected failure shape on stale checkouts, not a tooling bug.
- **"unknown command: dev-link"** from `@superdesk/build-tools` itself —
  the installed build-tools is older than 1.1.0 (where the command was
  added by superdesk-client-core PR #5180). The host's pinned range
  `^1.0.19` permits anything up to 2.0, so a clean reinstall normally
  fixes it:

  ```
  rm -rf client/node_modules client/package-lock.json
  ./scripts/dev/setup.sh
  ```

  If after a clean reinstall the command still isn't found, the host's
  build-tools dep range needs bumping — that's a developer task, not
  something this skill should attempt.

### "data-test-id"-style extension that needs more than a config change

If the user asks to enable an extension that isn't in `client-core/scripts/
extensions/` at all — for example, an extension that lives in
`superdesk-planning/client/<x>-extension` or in a sibling repo entirely —
that's outside scope. Tell them: "This skill only handles in-tree
extensions from superdesk-client-core. For external extensions, edit
`client/index.ts` manually or ask a developer."

### First-run init fails

If `python manage.py app:initialize_data` errors, it usually means MongoDB
or Elasticsearch didn't fully start before init ran. Wait 30s and run
setup with `--reinit`. If it still fails, dump `docker compose -f
docker-compose.dev.yml logs superdesk-server` for the user and stop.

## What to communicate at hand-off

A short, plain-language status:

- What's running (server + client URLs).
- What credentials to use (admin / admin).
- If applicable, what extensions are now enabled.
- How to stop everything (`./scripts/dev/down.sh`) and what Docker Desktop
  will be doing afterwards.

No need to summarise the script output verbatim; the user saw it. Focus on
"here's where you can click now."

## Pitfalls — avoid without being told

- **Do not edit `client/index.ts` directly.** Always go through
  `scripts/dev/extension.sh`. Hand-edits inside the markers will be undone
  by the next script invocation; hand-edits outside the markers are fine
  but the user shouldn't need to make any.
- **Do not run `docker compose down -v` casually.** It drops the named
  volumes and forces a re-run of the first-time DB init (5–10 minutes).
  Use `down.sh` (without `--volumes`) for normal stops.
- **Do not start Docker Desktop on the user's behalf.** Some users have
  Docker permissioned in ways that make automated startup fail silently.
  Always ask them to start it.
- **Do not skip Volta.** "I'll just use my system Node" produces hard-to-
  diagnose errors in grunt builds.
- **Do not modify the existing `docker-compose.yml`.** It's the fully-
  containerised path that other users rely on. The dev stack lives in
  `docker-compose.dev.yml`, always.

## When to ask the user vs proceed

- Ambiguous mode (setup vs up vs status) → ask once with
  `AskUserQuestion`.
- Unknown extension name → don't guess; show the list and let the user
  pick.
- Conflicting port that looks like another Superdesk stack → tell the user
  and stop; don't try to identify which other stack it is.
- Setup wants to do first-run DB init → just do it; that's why it's there.
- A real bug in the underlying scripts (script crash, unexpected output)
  → relay the error verbatim and stop. Don't paper over it.
