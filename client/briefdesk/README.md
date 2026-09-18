# Briefdesk client files

Everything in this folder is specific to the Briefdesk demo instance. The rest of `client/` is the
stock Superdesk distribution.

## Files

### `terminology.js`

The English terminology pack: a plain object of exact newsroom msgid to Briefdesk replacement
("Desk" to "Team", "Publish" to "Release", and so on). `client/superdesk.config.js` requires it and
merges it into `langOverride.en`, which `scripts/init.ts` in superdesk-client-core copies over the
loaded translations at startup.

Two things to know about it:

- `langOverride` is exact match on the msgid. A string that differs by a character, or one built at
  runtime, is not replaced. Expect a sweep with screenshots to catch the misses.
- Webpack only registers `superdesk.config.js` itself as a build dependency, not the modules it
  requires, so editing the pack does not invalidate the build cache. Restart the build, or delete
  `client/node_modules/.cache`, after changing it.

### `ai-actions.ts`

Glue between the `ai-widget` extension that ships with superdesk-client-core and the `ai_actions`
resource of superdesk-core. `client/index.ts` registers the extension and passes
`configureAiWidget` to its `configure()` hook, which fills in the `generateHeadlines` and
`generateSummary` callbacks the widget calls.

Each call:

1. `GET /api/ai_actions` and takes the first active action of type `suggestion` (headlines) or
   `summary` (summary). The seed script creates those as "Suggest titles" and "Draft summary".
2. `POST /api/ai_actions/<id>/run` with `{item_id, language, source: "authoring", fields}`, where
   `fields` carries the text the editor currently holds for `headline`, `slugline`, `abstract` and
   `body_html`. The server uses those instead of the stored item for whichever fields the action
   lists in its own `input_fields`, and ignores the rest.
3. Returns `suggestions[].text` from the response. Headlines get the list, summary gets the first
   entry.

Demo hacks and limits in this file:

- **It is a hack by design.** The planned integration (SDESK-7996) is a data driven widget that
  lists the actions the content profile allows. This one hard-codes one action per widget feature,
  which is why it is on the ledger as a branch hack.
- **Privileges.** Running an action needs the `ai` privilege; *listing* `ai_actions` needs
  `ai_studio`, which analysts should not normally have. If the demo users do not hold `ai_studio`,
  paste the two action ids into `ACTION_IDS` at the top of the file and the lookup is skipped.
- **Translations are deliberately not configured**, so the widget shows only Headlines and Summary.
- **Errors** are notified through `superdesk.ui.notify.error` before the promise is rejected,
  because the widget renders any rejection as a bare "there was an error" panel.
- **Applied answers are reported as accepted.** A run answers with an `event_id`. The
  `hg/briefdesk-branding` branch of superdesk-client-core adds an optional `onAnswerApplied`
  callback to the widget's configuration (and an Apply button on the Summary panel that writes to
  `abstract`), and this glue answers it with `PATCH /api/ai_events/<event_id>` and
  `{"outcome": "accepted", "applied_index": <n>}`. Runs whose answers are never applied stay
  `pending`; `edited` and `discarded` are not reported.
- **The text sent is whatever the widget hands over**: `itemWithChanges` in React authoring (so
  autosaved edits are included) and the scope item in Angular authoring. Edits made in the last
  keystrokes before pressing the button may not be in it.
