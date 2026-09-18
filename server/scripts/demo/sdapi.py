"""Minimal Superdesk REST client for the Briefdesk demo seeder.

Standard library only: the seeder runs from a laptop against a deployed instance, where
nothing from server/requirements.txt is installed.
"""

import errno
import time
import base64
import json
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request


class ApiError(RuntimeError):
    def __init__(self, method, url, status, body):
        self.status = status
        self.body = body
        super().__init__("%s %s -> %s\n%s" % (method, url, status, body))


class DryRunId(str):
    """Marks an id that was never assigned by a server, so the report can say so."""


class Superdesk:
    def __init__(self, base_url, dry_run=False, verbose=False, insecure=False):
        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("/api"):
            self.base_url += "/api"
        self.dry_run = dry_run
        self.verbose = verbose
        self.token = None
        self.user_id = None
        self._dry_seq = 0
        self._ssl_context = ssl._create_unverified_context() if insecure else None

    # -- plumbing ---------------------------------------------------------

    def _headers(self):
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            raw = base64.b64encode(("%s:" % self.token).encode()).decode()
            headers["Authorization"] = "Basic " + raw
        return headers

    def _call(self, method, path, body=None, params=None, etag=None):
        url = self.base_url + "/" + path.lstrip("/")
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = self._headers()
        if etag:
            headers["If-Match"] = etag
        data = json.dumps(body).encode() if body is not None else None
        attempt = 0
        while True:
            attempt += 1
            request = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=120, context=self._ssl_context) as response:
                    payload = response.read().decode() or "{}"
                break
            except urllib.error.HTTPError as err:
                raise ApiError(method, url, err.code, err.read().decode()) from None
            except urllib.error.URLError as err:
                # A write is only repeated when the connection was never established, so that a
                # request the server may already have acted on is not sent twice.
                never_connected = getattr(err.reason, "errno", None) in (errno.ETIMEDOUT, errno.ECONNREFUSED)
                if attempt < 4 and (method == "GET" or never_connected):
                    print("    connection to %s failed (%s), retrying" % (url, err.reason))
                    time.sleep(3 * attempt)
                    continue
                raise ApiError(method, url, "connection failed", str(err.reason)) from None
        if self.verbose:
            print("    %s %s" % (method, url))
        return json.loads(payload)

    # -- verbs ------------------------------------------------------------

    def login(self, username, password):
        if self.dry_run:
            self.token = "dry-run"
            self.user_id = DryRunId("dry-run:user")
            return
        saved, self.token = self.token, None
        try:
            session = self._call("POST", "auth_db", {"username": username, "password": password})
        except ApiError:
            self.token = saved
            raise
        self.token = session["token"]
        self.user_id = session["user"]

    def get(self, resource, params=None):
        if self.dry_run:
            return {"_items": []}
        return self._call("GET", resource, params=params)

    def get_item(self, resource, item_id):
        if self.dry_run:
            return None
        try:
            return self._call("GET", "%s/%s" % (resource, item_id))
        except ApiError as err:
            if err.status == 404:
                return None
            raise

    def post(self, resource, doc):
        if self.dry_run:
            self._dry_seq += 1
            return {"_id": DryRunId("dry-run:%s:%d" % (resource, self._dry_seq)), "_etag": "dry-run"}
        created = self._call("POST", resource, doc)
        if "_items" in created:
            return created["_items"][0]
        return created

    def patch(self, resource, item_id, updates, etag=None):
        if self.dry_run:
            return {"_id": item_id, "_etag": "dry-run"}
        if etag is None:
            current = self._call("GET", "%s/%s" % (resource, item_id))
            etag = current["_etag"]
        return self._call("PATCH", "%s/%s" % (resource, item_id), updates, etag=etag)

    # -- lookups ----------------------------------------------------------

    def find_one(self, resource, **where):
        """Find a single document with a mongo `where` query."""
        if self.dry_run:
            return None
        result = self.get(resource, {"where": json.dumps(where), "max_results": 1})
        items = result.get("_items") or []
        return items[0] if items else None

    def find_all(self, resource, where=None, max_results=200):
        if self.dry_run:
            return []
        params = {"max_results": max_results}
        if where:
            params["where"] = json.dumps(where)
        return self.get(resource, params).get("_items") or []

    def search(self, resource, query, max_results=200):
        """Find documents on an elastic-backed resource."""
        if self.dry_run:
            return []
        source = {"query": query, "size": max_results}
        return self.get(resource, {"source": json.dumps(source)}).get("_items") or []


def log(message, indent=0):
    sys.stdout.write("%s%s\n" % ("  " * indent, message))
    sys.stdout.flush()
