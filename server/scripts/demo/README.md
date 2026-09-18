# Briefdesk demo seeder

One re-runnable command that turns a freshly deployed Superdesk instance into the Briefdesk demo:
taxonomies, roles, users, teams, report types, templates, sources, entitlement filtering,
recipients, a briefing list, AI actions, a client request and about thirty sample reports.

It talks to the instance over the normal REST API at `<SUPERDESK_URL>/api`. It uses the Python
standard library only, so it runs from a laptop with no virtualenv. `requests` is in
`server/requirements.txt` but that is the server's environment, not yours.

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
| `OPENROUTER_API_KEY` | no | When absent the AI section is skipped with a warning, unless the provider already exists. |
| `BRIEFDESK_AI_MODEL` | no, defaults to `openai/gpt-4o-mini` | Model the AI provider and both actions use. |

Flags:

- `--dry-run` prints every planned operation and makes no network call at all.
- `--only <section>` runs one section, repeatable. Sections are, in dependency order:
  `vocabularies roles users profiles desks templates ingest publishing highlights ai planning content`.
  A later section assumes the earlier ones have run, and fails with a clear message if not.
- `--verbose` prints each request.
- `--insecure` skips TLS verification, for a self-signed test instance.
- `--write-geo-index` regenerates `content/geo_index.json` and exits, no instance needed.

Nothing here is secret. The push key (`briefdesk-demo-push-key`) and the demo user password
(`Briefdesk-demo-1`) are deliberately silly hard-coded values. The OpenRouter key only ever comes
from the environment.

## What each section does

**vocabularies** Upserts the nine Briefdesk vocabularies read from `server/data/vocabularies.json`:
the six taxonomies (`severity`, `threat_type`, `region`, `country`, `sector`, `tlp`) and the three
custom text fields (`recommended_actions`, `location_text`, `sources`). The file is the single
source of truth; the seeder does not carry its own copy. `app:initialize_data` loads the same file
on deploy, so this section is only needed when you change a taxonomy without redeploying.

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

**templates** One template per report type per team where it matters, each with a body skeleton
(Alert: Situation, Assessment, Outlook) and prefilled region and TLP where that is obvious. Also
the highlights-type template the briefing list exports through. Finishes by pointing each team's
`default_content_profile` and `default_content_template` at the right ones.

**ingest** RSS providers for GDACS, USGS significant earthquakes and ReliefWeb, plus a routing
scheme sending everything to Watch / Incoming. The `rss` feeding service handles Atom as well
(`feedparser` underneath, and its own label is "RSS/Atom"), so the USGS Atom feed needs no special
handling and no `feed_parser`.

**publishing** Filter conditions on the custom vocabularies, one content filter per client company,
one package (product) per company plus one for the portal, and the recipients: `Briefdesk Portal`
as an HTTP push destination with format `newsroom ninjs` and `secret_token`, and one email
recipient per client company.

**highlights** The "Europe daily brief" briefing list on the Europe team, with `auto_insert` set to
`now-24h` and the highlight template attached.

**ai** The `OpenRouter` provider (`provider_type: openai_compatible`, base URL
`https://openrouter.ai/api/v1`) and two actions, "Suggest titles" (suggestion, body plus summary in,
headline out) and "Draft summary" (summary, body in, summary out), both with a system prompt written
for a risk intelligence analyst. The script prints both action ids at the end.

**planning** One programme (agenda) per client company, and one client request for Castellan Energy
as a planning item with a deliverable (coverage) assigned to `omar.nasser` on the MENA team, due in
two days. `workflow_status: "active"` on the coverage is what makes the server create a visible
tasking rather than a draft one.

**content** Creates 29 alerts, 3 daily briefs and 2 country assessments from `content/*.json` on the
right team and stage, releases the 29 that are marked `released` by publishing them through the API
so they flow to the recipients, leaves 3 in Analysis and 2 in Review, leaves a review comment on the
two in Review (signing in as `tomas.havel`, because a comment is always attributed to the session
user), and adds the Europe alerts released in the last 24 hours to the briefing list.

## Sample content

`content/alerts.json`, `content/daily_briefs.json` and `content/country_assessments.json`. All of it
is invented: real cities, fictional events, fictional companies, `.example` email domains.

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
- the client request by `slugline`

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
