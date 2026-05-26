---
description: Stop the local Superdesk dev stack. Data is preserved unless --volumes is passed.
---

If the user passed `--volumes` (or said something equivalent like "wipe
everything", "clean reset", "fresh start"), confirm with them first
using `AskUserQuestion`:

> Running with `--volumes` will drop the MongoDB and Elasticsearch
> volumes — all your local data is gone, and the next setup will re-run
> the first-time DB init (5–10 min). Continue?

Only proceed if they confirm. For a normal stop (no `--volumes`),
proceed directly — it's idempotent and non-destructive.

Run `./scripts/dev/down.sh $ARGUMENTS` and relay its output.

**Always relay the Docker Desktop reminder the script prints at the end**
— designers tend to forget Docker keeps running as a separate process
after the compose stack stops.
