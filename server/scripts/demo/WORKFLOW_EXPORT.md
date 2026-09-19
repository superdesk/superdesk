# Workflow data export

A small read-only tool that answers the workload question a security intelligence prospect asked us: how much work goes through the desk, when does it converge, how long do briefs wait for a reviewer, and who was available. It exports Superdesk's own workflow record to CSV and renders a single-file HTML report from it.

Nothing here is a product change. It is three standalone scripts plus a shared module, standard library Python 3 only, talking to a running instance over the public REST API with GET requests. The export cannot modify an instance: the only non-GET call it makes is the login.

## What it reads

Superdesk records every operation on an item in `archive_history`, a resource that only supports GET. There is nothing to read unless work actually moved: the `workflow` section of `seed_superdesk.py` walks ten reports through the stages as the named staff so the demo instance has that record. See the seeder's README. Each record carries `item_id`, `user_id`, `operation`, `version`, `_created` and an `update` dictionary holding the fields that changed. Stage moves are written with operation `move`; the others seen in practice are `create`, `fetch`, `update`, `publish`, `spike`, `mark`, `item_lock` and `item_unlock`. The export resolves team, stage, user and report type ids to names, and joins item metadata (reference, title, report type, severity, priority, urgency) from `archive` and `published`.

## Files

| File | What it is |
|---|---|
| `workflow_export.py` | Reads a live instance and writes the three CSVs. Optionally renders the report. |
| `workflow_sample.py` | Generates a deterministic synthetic month in the same CSV format. No instance involved. |
| `workflow_report.py` | Renders `report.html` from a directory holding the three CSVs. |
| `workflow_common.py` | The CSV shapes, time handling, and the derivation of stage visits and hourly review load. Both the live export and the sample go through it, so both sets of numbers are produced by identical code. |

Outputs live in `Briefdesk/workflow-export/live/` and `Briefdesk/workflow-export/sample/`, each holding `events.csv`, `stage_intervals.csv`, `review_load_by_hour.csv` and `report.html`.

## Running it

From `Briefdesk/superdesk/server/scripts/demo`.

Live export plus report:

```
SUPERDESK_URL=https://sd-hgbriefdeskdemo.test.superdesk.org \
SUPERDESK_USER=admin SUPERDESK_PASSWORD=admin \
python3 workflow_export.py --out ../../../../workflow-export/live --report
```

Sample month plus report:

```
python3 workflow_sample.py --out ../../../../workflow-export/sample --report
```

Re-render a report without touching the data:

```
python3 workflow_report.py --in ../../../../workflow-export/live \
    --source-label "Live export from https://sd-hgbriefdeskdemo.test.superdesk.org"
python3 workflow_report.py --in ../../../../workflow-export/sample --sample
```

### workflow_export.py options

- `--url`, `--user`, `--password`, or the environment variables `SUPERDESK_URL`, `SUPERDESK_USER`, `SUPERDESK_PASSWORD`. These are the same variables the demo seed uses.
- `--since`, `--until`. Either `YYYY-MM-DD`, which means local midnight, or a full ISO timestamp. `--until` on a bare date means the end of that day.
- `--team NAME`, repeatable. Keeps only events whose team resolves to one of the given names.
- `--out DIR`, default `workflow-export/live`.
- `--timezone NAME`, default `Europe/Prague`. Sets the local column and the hours the hourly table is bucketed into.
- `--review-stage NAME`, repeatable, default `Review`. Which stage names count as review. Stage names repeat across teams, so this matches by name in any team.
- `--exclude-locks` drops `item_lock` and `item_unlock` rows. They are kept by default because they are the only signal of who had an item open.
- `--report` also writes `report.html` into the output directory.
- `--insecure` skips TLS verification.

### workflow_sample.py options

`--out`, `--seed` (default 20260918), `--start` (default 2026-08-17), `--days` (default 28), `--timezone`, `--alerts-per-day` (default 26), `--report`. Same seed, same output, byte for byte.

## The CSV columns

### events.csv, one row per workflow event

| Column | Meaning |
|---|---|
| `timestamp_utc` | When the event was recorded, ISO 8601 with a UTC offset. This is `_created` on the history record. |
| `timestamp_local` | The same instant in the timezone passed to `--timezone`. |
| `item_id` | The item's guid. Stable across the whole lifecycle, including after release. |
| `item_reference` | The item's Reference (Superdesk `slugline`). Blank for ingested items that never got one. |
| `title` | The item's Title (Superdesk `headline`). |
| `report_type` | The content profile's label, for example Alert or Daily Brief. Falls back to the item type for items with no profile. |
| `severity` | The value of the `severity` custom vocabulary, read from `subject[]` where `scheme` is `severity`. Blank when not set. |
| `priority`, `urgency` | Superdesk's native numeric priority and urgency, if set on the item. |
| `operation` | The history operation. `move` is a stage move, `publish` is a release, `spike` is an archive, `create` and `fetch` bring an item into a stage. |
| `team` | The team (desk) the item was in after the event. |
| `from_stage` | The stage the item was in before the event. Derived, see the limits below. |
| `to_stage` | The stage the item was in after the event. |
| `user` | Display name of the user the operation was recorded against. Blank for system operations such as ingest. |
| `version` | The item version the history record carries. |

### stage_intervals.csv, one row per item per stage visit

| Column | Meaning |
|---|---|
| `item_id`, `item_reference`, `title`, `report_type`, `severity`, `team` | As above, carried from the event that opened the visit. |
| `stage` | The stage being visited. |
| `entered_at_utc`, `entered_at_local` | When the item arrived in the stage. |
| `entered_by` | Who moved it in. |
| `entered_operation` | The operation that put it there, usually `move`, or `create` and `fetch` for the first stage. |
| `left_at_utc`, `left_at_local` | When it left. For a visit that was still running when the export was taken, this is the export horizon. |
| `left_by`, `left_operation` | Who moved it on and how. Blank for a visit that had not ended. |
| `duration_minutes` | Wall clock minutes in the stage, one decimal. Never negative. |
| `still_open` | `yes` when the visit had not ended, so the duration is a lower bound measured to the export horizon. |

This is the file that answers "how long did briefs wait in Review": filter `stage` to Review and read `duration_minutes`.

### review_load_by_hour.csv, one row per hour of the local day

| Column | Meaning |
|---|---|
| `hour_local` | Hour of the day, 00 to 23, in the export timezone. |
| `entered_review` | Number of review visits that started in that hour, summed over every day in the export. |
| `queue_end_of_hour_avg` | Average number of items sitting in a Review stage at the end of that hour, averaged over the days in range. |
| `queue_end_of_hour_max` | The worst single day's queue at the end of that hour. |
| `median_wait_minutes` | Median time in Review for the visits that started in that hour. Completed visits only, blank when there are none. |
| `p90_wait_minutes` | The same at the 90th percentile, linear interpolation between ranks. |
| `distinct_reviewers` | Number of distinct people who acted on an item that was already in Review during that hour. The move that puts an item into Review is the analyst handing it over, so it is read from `from_stage` and does not count the analyst. |
| `days_observed` | Number of local days the export spans. The averages divide by this. |

## What is real and what is sample

`workflow-export/live/` is a real export of https://sd-hgbriefdeskdemo.test.superdesk.org, taken over the REST API. Nothing in it was invented and nothing was written to the instance.

`workflow-export/sample/` is generated by `workflow_sample.py`. It is a simulation of a month at the invented firm Halden Risk Intelligence, with invented people. It exists because the live demo instance holds a single session of seeded work: the `workflow` section of the demo seed walks ten reports through the stages with real operations, which gives the live export real stage visits, but a session of a few minutes has no daily rhythm and cannot show the 17:00 convergence a customer asked about. Fabricating a month of that history on the instance was not an option, so the sample lives entirely in files instead.

The sample's report carries a "Sample data" label in the header, on every chart, and in the page title. Both reports are produced by the same rendering code from the same CSV columns.

The sample is not random noise dressed up as data. Arrivals are shaped by hour of day, the daily client briefs are handed to review around 17:15 local, and the review queue is a genuine first come first served simulation against reviewer rotas. The afternoon backlog is what the model produces, not a number written into it: Tomas Havel is off at 17:00 and Lucia Ferro then covers three teams alone until 18:30. The staff are the five named in `CONTRACT.md` plus six more invented in the same style, because five people cannot staff a 24/7 rota and three regional teams.

## Limits of the data

These are properties of what Superdesk records, found by reading the live instance and `origin/develop`, not guesses.

- **A move does not record where the item came from.** `apps/duplication/archive_move.py` passes the whole updated item to the history service, so `update.task` holds the desk and stage the item lands in and nothing about the previous stage. The `from_stage` column is therefore derived by walking each item's own events in order. It is blank for an item's first event in the window, and `--since` truncates history, so an interval that began before the window starts with an unknown previous stage.
- **Release does not record a stage change.** A `publish` record's `update` has no `task` at all, even though the item's stage does change. A stage visit that ends in a release is therefore measured up to the release itself.
- **A stage visit that had not ended is measured to the export horizon** and flagged `still_open`. The hourly median and p90 use completed visits only, so an hour where everything is still in flight shows blank waits rather than an understated number.
- **An hour that had not finished when the export was taken has no queue figure.** `queue_end_of_hour_avg` and `queue_end_of_hour_max` are blank for it rather than zero, and the day it belongs to is left out of that hour's average. Counting it as an empty queue would read as "everything had been dealt with" in the very hour the work arrived, because every open visit is measured only up to the horizon. The report prints those cells as `n/a` and breaks the queue line rather than drawing it down to the axis.
- **Time in a stage is wall clock time.** It does not separate an item being worked on from an item waiting. The `item_lock` and `item_unlock` events are the nearest thing to "someone had this open", which is why they are exported by default.
- **Reviewer availability is inferred, not rostered.** The export can say who acted on items in Review in a given hour. It cannot say who was on shift and idle. A real capacity answer needs a roster alongside this.
- **History is deleted with the item.** `ArchiveHistoryService.on_item_deleted` removes every history record for an item that is hard deleted, so anything purged from `archive` leaves no trace. Released items keep their history, and their metadata is joined from `published`.
- **`archive_history` is not filtered by desk.** It returns every item the caller can see, so `--team` is applied after the fact, on the resolved team name.
- **Pagination.** The resource pages at 200 records per request; the export walks the pages and sorts by `_created`. `--since` and `--until` are sent as a Mongo `where` on `_created` and are also enforced locally, so a backend that ignored the filter could not widen the export.
- **Unknown stages are passed through.** A stage added after this was written shows up under its own name with no code change. If a stage id cannot be resolved to a name, the raw id is written rather than a blank.

## What the live export actually shows, and what it does not

At the time of writing the live instance holds 246 history records over 64 items, from one afternoon of seeding, a screenshot session, and one run of the `workflow` section of the demo seed.

That section is what makes the live export worth reading. It walks ten new reports through the stages with the endpoints the product itself uses, signed in as the staff the demo names, so the history has real operations in it rather than ten items conjured into their final stage. What the export finds as a result:

- **29 `move` operations**, by Omar Nasser (9), Maja Lindqvist (8), Lucia Ferro (5), Dana Reyes (4) and Tomas Havel (3). Two of them cross teams, Watch to Europe and Watch to MENA.
- **16 review visits, 8 of them completed.** Four ended in a release, four in a move back to Analysis or into Held. Waits run from 36 seconds to 20 minutes, median 3.8 minutes, p90 17.8 minutes. The eight still open are the reports the earlier sections created straight into a Review stage, which have no arrival event and are measured to the export horizon.
- **101 stage visits, 65 of them completed**, covering Incoming, Triage, Analysis, Held and Review on all four teams.
- **Two distinct reviewers** in the hour the walk ran: Tomas Havel on Europe and Americas, Lucia Ferro on MENA.
- Four releases with a named reviewer against them, which is the only part of the release path the history records: `publish` carries no stage, so the visit is closed at the release.

The walk takes minutes, not days, so the durations are minutes and everything lands inside one hour of one day. The report says exactly that and withholds a peak hour, because 16 review arrivals across two calendar days cannot support one. The live half proves the export runs against a real instance, resolves real ids, derives real stage visits with both ends, and names the people who did the work. The sample half shows the shape of the answer on a month of traffic.

Two artefacts of a demo instance are visible in the live CSVs and are not bugs: three spiked `TEST-PROBE-*` items from earlier probing, and `item_lock` / `item_unlock` pairs from the screenshot sessions, which are what make a reviewer show up in an evening hour where nothing moved.

A customer with a month of real production data could answer, from these three files alone: how many items each team handled, how long items waited in each stage at the median and the tail, which hour of the day the review queue peaks and how deep it gets, how many people were acting on review work in each hour, and which specific items waited longest and who handled them. They could not answer, without other sources: who was rostered but idle, how much of a wait was active work rather than queueing, or anything about items that have been hard deleted.
