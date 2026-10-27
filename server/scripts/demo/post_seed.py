"""Finishing touches the seed engine cannot express, applied over the REST API.

Run after `build.py superdesk seed` (see direction/scenes.md, "Seeding order"):

    SUPERDESK_URL=https://<host> SUPERDESK_USER=admin SUPERDESK_PASSWORD=... python3 post_seed.py [--apply] [--only STEP ...]

Without --apply nothing is written: every step only prints what it would change. Every step is
idempotent. Not yet run against a live instance: run the first time with a dry pass, read it, then
--apply.

Steps, in this order:
  hierarchy       Themenarchitektur becomes a two-level list (parent of every Thema)
  coverage_types  one coverage type per channel in the coverage type list
  retype          seeded coverages get their channel's coverage type (the engine writes "text" on all)
  states          seeded items go from "fetched" to "in_progress" (board and list badges read better)

Re-running the engine's `vocabularies` section resets the hierarchy; run `hierarchy` again afterwards.
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

# Thema qcode -> Themenfeld qcode. Must match the themenarchitektur vocabulary in contract.yaml.
PARENTS = {
    "thema:waermewende": "themenfeld:gebaeude_waerme",
    "thema:sanierung": "themenfeld:gebaeude_waerme",
    "thema:waermepumpen": "themenfeld:gebaeude_waerme",
    "thema:serielles_sanieren": "themenfeld:gebaeude_waerme",
    "thema:erneuerbare": "themenfeld:strom_netze",
    "thema:netzausbau": "themenfeld:strom_netze",
    "thema:speicher": "themenfeld:strom_netze",
    "thema:wasserstoff": "themenfeld:industrie_wasserstoff",
    "thema:effizienz_industrie": "themenfeld:industrie_wasserstoff",
    "thema:abwaerme": "themenfeld:industrie_wasserstoff",
    "thema:elektromobilitaet": "themenfeld:mobilitaet",
    "thema:ladeinfrastruktur": "themenfeld:mobilitaet",
    "thema:alternative_kraftstoffe": "themenfeld:mobilitaet",
}

# One coverage type per channel. "content item type" decides which kind of article an assignment
# creates; every text channel uses text, YouTube uses video.
COVERAGE_TYPES = [
    ("pressemitteilung", "Pressemitteilung", "text"),
    ("linkedin", "LinkedIn", "text"),
    ("instagram", "Instagram", "text"),
    ("youtube", "YouTube", "video"),
    ("newsletter", "Newsletter", "text"),
    ("website", "Website", "text"),
    ("intranet", "Intranet", "text"),
    ("event", "Event", "text"),
]

# Coverage slugline (the `ref` in content/storys.json) -> coverage type qcode.
COVERAGE_BY_REF = {
    "ST-WP-PM": "pressemitteilung",
    "ST-WP-LI": "linkedin",
    "ST-WP-NL": "newsletter",
    "ST-WP-IG": "instagram",
    "ST-FA-PM": "pressemitteilung",
    "ST-FA-WEB": "website",
    "ST-FA-INT": "intranet",
    "ST-LQ-PM": "pressemitteilung",
    "ST-LQ-LI": "linkedin",
    "ST-LQ-EV": "event",
    "ST-WS-LI": "linkedin",
    "ST-WS-NL": "newsletter",
    "ST-WS-WEB": "website",
}

GUID_PREFIX = "urn:eakom:demo:"


class Api:
    def __init__(self, url, user, password, apply):
        self.url = url.rstrip("/")
        if not self.url.endswith("/api"):
            self.url += "/api"
        self.apply = apply
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
                raise RuntimeError("%s %s -> %s: %s" % (method, path, e.code, detail)) from None
            except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
                if attempt == 5:
                    raise
                print("    connection to %s failed (%s), retrying" % (path, e), flush=True)
                time.sleep(3)

    def get(self, path, **params):
        return self.request("GET", path, params=params)

    def items(self, path, **params):
        return self.get(path, max_results=200, **params)["_items"]

    def patch(self, path, body, etag):
        if not self.apply:
            return None
        return self.request("PATCH", path, body, etag=etag)


def step_hierarchy(api):
    print("Themenarchitektur hierarchy")
    vocabulary = api.get("/vocabularies/themenarchitektur")
    items = vocabulary["items"]
    changed = False
    for item in items:
        wanted = PARENTS.get(item["qcode"])
        if wanted and item.get("parent") != wanted:
            item["parent"] = wanted
            changed = True
    schema = dict(vocabulary.get("schema") or {})
    if "parent" not in schema:
        schema["parent"] = {}
        changed = True
    if not changed:
        print("  already two levels")
        return
    api.patch("/vocabularies/themenarchitektur", {"items": items, "schema": schema}, vocabulary["_etag"])
    print("  %s: parent set on %d themes" % ("done" if api.apply else "would set", len([i for i in items if i.get("parent")])))


def step_coverage_types(api):
    print("Coverage types")
    vocabulary = api.get("/vocabularies/g2_content_type")
    items = vocabulary["items"]
    present = {item["qcode"] for item in items}
    missing = [t for t in COVERAGE_TYPES if t[0] not in present]
    if not missing:
        print("  all channel types present")
        return
    for qcode, name, item_type in missing:
        items.append({"is_active": True, "qcode": qcode, "name": name, "content item type": item_type})
    api.patch("/vocabularies/g2_content_type", {"items": items}, vocabulary["_etag"])
    print("  %s: %s" % ("added" if api.apply else "would add", ", ".join(t[1] for t in missing)))


def step_retype(api):
    print("Coverage types on the seeded Storys")
    for plan in api.items("/planning"):
        if not str(plan.get("guid", "")).startswith(GUID_PREFIX + "request:"):
            continue
        coverages = plan.get("coverages") or []
        changed = []
        for coverage in coverages:
            wanted = COVERAGE_BY_REF.get((coverage.get("planning") or {}).get("slugline"))
            if wanted and coverage["planning"].get("g2_content_type") != wanted:
                coverage["planning"]["g2_content_type"] = wanted
                changed.append(coverage["planning"]["slugline"])
        if not changed:
            print("  %s: unchanged" % plan.get("slugline"))
            continue
        try:
            api.patch("/planning/%s" % plan["_id"], {"coverages": coverages}, plan["_etag"])
            print("  %s: %s %s" % (plan.get("slugline"), "retyped" if api.apply else "would retype", ", ".join(changed)))
        except RuntimeError as err:
            print("  %s: FAILED, set the type by hand (see direction/scenes.md): %s" % (plan.get("slugline"), err))


def step_states(api):
    print("Item states")
    query = {"query": {"bool": {"must": [{"term": {"state": "fetched"}}]}}}
    for item in api.items("/archive", source=json.dumps(query)):
        if not str(item.get("guid", "")).startswith(GUID_PREFIX):
            continue
        api.patch("/archive/%s" % item["_id"], {"state": "in_progress"}, item["_etag"])
        print("  %s: fetched -> in_progress%s" % (item.get("headline", item["_id"])[:60], "" if api.apply else " (dry)"))


STEPS = {"hierarchy": step_hierarchy, "coverage_types": step_coverage_types, "retype": step_retype, "states": step_states}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="write; without it every step only prints")
    parser.add_argument("--only", action="append", choices=list(STEPS))
    args = parser.parse_args()
    url, user, password = os.environ.get("SUPERDESK_URL"), os.environ.get("SUPERDESK_USER", "admin"), os.environ.get("SUPERDESK_PASSWORD")
    if not url or not password:
        sys.exit("Set SUPERDESK_URL and SUPERDESK_PASSWORD (and SUPERDESK_USER if it is not admin).")
    api = Api(url, user, password, args.apply)
    print("%s on %s" % ("Applying" if args.apply else "Dry pass", api.url))
    for name in args.only or list(STEPS):
        STEPS[name](api)


if __name__ == "__main__":
    main()
