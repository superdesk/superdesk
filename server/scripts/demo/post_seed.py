"""Finishing touches the seed engine cannot express, applied over the REST API.

Run after ``run_seed.sh`` or ``build.py superdesk seed``:

    SUPERDESK_URL=https://<host>/api SUPERDESK_USER=admin SUPERDESK_PASSWORD=... python3 post_seed.py [--only STEP ...]

Steps, in order: stages (board order Draft first, global read off), states (seeded items
from ``fetched`` to ``in_progress``), scheduled (one story published with an embargo
time), revoked (one published story killed). Every step is idempotent.
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

STAGE_ORDER = ["Draft", "Review Pending", "In Review", "Returned", "Hold", "Scheduled", "Published", "Revoked"]
SCHEDULED_ITEM = "urn:localwire:demo:LW-SLG-302"
REVOKED_ITEM = "urn:localwire:demo:LW-RPG-109"
REVOKE_REASON = "The location given for the hub was wrong. A corrected story will follow."


class Api:
    def __init__(self, url, user, password):
        self.url = url.rstrip("/")
        token = self.request("POST", "/auth_db", {"username": user, "password": password}, auth=False)["token"]
        self.auth = "Basic " + base64.b64encode((token + ":").encode()).decode()

    def request(self, method, path, body=None, auth=True, etag=None, params=None):
        url = self.url + path + ("?" + urllib.parse.urlencode(params) if params else "")
        data = json.dumps(body).encode() if body is not None else None
        headers = {"Content-Type": "application/json"}
        if auth:
            headers["Authorization"] = self.auth
        if etag:
            headers["If-Match"] = etag
        for attempt in range(6):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method=method)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    raw = resp.read()
                    return json.loads(raw) if raw else {}
            except urllib.error.HTTPError as e:
                detail = e.read().decode(errors="replace")[:400]
                raise RuntimeError(f"{method} {path} -> {e.code}: {detail}") from None
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt == 5:
                    raise
                print(f"    connection to {path} failed ({e}), retrying", flush=True)
                time.sleep(3)

    def get(self, path, **params):
        return self.request("GET", path, params=params)

    def items(self, path, **params):
        return self.get(path, max_results=200, **params)["_items"]

    def patch(self, path, body, etag):
        return self.request("PATCH", path, body, etag=etag)


def step_stages(api):
    """Board order Draft first, and global read off so a workgroup's stories stay inside it."""
    print("Stages")
    desks = {d["_id"]: d["name"] for d in api.items("/desks")}
    stages = [s for s in api.items("/stages") if s["desk"] in desks]
    for desk_id, desk_name in desks.items():
        own = {s["name"]: s for s in stages if s["desk"] == desk_id}
        ordered = [own[n]["_id"] for n in STAGE_ORDER if n in own]
        ordered += [s["_id"] for s in own.values() if s["_id"] not in ordered]
        current = [s["_id"] for s in sorted(own.values(), key=lambda s: s.get("desk_order", 0))]
        if current != ordered:
            api.request("POST", "/stages_order", {"desk": desk_id, "stages": ordered})
            print(f"  {desk_name}: order set")
        else:
            print(f"  {desk_name}: order unchanged")
        for stage in own.values():
            if stage.get("is_visible"):
                api.patch(f"/stages/{stage['_id']}", {"is_visible": False}, stage["_etag"])
                print(f"  {desk_name} / {stage['name']}: global read off")


def step_states(api):
    print("Item states")
    query = {"query": {"bool": {"must": [{"term": {"state": "fetched"}}]}}}
    for item in api.items("/archive", source=json.dumps(query)):
        api.patch(f"/archive/{item['_id']}", {"state": "in_progress"}, item["_etag"])
        print(f"  {item.get('headline', item['_id'])[:60]}: fetched -> in_progress")


def step_scheduled(api):
    print("Scheduled story")
    item = api.get(f"/archive/{SCHEDULED_ITEM}")
    if item.get("state") in ("scheduled", "published"):
        print(f"  {item['headline'][:60]}: already {item['state']}")
        return
    when = (datetime.now(timezone.utc) + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0)
    api.patch(f"/archive/publish/{SCHEDULED_ITEM}", {"publish_schedule": when.strftime("%Y-%m-%dT%H:%M:%S+0000")}, item["_etag"])
    print(f"  {item['headline'][:60]}: scheduled for {when.isoformat()}")


def step_revoked(api):
    print("Revoked story")
    item = api.get(f"/archive/{REVOKED_ITEM}")
    if item.get("state") == "killed":
        print(f"  {item['headline'][:60]}: already killed")
        return
    if item.get("state") != "published":
        print(f"  {item['headline'][:60]}: not published ({item.get('state')}), skipped")
        return
    api.patch(f"/archive/kill/{REVOKED_ITEM}", {"body_html": f"<p>{REVOKE_REASON}</p>"}, item["_etag"])
    print(f"  {item['headline'][:60]}: killed")


STEPS = {"stages": step_stages, "states": step_states, "scheduled": step_scheduled, "revoked": step_revoked}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", choices=sorted(STEPS))
    args = parser.parse_args()
    url = os.environ["SUPERDESK_URL"]
    api = Api(url, os.environ.get("SUPERDESK_USER", "admin"), os.environ["SUPERDESK_PASSWORD"])
    print(f"Post-seed on {url} as {os.environ.get('SUPERDESK_USER', 'admin')}")
    for name in (args.only or list(STEPS)):
        try:
            STEPS[name](api)
        except RuntimeError as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            if not args.only:
                continue
            raise SystemExit(1)


if __name__ == "__main__":
    main()
