# Documentation screenshot instance

This branch (`auto-docs`) is the "docs instance" for the automated user guide screenshots (SDESK-8055). Fireq builds it as https://sd-autodocs.test.superdesk.org (admin / admin). The screenshot tooling lives in the docs repo, `superdesk/superdesk-docs-user-guide`, under `tools/screenshots`; this folder only seeds the instance and keeps snapshots of the seeded data so a capture run can start from a known state.

What the branch changes compared to `develop`:

- `server/settings.py`: `SUPERDESK_TESTING` on (adds the public `restore_record` and `prepopulate` endpoints), the ported `planning_prepopulate` endpoint (`server/planning_prepopulate.py`), `MONGO_DBNAME` derived from `MONGO_URI`, Europe/London as the default time zone, content expiry off.
- `server/Procfile`: a `seed:` process running `run_seed.sh`.
- `client/`: `view.dateformat` DD/MM/YYYY, `defaultTimezone` Europe/London, and the `content-lists` and `ai-widget` extensions (the AI widget answers with canned text, nothing calls an AI service).

## How the seed works

`run_seed.sh` runs once per start of the instance and then idles, because honcho stops every process when one of them exits.

1. It copies the client-core e2e `main` dump from `client/node_modules/superdesk-core/e2e/server/dump/full/main` into `dump/full/autodocs-base`, renaming the database folders to this instance's database names. The seed scripts were written on top of that data (users `samgamgee` and `frodobaggins`, desk Sports, `story 2` and so on).
2. If the database already carries the seed marker for `SEED_VERSION`, it makes sure the snapshot files are on disk (see below) and stops there.
3. Otherwise it waits for the API on `http://localhost:5000/api`, clones `tools/screenshots` from the docs repo (branch `main`, sparse and shallow) and seeds with admin / admin:
   - `seed_planning.py --reset`: wipes the database, loads the `planning_prepopulate_data` profile and seeds the planning data. Saved as snapshot `autodocs-planning`.
   - restores `autodocs-base`, then `seed.py` and `seed_broadcasting.py`. Saved as snapshot `autodocs`. This is the state the instance is left in.
4. It stores both snapshots as one archive in the `<db>_autodocs` Mongo database and writes the marker there.

A snapshot is a full dump in `server/dump/full/<name>/` plus a record in `server/dump/records/<name>.json.bz2` that points at it, the same layout client-core's e2e stack uses for `main`. `POST /api/restore_record {"name": "<name>"}` drops the four Superdesk databases, loads the dump and rebuilds the Elasticsearch index.

A push replaces the container, so the files under `server/dump` are gone after every redeploy while Mongo stays. On the next start the script finds the marker and unpacks the archive from Mongo, so the snapshots are always the ones taken right after seeding, not a copy of whatever the database looks like by then.

## Seeding again

- Bump `SEED_VERSION` in `run_seed.sh` and push. The next start wipes the database and seeds from the docs repo's current `main`. Do this after the seed data changed.
- Or press "reset db" for the instance on https://test.superdesk.org/. That drops every database of the instance, the marker and archive included, and the restart seeds from scratch.

Seeding takes a few minutes after the API is up. Follow it in the instance log (lines start with `[autodocs-seed]`).

Settings, all optional, read from the environment: `AUTODOCS_DOCS_REF` (branch or tag, default `main`), `AUTODOCS_DOCS_REPO`, `AUTODOCS_DOCS_PATH` (default `tools/screenshots`), `SUPERDESK_USER` / `SUPERDESK_PASSWORD` (default admin / admin; both base datasets only know admin / admin), `AUTODOCS_SEED=0` to switch the seed off, `AUTODOCS_SEED=1` to force it outside Fireq (it wipes the database).

## Restoring a snapshot from a laptop

```sh
curl -X POST https://sd-autodocs.test.superdesk.org/api/restore_record \
  -H 'Content-Type: application/json' -d '{"name": "autodocs"}'
```

Names: `autodocs` (newsroom, broadcasting), `autodocs-planning` (planning pages), `autodocs-base` (the bare e2e data, for seeding again from a laptop). A restore logs everybody out.

The seeds date schedules, embargoes, rundowns and planning items relative to the day they run, and locks belong to sessions that expire. A snapshot is therefore exact only on the day it was taken. For shots that depend on dates or locks, restore `autodocs-base` and run the seeds against the instance on the capture day; `tools/screenshots/run-capture-autodocs.sh` in the docs repo does that with `FRESH=1`.

## Keeping the instance

Fireq removes test instances that are not on its cleanup whitelist. `sd-autodocs` has to be added there (ticket to Ivan).

The restore, prepopulate and planning_prepopulate endpoints need no login, the same as on the e2e stacks. Anyone who finds the instance can reset its data, which is acceptable for a demo instance with admin / admin, but keep anything that matters off it.
