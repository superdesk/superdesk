"""Finishing touches the seed engine cannot express, applied over the REST API.

Run after ``run_seed.sh`` or ``build.py superdesk seed``:

    SUPERDESK_URL=https://<host>/api SUPERDESK_USER=admin SUPERDESK_PASSWORD=... python3 post_seed.py [--only STEP ...]

Steps, in order: picture_field (the feature media field enabled on both profiles and the crop
size "FIXME" renamed to "4-3"), states (seeded items from ``fetched`` to ``in_progress``),
user_language (every user's interface language set to English). Every step is idempotent.
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

PICTURE_PROFILES = ("Matéria", "Matéria web")
UI_LANGUAGE = "en"


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
    for label in PICTURE_PROFILES:
        profile = next((p for p in api.items("/content_types") if p.get("label") == label), None)
        if profile is None:
            raise RuntimeError(f"no content profile labelled {label}")
        editor = profile.get("editor") or {}
        schema = profile.get("schema") or {}
        if (editor.get("feature_media") or {}).get("enabled") and schema.get("feature_media"):
            print(f"  {label}: picture field already enabled")
            continue
        editor["feature_media"] = {
            "enabled": True,
            "order": 11,
            "sdWidth": "full",
            "field_name": "Foto",
        }
        schema["feature_media"] = {"type": "media", "required": False}
        api.patch(
            f"/content_types/{profile['_id']}",
            {"editor": editor, "schema": schema},
            profile["_etag"],
        )
        print(f"  {label}: picture field enabled")
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


def step_user_language(api):
    # The seed gives every user the content language (pt-BR), and the client takes the
    # interface language from the user, so the demo would open in Portuguese.
    print("Interface language")
    for user in api.items("/users"):
        if user.get("language") == UI_LANGUAGE:
            continue
        api.patch(f"/users/{user['_id']}", {"language": UI_LANGUAGE}, user["_etag"])
        print(f"  {user['username']}: {user.get('language')} -> {UI_LANGUAGE}")


def step_states(api):
    print("Item states")
    query = {"query": {"bool": {"must": [{"term": {"state": "fetched"}}]}}}
    for item in api.items("/archive", source=json.dumps(query)):
        api.patch(f"/archive/{item['_id']}", {"state": "in_progress"}, item["_etag"])
        print(f"  {item.get('headline', item['_id'])[:60]}: fetched -> in_progress")


STEPS = {
    "picture_field": step_picture_field,
    "states": step_states,
    "user_language": step_user_language,
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
