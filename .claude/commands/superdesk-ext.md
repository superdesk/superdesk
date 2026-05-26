---
description: Manage in-tree Superdesk extensions. Usage: list | enable NAME | disable NAME.
---

Run `./scripts/dev/extension.sh $ARGUMENTS` and relay its output.

Common usages:
- `/superdesk-ext list` — show what's available and what's currently enabled.
- `/superdesk-ext enable <name>` — turn on an in-tree extension.
- `/superdesk-ext disable <name>` — turn off an in-tree extension.

If the user invoked this without arguments, default to `list` so they
can see their options.

Known refusals (the script names them — relay verbatim):
- `auto-tagging-widget` is on the legacy build path; the script refuses
  to enable it. Don't argue with the script's refusal.
- `planning-extension` and `broadcasting` live outside the managed
  region (they have custom-load logic). The script will refuse to
  toggle them with an INFO message. If the user really needs to change
  them, point them at `client/index.ts` and the section above the
  `// extensions:start` marker.

After a successful enable/disable, tell the user grunt's watch picks up
the `client/index.ts` change automatically — they should refresh the
browser after a few seconds to see the result. No restart needed.
