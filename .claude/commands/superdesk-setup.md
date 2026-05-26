---
description: Set up the local Superdesk dev environment (first-time install + link siblings + first-run DB init).
---

**Before running anything**, check that both required sibling repos
exist:

```bash
ls ../superdesk-client-core/package.json ../superdesk-planning/package.json
```

If either is missing, STOP and tell the user exactly which one is
missing, with the exact git clone command to copy-paste from the
parent directory:

```
cd ..
git clone https://github.com/superdesk/superdesk-client-core.git
git clone https://github.com/superdesk/superdesk-planning.git
```

Don't run setup.sh until both are present — it will error out after
some work has already started. (Optional repos: superdesk-analytics,
superdesk-publisher. Skip unless the user explicitly wants them.)

If both siblings exist, run `./scripts/dev/setup.sh $ARGUMENTS` and
relay its output to the user.

The script accepts these flags (pass them through verbatim if the user
specified any): `--only <names>`, `--skip <names>`, `--link <abs-path>`,
`--reinit`.

If the script reports other known failure modes (Docker not running,
Volta missing, first-run init failure), refer to
`.claude/skills/superdesk-dev/SKILL.md` for how to communicate them.
Do not try to fix the underlying issue yourself.

On success: tell the user the backend is now running and they can start
the client with `/superdesk-up` (or by asking Claude to "start
superdesk"). Mention the admin credentials (admin / admin).
