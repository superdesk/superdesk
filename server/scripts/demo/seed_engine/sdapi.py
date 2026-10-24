"""A small Superdesk REST client.

Every request goes through a transport. `HttpTransport` talks to a real instance and retries a
connection that times out or is refused, which happens now and then from a laptop.
`sim.SimTransport` answers from an in-memory instance and prints the request instead, which is
what `--dry-run` uses: nothing leaves the machine.
"""
import base64
import errno
import json
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

SECRET_KEYS = ("password", "secret_token", "api_key")


class ApiError(RuntimeError):
    def __init__(self, method, url, status, body):
        self.status = status
        self.body = body
        super().__init__("%s %s -> %s\n%s" % (method, url, status, body))


class HttpTransport:
    def __init__(self, insecure=False, timeout=120):
        self.timeout = timeout
        self.context = ssl._create_unverified_context() if insecure else None

    def __call__(self, method, url, headers, body):
        data = json.dumps(body).encode() if body is not None else None
        attempt = 0
        while True:
            attempt += 1
            request = urllib.request.Request(url, data=data, headers=headers, method=method)
            try:
                with urllib.request.urlopen(request, timeout=self.timeout, context=self.context) as response:
                    return json.loads(response.read().decode() or "{}")
            except urllib.error.HTTPError as err:
                raise ApiError(method, url, err.code, err.read().decode()) from None
            except urllib.error.URLError as err:
                # A write is only repeated when the connection was never established, so a request
                # the server may already have acted on is not sent twice.
                never_connected = getattr(err.reason, "errno", None) in (errno.ETIMEDOUT, errno.ECONNREFUSED)
                if attempt < 4 and (method == "GET" or never_connected):
                    log("connection to %s failed (%s), retrying" % (url, err.reason), 2)
                    time.sleep(3 * attempt)
                    continue
                raise ApiError(method, url, "connection failed", str(err.reason)) from None


class Superdesk:
    def __init__(self, base_url, transport, verbose=False):
        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("/api"):
            self.base_url += "/api"
        self.transport = transport
        self.verbose = verbose
        self.token = None
        self.user_id = None
        self.username = None
        # `preferences` is keyed by the session, not by the user.
        self.session_id = None

    def another(self):
        """A client for the same instance with no session, to sign in as somebody else."""
        return Superdesk(self.base_url, self.transport, verbose=self.verbose)

    def _call(self, method, path, body=None, params=None, etag=None):
        url = self.base_url + "/" + path.lstrip("/")
        if params:
            url += "?" + urllib.parse.urlencode(params)
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self.token:
            headers["Authorization"] = "Basic " + base64.b64encode(("%s:" % self.token).encode()).decode()
        if etag:
            headers["If-Match"] = etag
        # A dry run's transport prints writes itself.
        if self.verbose and (method == "GET" or not hasattr(self.transport, "echo")):
            log("%s %s" % (method, url), 2)
        return self.transport(method, url, headers, body)

    def login(self, username, password):
        saved, self.token = self.token, None
        try:
            session = self._call("POST", "auth_db", {"username": username, "password": password})
        except ApiError:
            self.token = saved
            raise
        self.token = session["token"]
        self.user_id = session["user"]
        self.session_id = session["_id"]
        self.username = username

    def get(self, resource, params=None):
        return self._call("GET", resource, params=params)

    def get_item(self, resource, item_id):
        try:
            return self._call("GET", "%s/%s" % (resource, item_id))
        except ApiError as err:
            if err.status == 404:
                return None
            raise

    def post(self, resource, doc):
        created = self._call("POST", resource, doc)
        if isinstance(created, dict) and "_items" in created:
            return created["_items"][0]
        return created

    def patch(self, resource, item_id, updates, etag=None):
        if etag is None:
            etag = self._call("GET", "%s/%s" % (resource, item_id)).get("_etag")
        return self._call("PATCH", "%s/%s" % (resource, item_id), updates, etag=etag)

    def find_one(self, resource, **where):
        items = self.get(resource, {"where": json.dumps(where), "max_results": 1}).get("_items") or []
        return items[0] if items else None

    def find_all(self, resource, where=None, max_results=200):
        params = {"max_results": max_results}
        if where:
            params["where"] = json.dumps(where)
        return self.get(resource, params).get("_items") or []


def masked(value):
    """A copy of a request body that is safe to print."""
    if isinstance(value, dict):
        return {k: ("***" if k in SECRET_KEYS and v else masked(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [masked(v) for v in value]
    return value


def log(message, indent=0):
    sys.stdout.write("%s%s\n" % ("  " * indent, message))
    sys.stdout.flush()
