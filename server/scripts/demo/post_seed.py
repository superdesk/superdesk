"""Finishing touches the seed engine cannot express, applied over the REST API.

Run after ``run_seed.sh`` or ``build.py superdesk seed``:

    SUPERDESK_URL=https://<host>/api SUPERDESK_USER=admin SUPERDESK_PASSWORD=... python3 post_seed.py [--only STEP ...]

Steps, in order: picture_field (the Story profile's feature media field enabled and the
crop size "FIXME" renamed to "4-3"), states (seeded items from ``fetched`` to ``in_progress``), scheduled (one
Ready story published with an embargo time tomorrow at 06:00 UTC). Every step is idempotent.
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

SCHEDULED_ITEM = "urn:agency:demo:MNA-POL-205"


class Api:
    def __init__(self, url, user, password):
        self.url = url.rstrip("/")
        token = self.request(
            "POST", "/auth_db", {"username": user, "password": password}, auth=False
        )["token"]
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
                req = urllib.request.Request(
                    url, data=data, headers=headers, method=method
                )
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


def step_picture_field(api):
    print("Picture field")
    profile = next((p for p in api.items("/content_types") if p.get("label") == "Story"), None)
    if profile is None:
        raise RuntimeError("no content profile labelled Story")
    editor = profile.get("editor") or {}
    schema = profile.get("schema") or {}
    if (editor.get("feature_media") or {}).get("enabled") and schema.get("feature_media"):
        print("  Story: picture field already enabled")
    else:
        editor["feature_media"] = {
            "enabled": True,
            "order": 11,
            "sdWidth": "full",
            "field_name": "Picture",
        }
        schema["feature_media"] = {"type": "media", "required": False}
        api.patch(
            f"/content_types/{profile['_id']}",
            {"editor": editor, "schema": schema},
            profile["_etag"],
        )
        print("  Story: picture field enabled")
    crops = api.get("/vocabularies/crop_sizes")
    items = crops.get("items") or []
    if any(i.get("name") == "FIXME" for i in items):
        for i in items:
            if i.get("name") == "FIXME":
                i["name"] = "4-3"
        api.patch("/vocabularies/crop_sizes", {"items": items}, crops["_etag"])
        print("  crop size FIXME renamed to 4-3")
    else:
        print("  crop sizes: nothing to rename")


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
    when = (datetime.now(timezone.utc) + timedelta(days=1)).replace(
        hour=6, minute=0, second=0, microsecond=0
    )
    api.patch(
        f"/archive/publish/{SCHEDULED_ITEM}",
        {"publish_schedule": when.strftime("%Y-%m-%dT%H:%M:%S+0000")},
        item["_etag"],
    )
    print(f"  {item['headline'][:60]}: scheduled for {when.isoformat()}")


STEPS = {
    "picture_field": step_picture_field,
    "states": step_states,
    "scheduled": step_scheduled,
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", action="append", choices=sorted(STEPS))
    args = parser.parse_args()
    url = os.environ["SUPERDESK_URL"]
    api = Api(
        url, os.environ.get("SUPERDESK_USER", "admin"), os.environ["SUPERDESK_PASSWORD"]
    )
    print(f"Post-seed on {url} as {os.environ.get('SUPERDESK_USER', 'admin')}")
    for name in args.only or list(STEPS):
        try:
            STEPS[name](api)
        except RuntimeError as e:
            print(f"  FAILED: {e}", file=sys.stderr)
            if not args.only:
                continue
            raise SystemExit(1)


if __name__ == "__main__":
    main()
