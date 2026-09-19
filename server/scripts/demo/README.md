# Briefdesk demo seeder

One re-runnable command that turns a freshly deployed Superdesk instance into the Briefdesk demo:
taxonomies, roles, users, teams, report types, templates, sources, entitlement filtering,
recipients, a briefing list, AI actions, a client request, about forty sample reports, and a walk of
ten of them through the stages so the instance has real workflow history in it.

It talks to the instance over the normal REST API at `<SUPERDESK_URL>/api`. It uses the Python
standard library only, so it runs from a laptop with no virtualenv. `requests` is in
`server/requirements.txt` but that is the server's environment, not yours.

## On Fireq (automatic)

Nobody has a shell on a Fireq instance, so the branch seeds itself. `server/Procfile` has a
`seed:` entry running `scripts/demo/run_seed.sh`, which:

1. does nothing unless `DB_NAME` is set (Fireq exports it, the Docker setups here do not);
   `BRIEFDESK_SEED=1` forces it and `BRIEFDESK_SEED=0` disables it,
2. skips when the marker document `briefdesk_seed/v1` exists in MongoDB,
3. waits up to 15 minutes for the API on `http://localhost:5000/api` (honcho gives `rest`, the
   first Procfile entry, port 5000), falling back to `$SUPERDESK_URL`,
4. picks the push destination: the public portal URL if this instance can reach it, otherwise the
   portal container's internal name `http://nra-hgbriefdeskportaldemo`. Only the push destination
   changes, exported as `PORTAL_PUSH_URL`,
5. runs `python3 -u scripts/demo/seed_superdesk.py` as `admin` / `admin` (the user Fireq creates),
6. writes the marker on success, and then idles forever. It never exits, because honcho stops the
   whole instance when one Procfile process ends.

- Instance: https://sd-hgbriefdeskdemo.test.superdesk.org (Fireq strips everything but letters
  and digits from the branch name `hg/briefdesk-demo`). Login `admin` / `admin`, staff users per
  the table below with password `Briefdesk-demo-1`.
- Portal: https://nra-hgbriefdeskportaldemo.test.superdesk.org , login `admin@example.com` /
  `admin`.
- Seed output: https://sd-hgbriefdeskdemo.test.superdesk.org/logs/ , lines start with
  `[briefdesk-seed]`.
- Mail this instance sends (email recipients, notifications):
  https://sd-hgbriefdeskdemo.test.superdesk.org/mail/
- To seed again: the `[reset db]` button on https://test.superdesk.org/sd drops the database and
  with it the marker. Or bump `SEED_VERSION` in `run_seed.sh` and push (the seed is idempotent,
  so this only adds and updates).
- Push order: `hg/briefdesk-portal-demo` in newsroom-app first, then `hg/briefdesk-branding` in
  superdesk-client-core, then this branch (its `client/package.json` points at that client
  branch, so it has to exist on GitHub first).

### The OpenRouter key is pasted in by hand

A pushed branch cannot give a Fireq instance a secret, and this repository is public. Without
`OPENROUTER_API_KEY` the seed still creates the `OpenRouter` provider (with no key) and both AI
actions, and says so under "Things to look at". After the deploy, open Settings, AI providers,
edit `OpenRouter` and paste the key. Until then every AI run fails with an authorisation error
from the provider. A later seed run never touches the pasted key: the key is only sent when
`OPENROUTER_API_KEY` is set.

## Run it

```
SUPERDESK_URL=https://<instance> \
SUPERDESK_USER=admin \
SUPERDESK_PASSWORD=<admin password> \
PORTAL_URL=https://<portal instance> \
OPENROUTER_API_KEY=sk-or-... \
python3 server/scripts/demo/seed_superdesk.py
```

| Variable | Required | What it does |
|---|---|---|
| `SUPERDESK_URL` | yes | Instance URL. `/api` is appended if it is not already there. |
| `SUPERDESK_USER` | no, defaults to `admin` | Account to sign in as. Must be an administrator. |
| `SUPERDESK_PASSWORD` | yes, unless `SUPERDESK_TOKEN` | Password for that account. |
| `SUPERDESK_TOKEN` | no | An existing session token, used instead of signing in. |
| `PORTAL_URL` | no, but the portal push is useless without it | Base URL of the Briefdesk Portal. The push destination becomes `<PORTAL_URL>/push`. |
| `PORTAL_PUSH_URL` | no | Address this server uses to reach the portal, when it differs from the one a browser uses (two instances on one host). Defaults to `PORTAL_URL`. The push destination becomes `<PORTAL_PUSH_URL>/push`. |
| `OPENROUTER_API_KEY` | no | When absent the provider is created without a key and both actions are still created. Paste the key into Settings, AI providers afterwards. A key already stored is never touched. |
| `BRIEFDESK_AI_MODEL` | no, defaults to `z-ai/glm-5.3-flash` | Default model of the AI provider when the seed creates it. An existing provider is never changed, and the actions carry no model of their own, so they follow the provider's default. |

Flags:

- `--dry-run` prints every planned operation and makes no network call at all.
- `--only <section>` runs one section, repeatable. Sections are, in dependency order:
  `vocabularies roles users profiles desks templates ingest publishing highlights dashboards ai
  planning content triage workflow`.
  A later section assumes the earlier ones have run, and fails with a clear message if not.
- `--verbose` prints each request.
- `--pace <seconds>` sets how long one unit of the `workflow` schedule lasts, default 20. It is the
  only thing that decides how long that section takes and how long a stage visit lasts in the
  workflow export. `0` runs every step back to back, which is what a test wants. Nothing else in
  the seed reads it.
- `--insecure` skips TLS verification, for a self-signed test instance.
- `--write-geo-index` regenerates `content/geo_index.json` and exits, no instance needed.

Nothing here is secret. The push key (`briefdesk-demo-push-key`) and the demo user password
(`Briefdesk-demo-1`) are deliberately silly hard-coded values. The OpenRouter key only ever comes
from the environment.

## What each section does

**vocabularies** Upserts ten vocabularies read from `server/data/vocabularies.json`: the six
taxonomies (`severity`, `threat_type`, `region`, `country`, `sector`, `tlp`), the three custom text
fields (`recommended_actions`, `location_text`, `sources`) and Superdesk's own `urgency`. The file
is the single source of truth; the seeder does not carry its own copy. `app:initialize_data` loads
the same file on deploy, so this section is only needed when you change a taxonomy without
redeploying.

`urgency` is the severity level as Superdesk itself understands it. It is the only metadata field
that renders as a coloured badge in every list row and that the sort bar and the search facets
offer, which is why the demo carries severity there as well as in `subject`. The vocabulary is
relabelled to "Severity" and its five values are renamed Critical to Informational, each with a
one-letter `short` (the badge text) and the contract's severity `color` (the badge background).
The custom `severity` taxonomy keeps its qcodes and becomes "Severity (client feed)" in the editor,
because that is the copy the client portal filters on. Nothing keeps the two in step by itself:
the `triage` section does it for everything the seed knows about.

A taxonomy is a vocabulary with `service: {"all": 1}` and no `field_type`. That combination is what
`VocabulariesService.get_custom_vocabularies()` looks for, and it makes the vocabulary available as
a field in a content profile whose selected values are stored in the item's `subject` list with
`scheme` set to the vocabulary `_id`. A custom field is a vocabulary with `field_type: "text"`; its
value lives in `item["extra"][<id>]`, not at the top level.

**roles** Analyst, Reviewer, Team lead and Watch officer, each with an explicit privilege list.
Everything not listed is denied, which is how the newsroom-only modules stay out of sight. Analysts
have no `publish`, `correct`, `unpublish`, `kill` or `takedown`; reviewers have the first three;
retract and takedown stay with the team lead.

**users** The five staff users, with `password` set on creation only. Existing users keep their
password on a re-run. Desk membership and default team are set in the next section.

**profiles** Alert, Daily Brief, Country Assessment and RFI Response. Each is created bare and then
PATCHed with `editor` and `schema` in the expanded notation the content profile editor uses; the
server folds the custom vocabularies back into `subject` on save. Severity and Region are required
on Alert. Assessment bodies offer tables, links, lists, annotations, comments and suggestions.

**desks** The four teams as production desks, with their stages. A new desk arrives with a
"Working Stage" and an "Incoming Stage"; those are renamed in place (to Incoming plus Analysis, or
Incoming plus Triage for Watch) so the default incoming stage keeps its meaning, the remaining
stages are created, and the whole set is reordered. Desk members, each desk's monitoring board and
each user's default team are set here.

Stages per team: Watch gets Incoming, Triage, Held; the three regional teams get Incoming,
Analysis, Held, Review, Released. `Held` is where a significant item is captured and parked, either
because it is not corroborated yet or because it belongs in a later brief. `Released` exists only
because every released report points at it through `task.stage`; a stage group queries `archive`
and a released report lives in `published`, so the column would always be empty, and
`BOARD_HIDDEN_STAGES` keeps it off the board. Released work shows up in Team Output instead.
`STAGE_TASK_STATUS` fixes what each stage does to a linked tasking rather than letting the order of
the stage list decide it.

**templates** One template per report type per team where it matters, each with a body skeleton
(Alert: Situation, Assessment, Outlook) and prefilled region and TLP where that is obvious. Also
the highlights-type template the briefing list exports through. Finishes by pointing each team's
`default_content_profile` and `default_content_template` at the right ones.

**ingest** RSS providers for GDACS, USGS significant earthquakes and ReliefWeb, plus a routing
scheme sending everything to Watch / Incoming. The `rss` feeding service handles Atom as well
(`feedparser` underneath, and its own label is "RSS/Atom"), so the USGS Atom feed needs no special
handling and no `feed_parser`.

**publishing** Filter conditions on the custom vocabularies, one content filter per client company,
one package (product) per company plus two for the portal, and the recipients: `Briefdesk Portal`
as an HTTP push destination with format `newsroom ninjs` and `secret_token`, `Briefdesk Portal
calendar` with `json_event` and `json_planning` destinations to the same URL, and one email
recipient per client company.

The portal needs two recipients rather than one: Superdesk matches a recipient's packages once and
then hands the item to every destination that recipient owns, and the Newsroom NINJS formatter
accepts an event as readily as a report, so a single recipient would push a wire-shaped duplicate
of every calendar entry under the same guid. Two packages filtered on `type` (`text` for reports,
`event,planning` for the calendar) keep each kind on its own recipient.

The pushed payload carries a `products` array of the packages the item matched, which is what the
portal maps to its own products through `sd_product_id`. The client entitlement packages match
events and requests too, so a calendar entry tagged region `europe` plus sector `logistics` arrives
carrying the Nordfreight package alongside the calendar one.

**highlights** The "Europe daily brief" briefing list on the Europe team, with `auto_insert` set to
`now-24h` and the highlight template attached.

**ai** The `OpenRouter` provider (`provider_type: openai_compatible`, base URL
`https://openrouter.ai/api/v1`) and two actions, "Suggest titles" (suggestion, body plus summary in,
headline out) and "Draft summary" (summary, body in, summary out), both with a system prompt written
for a risk intelligence analyst. The script prints both action ids at the end.

**planning** One programme (agenda) per client company, the `event_calendars` vocabulary rewritten
to Political, Labour, Legal, Trade and industry and Security, 17 risk calendar entries (15 single
plus two weekly series, so 26 event documents), 14 client requests and 21 deliverables with their
taskings.

Dates are computed at run time from the day of the run, so the calendar and the due times always
look current. Entries carry a location with geo coordinates, an occurrence status from
`eventoccurstatus` and one calendar. A recurring entry is posted as one event with
`dates.recurring_rule`; the server generates the whole series and ignores a client `guid`, so the
stable lookup key for an entry is its `slugline`, not its id.

`workflow_status: "active"` on a coverage is what makes the server create a visible tasking rather
than a draft one. Taskings are then walked to their demo state through the real endpoints:

- `POST assignments/content` with `assignment_id` and `template_name` starts work and creates the
  report from the team's template. It assigns the tasking to whoever called it, so the seed signs
  in as the assignee for this one step and keeps the admin session for everything else.
- `PATCH assignments/complete/<id>` completes it. Admin may complete another user's tasking and the
  assignee is kept, so this runs on the admin session.
- `POST assignments/link` with `reassign: false` hands an already released report to a deliverable.
  The tasking goes straight to completed and the Planning view shows the delivered report. The
  report must not already be linked and the tasking must not have had work started on it.

Entries and requests marked `post` are released to the portal through `events/post` and
`planning/post` with `pubstatus: "usable"`; a recurring entry is posted with `update_method: "all"`.
The client RFIs and the two internal coordination meetings stay unposted, which is what keeps them
inside Halden.

**content** Creates 29 alerts, 3 daily briefs and 2 country assessments from `content/*.json` on the
right team and stage, releases the 29 that are marked `released` by publishing them through the API
so they flow to the recipients, leaves 3 in Analysis and 2 in Review, leaves a review comment on the
two in Review (signing in as `tomas.havel`, because a comment is always attributed to the session
user), and adds the Europe alerts released in the last 24 hours to the briefing list.

**triage** The severity layer, kept apart from `content` because `content` releases what it creates
and must never be run twice on a live instance. Everything here creates only what is missing or
patches what is wrong, so it is safe to re-run:

- upserts the `urgency` and `severity` vocabularies, so `--only triage` alone is enough after a
  change to either,
- creates the eight reports in `content/triage_items.json`, two of them in Held on Europe and
  Watch and the rest spread across Analysis and Review so a severity sort has something to show,
- walks every unreleased report and sets `urgency` (and `priority`) from its severity, adding the
  severity a report created from a tasking template never had, per `TRIAGE_SEVERITY`. Released
  reports are left alone: they already carry the right urgency, and the only way to change one is a
  correction, which would push it to the portal a second time,
- creates the global saved search "Needs review now", covering the Review stage of all three
  regional teams, ordered most severe first,
- creates a custom workspace named Triage for the team lead and for whoever runs the seed, with
  that saved search as its only monitoring group.

Sorting is the one part that is not data. Superdesk keeps the active sort in the URL
(`?sort=urgency:asc`), not on the saved search and not in a user preference. Opening the saved
search from the Search view replaces the URL query with `filter.query`, so the `sort` stored there
does take effect. Monitoring ignores it and uses `monitoring.stage.sort` from
`client/superdesk.config.js`, which sets every stage column to severity first and offers the
alternatives under "Sorting" in each column header. That part only exists once the client is built.

**workflow** Ten new reports walked through the stages with the operations the product itself uses,
signed in as the people who would do it. Every other section creates a report directly in the stage
it ends up in, which leaves `archive_history` with no `move` at all and the workflow export with no
stage visit that has both a beginning and an end. This is the section that puts real workflow on the
instance.

The reports are in `content/workflow_items.json`. Each one carries the usual report fields plus a
schedule: an `at` for the create and an `at` on every step, both counted in units of `--pace`. The
section flattens all ten schedules into one list and runs it in time order, so several reports sit
in Review at the same time and their visits overlap the way a shift does. At the default pace of 20
seconds the whole section is 55 operations over about six and a half minutes.

The steps are the real endpoints:

- `POST archive` as the analyst, so the `create` record carries their name.
- `POST archive/<guid>/move` with `task.desk` and `task.stage`, which is what the Send to panel
  calls. `MoveService` refuses a move within the same stage and sets the item to `submitted`. The
  desk membership check in `send_to` is waived for anyone holding the `move` privilege, which every
  Briefdesk role does.
- `PATCH archive/<guid>` with a real change to the body, so the item gains a version.
- `PATCH archive/publish/<guid>` as the reviewer, through the same helper the `content` section
  uses, so a release here reaches the portal and the entitled client companies exactly as one from
  the demo script does. Four of the ten are released.

Outcomes vary on purpose: four released, two sent back from Review to Analysis and resubmitted, one
parked in Held and brought back, one parked in Held by the reviewer at the end, two left waiting in
Review so the "Needs review now" queue stays populated, and one of those two is Critical. Two of the
ten start on Watch and are handed to a regional team, which is the only way the export sees a move
between two teams.

Nothing is ever locked: every step is a plain API call, and a lock is what the editor takes, not the
API.

The section is idempotent and resumable, and it reads its progress back from the instance rather
than remembering it. Per report: a `publish` record in `archive_history` means the walk is finished,
because a release is always the last step; the number of `move` records says how many move steps are
done; an edit is recognised by the text it adds being in the body already. A run stopped halfway
carries on from the first step that has not happened.

## Sample content

`content/alerts.json`, `content/daily_briefs.json` and `content/country_assessments.json`, plus
`content/triage_items.json` and `content/workflow_items.json`. All of it is invented: real cities,
fictional events, fictional companies, `.example` email domains.

Every item is dated relative to the moment you run the script, through `hours_ago`, so the demo is
always current. Severity spread is 3 critical, 9 high, 12 medium, 3 low, 2 informational. Eight
alerts concern Poland or Germany logistics, and three are High severity in Poland, so the portal's
"High severity, Poland" saved topic fires.

Entitlement coverage, which is the point of beat 8 of the demo script:

| Company | Entitlement | Alerts that match | Alerts that do not |
|---|---|---|---|
| Nordfreight Logistics | `region europe` and `sector logistics` | 11 | 18 |
| Aurelia Pharma | `region europe` or `mena`, and `sector pharma` | 5 | 24 |
| Castellan Energy | `region mena` and `sector energy` | 7 | 22 |

`_demo_geo` on each alert holds the latitude and longitude. The script never sends it to Superdesk.
It writes the combined list to `content/geo_index.json` on every run (also on `--dry-run`), for the
portal's map mock: `reference`, `title`, `severity`, `lat`, `lon`, `country`, `region`, `sector`,
plus the full `countries` / `regions` / `sectors` lists and the `workflow` state.

## Re-running and resetting

Every object is looked up first and then created or patched:

- vocabularies, report types by `_id`
- roles, teams, templates, briefing lists, filter conditions, content filters, packages, recipients,
  sources, routing schemes, AI providers and actions, programmes by `name`
- users by `username`
- reports by a deterministic `guid`: `urn:briefdesk:demo:<reference>`
- risk calendar entries, client requests and deliverables by `slugline`

An existing calendar entry or request is left as it is apart from its `subject`, which the seed
keeps in step with the taxonomies here because those values decide which client company sees the
entry in the portal. A tasking already past its demo state is left alone, so a re-run never sends a
completed tasking back to To Do.

Running it twice changes nothing the second time. There is no delete: to reset, redeploy the
instance. Deleting the sample reports by hand means archiving (spiking) them, which does not free
the guid, so a partial manual cleanup plus a re-run will not recreate them.

Anything the script could not do is printed at the end under "Things to look at" rather than being
buried in the log.

## Known limitations

- **Existing reports are not updated.** If a report with the same reference already exists the
  script leaves it alone, whatever state it is in. Editing the JSON and re-running will not change
  what is on the instance. Redeploy, or change the reference.
- **Comments are item-level, not inline.** The inline comments and tracked changes that beat 5 of
  the demo shows live are editor3 constructs stored in `fields_meta`, which is not something worth
  synthesising. The script leaves a normal item comment on the two reports in Review instead.
- **`versioncreated` may be reset on release.** `firstcreated` and `versioncreated` are set
  explicitly on creation, which the server honours (`update_dates_for` uses `setdefault`). Some
  update paths reset `versioncreated` to now, so released items may all carry a similar release
  time even though their creation times are spread. The briefing list uses `now-24h`, so this does
  not break it.
- **Field labels.** Custom field labels come from the vocabulary `display_name` and appear in the
  editor. Core field labels (Title for headline, Reference for slugline, Summary for abstract) are
  set as `field_name` in the profile, which the content profile configuration screen uses, but the
  authoring form itself takes them from the translation layer. The terminology pack in
  `client/superdesk.config.js` is what actually renames them in the editor.
- **Qcodes must stay unique across taxonomies.** A filter condition on a custom vocabulary is
  matched by `FilterConditionControlledVocabularyField`, which checks that the item has *some*
  subject entry with the right scheme and, separately, that *some* subject qcode is in the value
  list. The two checks are not tied together. The contract's qcodes are all distinct across the six
  taxonomies, so this is correct today, but adding a qcode that already exists under another scheme
  would silently over-match.
- **`skip_config_test: true` on the sources.** Creating an RSS provider normally fetches and parses
  the feed, and a proxy or a slow feed fails the whole POST. The test is skipped so seeding is
  deterministic. Check in Settings, Sources that each provider is actually ingesting.
- **The AI provider stores its key unencrypted** and `ai_studio` is write access to it. Every demo
  role has `ai_studio`, because listing `/ai_actions` requires it and the editor glue lists before
  it runs. That is a demo trade-off, not a recommendation.
- **Tier packages (Awareness, Alerting, Advisory, Analyst) are portal products**, per the contract,
  and are not created here. Superdesk holds the per-company entitlement packages only.
- **Nothing is verified against a running instance.** Every payload shape was checked against
  `origin/develop` of superdesk-core and superdesk-planning, but no instance existed when this was
  written. Expect to fix something on the first real run.
