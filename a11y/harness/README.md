# Accessibility harness

Measuring tools for the Superdesk authoring portal and the Newshub partner portal: an axe sweep with scripted WCAG 2.2 AA checks per role and page, and screen reader flows run with VoiceOver, NVDA and Guidepup's Virtual Screen Reader. Nothing here changes the instance: every non-GET request the apps send is aborted (see `readOnlyGuard` in `lib/instance.ts`), except logging in and locking or unlocking an item, and an item opened in the editor is closed again (with a fallback to the unlock endpoint if the Close button fails).

## Setup

```sh
cd a11y/harness
npm ci
npx playwright install chromium
```

VoiceOver flows also need the Mac prepared once for VoiceOver automation: `npx @guidepup/setup` (it enables AppleScript control of VoiceOver and writes VoiceOver's preferences; it changes system settings, so run it only with the machine owner's approval). NVDA runs on GitHub Actions, see `../workflows/a11y-nvda.yml`.

## Environment

Passwords stay in the environment; never write them into a file in this folder.

| Variable | Used by | Meaning |
|---|---|---|
| `SD_URL`, `NH_URL` | all | Superdesk and Newshub base URLs, no trailing slash |
| `SD_USER_REPORTER`, `SD_PASS_REPORTER` | a11y | Superdesk reporter |
| `SD_USER_REVIEWER`, `SD_PASS_REVIEWER` | a11y, screen reader flows | Superdesk reviewer |
| `SD_USER_ORGADMIN`, `SD_PASS_ORGADMIN` | a11y | Superdesk organisation administrator |
| `SD_USER_SYSADMIN`, `SD_PASS_SYSADMIN` | a11y | Superdesk system administrator |
| `NH_USER_PARTNER`, `NH_PASS_PARTNER` | a11y, screen reader flows | Newshub partner user |
| `NH_USER_ADMIN`, `NH_PASS_ADMIN` | a11y | Newshub administrator |
| `SD_SAMPLE_ITEM` | a11y | item id the reporter opens in the editor (a draft of theirs) |
| `SD_REVIEW_ITEM` | a11y, screen reader flows | item id in Review Pending that the reviewer opens; the flows expect it to be the first item there |
| `NH_SAMPLE_ITEM` | a11y | published item id opened in the Newshub item view |
| `NH_FILTER_AUTHORITY` | screen reader flows | local authority ticked in the Newshub filter flow (default `Kirklees Council`) |

On the demo pair the accounts are the reporter, reviewer, organisation administrator and system administrator of the first partner, the partner's Newshub user and the Newshub admin; the private credentials file of the market folder has them.

## Specs

| Spec | Runs | Time | Output |
|---|---|---|---|
| `a11y.spec.ts` | headless, anywhere | about 4 to 5 minutes for 27 targets | `out/<role>/<page>/`, `out/summary-by-sc.json`, `out/summary-checks.json` |
| `virtual-sr.spec.ts` | headless, anywhere | about 1.5 minutes | `out/virtual-sr/superdesk.txt`, `out/virtual-sr/newshub.txt` |
| `voiceover.spec.ts` | headed, macOS with VoiceOver automation; speaks aloud and takes the keyboard | a few minutes per flow | `out/voiceover/*.txt` |
| `nvda.spec.ts` | headed, Windows with NVDA (GitHub Actions) | a few minutes per flow | `out/nvda/*.txt` |

Always run with one worker, because the targets and flows open the same items in the editor:

```sh
npx playwright test a11y.spec.ts --workers 1 --reporter list
npx playwright test a11y.spec.ts --workers 1 --reporter list -g "reviewer /"   # one role
npx playwright test virtual-sr.spec.ts --workers 1 --reporter list
npx playwright test voiceover.spec.ts --workers 1 --reporter list -g newshub   # one VoiceOver flow
```

`look/` holds screenshot specs and `proof/` small demonstration specs and throwaway scans written by the fixing agents; neither is part of the measurement.

## a11y.spec.ts

Each target is a role, an app, a path and optionally a `prepare` step that opens a dialog or panel before the scan and a `cleanup` step that closes it without acting. Targets: Superdesk login, monitoring, personal space, the editor (reporter's draft), the editor's media upload dialog, search, the reviewer's monitoring, editor, Send to panel and Publish panel, user management and the user edit form, workgroups, vocabularies, content profiles and the Story profile editor, templates, user roles; Newshub login, home wire, item view, item view with the download dialog, saved items, My Wire Topics, My Profile, companies, products. The partner account gets 403 on `/company_admin`, so the company admin users page is not scanned.

Each role logs in once per worker; its session (storage state) is kept in memory and reused by its later targets.

Files per target, in `out/<role>/<page>/`:

- `axe.json`: the full axe result (`violations`, `passes`, `incomplete`) with WCAG 2.0, 2.1 and 2.2 A and AA tags. Each violation node has `html`, `target` and `failureSummary`.
- `checks.json`: scripted checks for what axe does not cover. They are signals for a human to confirm, not verdicts.
  - `lang`, `title` (3.1.1, 2.4.2).
  - `targetSize` (2.5.8): every visible, enabled interactive element under 24 by 24 CSS px with its name and size. `spacingOk` is the spacing exception (a 24 px circle on its centre touches no other target), `inline` the in-sentence link exception; `failingCount` counts the ones that meet neither.
  - `headings` (1.3.1, 2.4.6): the outline in DOM order (level, text, visible) and `issues` (no level 1, more than one level 1, skipped levels, empty headings).
  - `landmarks` (1.3.1, 2.4.1): counts per landmark role and `missing` among `main`, `navigation`, `banner`.
  - `ariaExpanded` (4.1.2): controls that open a menu or panel (`aria-haspopup`, dropdown and collapse toggles, `aria-controls`) and the ones without `aria-expanded`.
  - `loginAutocomplete` (1.3.5): username, e-mail and password fields with their `autocomplete` value, only on pages with a visible password field.
  - `liveRegions`, `liveRegionDetails` (4.1.3): elements with `aria-live`, `role=status|alert|log` or `output`.
  - `reflowHorizontalScroll` (1.4.10) at 320 by 256 CSS px.
  - `tabWalk` (2.1.1, 2.4.3, 2.4.7, 2.4.11, 2.4.13): 60 Tab presses, each with the focused element, its outline and box-shadow, `fullyCovered` (focus not obscured), and the focus ring colour (`ringSource`, `ringColor`), the background around it (`ringBackground`, translucent layers composited) and their contrast (`ringContrast`). `noVisibleOutlineCount` counts stops with neither outline nor box-shadow; `lowContrastFocusCount` counts stops whose ring is below 3:1. The ring is read from the focused state only, so a decorative box-shadow that does not change on focus is reported as if it were the ring; confirm on the screenshot.
  - `possibleTrap` (2.1.2): the last 20 stops cycle over two elements or fewer.
  - `blockedWrites`: requests the read-only guard aborted while the target was open.
- Screenshots: `page.png` (as scanned, full page), `reflow-320.png`, `zoom-200.png` (640 px wide, the 200 percent equivalent), `text-spacing.png` (WCAG 1.4.12 values injected), `forced-colors.png` (Windows high contrast emulation).

Run-level files:

- `out/summary-by-sc.json`: axe violations grouped by success criterion: `{ "1.4.3": [{role, page, rule, impact, nodes}], ... }`. Rules without a WCAG tag go under `best-practice`.
- `out/summary-checks.json`: the headline counters of every `checks.json` per page, and `missing` (targets with no output in this run).

Both summaries are rebuilt from the files on disk at the end of the run, so a target that failed keeps no stale result and shows up in `missing`.

## Screen reader flows (`sr/flows.ts`)

The same two flows run with each reader:

- Superdesk, reviewer: read the login page from the top, Tab to username and password (typed by Playwright, so passwords never pass through the reader's echo), Enter to log in, Tab to Monitoring and Enter, Tab to the first item in Review Pending, Enter to open it, move by headings to the editor and read the title and the first field labels, move back to Close and activate it.
- Newshub, partner: read the login page, log in the same way, Tab to Wire, open the filter panel and the Filters tab, tick one local authority with Space, apply with the panel's Search button, Tab to the first result and press Enter to open it (falls back to a mouse click when the keyboard cannot open it, and says so), Tab to Download, close with Escape or the Close button.

Each transcript lists, per step, the phrases the reader spoke (`>`) and notes (`!`): where focus landed, and `FLAG:` lines for steps where nothing was spoken, elements spoken as a bare role with no name, focus lost to the page body, and keyboard actions that did nothing. Passwords are redacted from every phrase.

The Virtual Screen Reader computes speech from the accessibility tree in the page. It follows real focus changes from Playwright's key presses and announces live regions, but it is not a real reader: it does not know about hidden content the way VoiceOver does, and it reads a password field as its label only. Use it for regressions and quick coverage; confirm with VoiceOver and NVDA.

## Comparing two runs

Keep each run's `out/` under a dated or named folder (`out-baseline-pre-theme/` and `out-post-theme/` are the runs before and after the ink-blue theme), then:

```sh
node compare.mjs out-post-theme out
```

It prints, per page, every axe rule whose node count changed (`before -> after (delta)`), pages that are new or missing in the second run, totals per success criterion, and, when both runs have `summary-checks.json`, the scripted-check counters that changed. Either argument can be a run folder or a `summary-by-sc.json` file.

Pages whose route or prepared state changed between two runs are not comparable one to one: in `out-baseline-pre-theme/` and `out-post-theme/`, `orgadmin/users` scanned `/#/settings/users`, which renders an empty page, and the two authoring targets scanned monitoring because the edit deep link does not open the editor.
