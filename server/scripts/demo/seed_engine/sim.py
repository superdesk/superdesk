"""An in-memory stand-in for a fresh Superdesk instance, for `--dry-run` and the regression test.

It answers the requests the seed makes the way the server does where that shapes the seed's next
request: a new desk comes with two stages, a planning item hands out tasking ids, a template run
creates a report, `archive_history` records creates, moves and releases. Everything else is stored
and returned as sent. It is not a Superdesk: validation, privileges and search are not simulated.

Ids are derived from the document (`desks:Europe`, `archive:<guid>`), so two runs that create the
same things get the same ids whatever order they create them in.
"""
import copy
import datetime
import json
import os
import urllib.parse

from .sdapi import ApiError, log, masked

HERE = os.path.dirname(os.path.abspath(__file__))

# Keys that name a document, in the order they are tried when an id is derived.
NAME_KEYS = ("_id", "guid", "username", "template_name", "name", "slugline")


def develop_vocabularies():
    """`urgency` and `event_calendars` as origin/develop ships them in server/data/vocabularies.json."""
    with open(os.path.join(HERE, "develop_vocabularies.json"), encoding="utf-8") as handle:
        return json.load(handle)


class SimInstance:
    def __init__(self, vocabularies=None, admin="admin"):
        self.db = {}
        self.sessions = {}
        self.session_users = {}
        self.clock = datetime.datetime(2026, 1, 1, tzinfo=datetime.timezone.utc)
        self.requests = []
        for vocabulary in vocabularies if vocabularies is not None else develop_vocabularies():
            self._store("vocabularies", copy.deepcopy(vocabulary))
        self._store("users", {"_id": "users:%s" % admin, "username": admin, "display_name": admin, "user_type": "administrator"})

    # -- storage -----------------------------------------------------------

    def collection(self, resource):
        return self.db.setdefault(resource, {})

    def _now(self):
        self.clock += datetime.timedelta(seconds=1)
        return self.clock.strftime("%Y-%m-%dT%H:%M:%S+0000")

    def _new_id(self, resource, doc):
        key = next((str(doc[k]) for k in NAME_KEYS if doc.get(k)), None)
        taken = self.collection(resource)
        candidate = "%s:%s" % (resource, key if key is not None else len(taken) + 1)
        unique, suffix = candidate, 1
        while unique in taken:
            suffix += 1
            unique = "%s#%d" % (candidate, suffix)
        return unique

    def _store(self, resource, doc):
        doc = dict(doc)
        doc["_id"] = doc.get("_id") or self._new_id(resource, doc)
        now = self._now()
        doc.setdefault("_created", now)
        doc["_updated"] = now
        doc["_etag"] = "etag:%s" % now
        self.collection(resource)[doc["_id"]] = doc
        return doc

    def _update(self, resource, item_id, updates):
        doc = self.collection(resource).get(item_id)
        if doc is None:
            raise ApiError("PATCH", "%s/%s" % (resource, item_id), 404, "not found")
        for key, value in updates.items():
            if key == "user_preferences" and isinstance(value, dict):
                doc.setdefault(key, {}).update(copy.deepcopy(value))
            else:
                doc[key] = copy.deepcopy(value)
        now = self._now()
        doc["_updated"] = now
        doc["_etag"] = "etag:%s" % now
        return doc

    def _history(self, item, operation, user_id, update=None):
        self._store(
            "archive_history",
            {
                "_id": "archive_history:%d" % (len(self.collection("archive_history")) + 1),
                "item_id": item["_id"],
                "operation": operation,
                "user_id": user_id,
                "version": item.get("_current_version", 1),
                "update": update or {},
            },
        )

    # -- dispatch ----------------------------------------------------------

    def handle(self, method, path, params, body, user_id):
        parts = [urllib.parse.unquote(p) for p in path.split("/") if p]
        resource = parts[0]
        special = getattr(self, "_%s_%s" % (method.lower(), resource), None)
        if special:
            return special(parts[1:], body, user_id)
        if method == "GET":
            if len(parts) > 1:
                doc = self.collection(resource).get(parts[1])
                if doc is None:
                    raise ApiError(method, path, 404, "not found")
                return copy.deepcopy(doc)
            return {"_items": self._query(resource, params)}
        if method == "POST":
            if isinstance(body, list):
                return {"_items": [self._create(resource, doc, user_id) for doc in body]}
            return self._create(resource, body, user_id)
        if method == "PATCH":
            return copy.deepcopy(self._update(resource, parts[1], body))
        raise ApiError(method, path, 405, "method not simulated")

    def _query(self, resource, params):
        if resource == "all_saved_searches":
            resource = "saved_searches"
        docs = list(self.collection(resource).values())
        if "where" in params:
            where = json.loads(params["where"])
            docs = [d for d in docs if all(_matches(d.get(k), v) for k, v in where.items())]
        if "source" in params:
            docs.sort(key=lambda d: d.get("versioncreated") or "", reverse=True)
            limit = json.loads(params["source"]).get("size") or len(docs)
        else:
            limit = int(params.get("max_results", 25))
        return copy.deepcopy(docs[:limit])

    def _create(self, resource, doc, user_id):
        doc = copy.deepcopy(doc)
        if resource == "archive":
            doc["_id"] = doc.get("guid") or self._new_id(resource, doc)
            doc["_current_version"] = 1
            doc.setdefault("original_creator", user_id)
            created = self._store(resource, doc)
            self._history(created, "create", user_id, {"task": doc.get("task")})
            return copy.deepcopy(created)
        if resource == "stages" and not doc.get("_id"):
            doc["_id"] = "stages:%s:%s" % (str(doc.get("desk")).split(":", 1)[-1], doc.get("name"))
        created = self._store(resource, doc)
        hook = getattr(self, "_after_create_%s" % resource, None)
        if hook:
            hook(created)
        return copy.deepcopy(created)

    # -- behaviour the seed depends on -------------------------------------

    def _after_create_desks(self, desk):
        working = self._store("stages", {"_id": "stages:%s:working" % desk["name"], "name": "Working Stage", "desk": desk["_id"], "desk_order": 1})
        incoming = self._store("stages", {"_id": "stages:%s:incoming" % desk["name"], "name": "Incoming Stage", "desk": desk["_id"], "desk_order": 2})
        desk["working_stage"] = working["_id"]
        desk["incoming_stage"] = incoming["_id"]

    def _after_create_stages(self, stage):
        siblings = [s for s in self.collection("stages").values() if s.get("desk") == stage["desk"]]
        stage["desk_order"] = len(siblings)

    def _after_create_planning(self, item):
        for index, coverage in enumerate(item.get("coverages") or []):
            coverage["coverage_id"] = "coverage:%s:%d" % (item.get("slugline"), index + 1)
            assigned = coverage.get("assigned_to")
            if not assigned:
                continue
            ref = (coverage.get("planning") or {}).get("slugline") or coverage["coverage_id"]
            assignment = self._store(
                "assignments",
                {
                    "_id": "assignments:%s" % ref,
                    "planning_item": item["_id"],
                    "coverage_item": coverage["coverage_id"],
                    "assigned_to": {"desk": assigned.get("desk"), "user": assigned.get("user"), "state": "assigned"},
                    "planning": copy.deepcopy(coverage.get("planning") or {}),
                },
            )
            assigned["assignment_id"] = assignment["_id"]
            assigned["state"] = "assigned"

    def _post_stages_order(self, parts, body, user_id):
        for index, stage_id in enumerate(body["stages"]):
            self._update("stages", stage_id, {"desk_order": index + 1})
        return {"_id": "stages_order"}

    def _post_archive(self, parts, body, user_id):
        if not parts:
            if isinstance(body, list):
                return {"_items": [self._create("archive", doc, user_id) for doc in body]}
            return self._create("archive", body, user_id)
        guid = parts[0]
        item = self.collection("archive").get(guid)
        if item is None:
            raise ApiError("POST", "archive/%s/move" % guid, 404, "not found")
        item["task"] = dict(item.get("task") or {}, **body["task"])
        item["_current_version"] = item.get("_current_version", 1) + 1
        self._history(item, "move", user_id, {"task": body["task"]})
        return copy.deepcopy(item)

    def _patch_archive(self, parts, body, user_id):
        if parts[0] == "publish":
            item = self._update("archive", parts[1], {"state": "published"})
            self._history(item, "publish", user_id)
            return copy.deepcopy(item)
        item = self._update("archive", parts[0], body)
        item["_current_version"] = item.get("_current_version", 1) + 1
        self._history(item, "update", user_id, body)
        return copy.deepcopy(item)

    def _post_assignments(self, parts, body, user_id):
        action = parts[0]
        for entry in body:
            assignment = self.collection("assignments")[entry["assignment_id"]]
            if action == "link":
                self._set_tasking_state(assignment, "completed")
                continue
            template = next(
                (t for t in self.collection("content_templates").values() if t.get("template_name") == entry.get("template_name")),
                {"data": {}},
            )
            data = copy.deepcopy(template.get("data") or {})
            data.update(
                {
                    "guid": "sim:tasking:%s" % assignment["planning"].get("slugline"),
                    "slugline": assignment["planning"].get("slugline"),
                    "headline": assignment["planning"].get("headline"),
                    "state": "in_progress",
                    "versioncreated": self._now(),
                    "assignment_id": assignment["_id"],
                    "task": {"desk": assignment["assigned_to"].get("desk"), "user": user_id},
                }
            )
            self._create("archive", data, user_id)
            self._set_tasking_state(assignment, "in_progress")
        return {"_items": body}

    def _patch_assignments(self, parts, body, user_id):
        assignment = self.collection("assignments")[parts[1]]
        self._set_tasking_state(assignment, "completed")
        return copy.deepcopy(assignment)

    def _set_tasking_state(self, assignment, state):
        """The planning item's coverage carries its tasking's state, as the server keeps it."""
        assignment["assigned_to"]["state"] = state
        item = self.collection("planning").get(assignment["planning_item"]) or {}
        for coverage in item.get("coverages") or []:
            if coverage.get("coverage_id") == assignment["coverage_item"]:
                coverage["assigned_to"]["state"] = state

    def _post_events(self, parts, body, user_id):
        if parts and parts[0] == "post":
            return self._pubstatus("events", body["event"], body)
        return {"_items": [self._create("events", doc, user_id) for doc in (body if isinstance(body, list) else [body])]}

    def _post_planning(self, parts, body, user_id):
        if parts and parts[0] == "post":
            return self._pubstatus("planning", body["planning"], body)
        return self._create("planning", body, user_id)

    def _pubstatus(self, resource, item_id, body):
        return copy.deepcopy(self._update(resource, item_id, {"pubstatus": body.get("pubstatus", "usable")}))

    def _post_marked_for_highlights(self, parts, body, user_id):
        item = self.collection("archive")[body["marked_item"]]
        marks = list(item.get("highlights") or [])
        for highlight in body["highlights"]:
            marks.remove(highlight) if highlight in marks else marks.append(highlight)
        item["highlights"] = marks
        return {"_id": "marked"}

    # The endpoint is addressed by session, but what it stores belongs to the user.

    def _get_preferences(self, parts, body, user_id):
        doc = self.collection("preferences").get(self.session_users.get(parts[0], parts[0]))
        return dict(copy.deepcopy(doc), _id=parts[0]) if doc else {"_id": parts[0], "user_preferences": {}, "_etag": "etag:0"}

    def _patch_preferences(self, parts, body, user_id):
        owner = self.session_users.get(parts[0], parts[0])
        if owner not in self.collection("preferences"):
            self.collection("preferences")[owner] = {"_id": owner, "user_preferences": {}}
        return dict(copy.deepcopy(self._update("preferences", owner, body)), _id=parts[0])

    def _post_auth_db(self, parts, body, user_id):
        user = next((u for u in self.collection("users").values() if u.get("username") == body["username"]), None)
        if user is None:
            raise ApiError("POST", "auth_db", 401, "unknown user %s" % body["username"])
        number = len(self.sessions) + 1
        token = "token:%s:%d" % (user["username"], number)
        session = "session:%s:%d" % (user["username"], number)
        self.sessions[token] = user["_id"]
        self.session_users[session] = user["_id"]
        return {"token": token, "user": user["_id"], "_id": session}


def _matches(value, wanted):
    if isinstance(wanted, dict):
        return False
    return str(value) == str(wanted) if value is not None else wanted is None


class SimTransport:
    """Sends a request to a SimInstance and records it. `echo` prints every write; writes made while
    `counting` is off (a silent replay of earlier sections) are not counted as planned."""

    def __init__(self, instance, echo=True):
        self.instance = instance
        self.echo = echo
        self.counting = True
        self.shown = 0

    def __call__(self, method, url, headers, body):
        parsed = urllib.parse.urlsplit(url)
        path = parsed.path.split("/api/", 1)[-1]
        params = dict(urllib.parse.parse_qsl(parsed.query))
        token = None
        if headers.get("Authorization"):
            import base64

            token = base64.b64decode(headers["Authorization"].split(" ", 1)[1]).decode().rstrip(":")
        user_id = self.instance.sessions.get(token)
        actor = next((u["username"] for u in self.instance.collection("users").values() if u["_id"] == user_id), None)
        if method != "GET":
            self.instance.requests.append({"actor": actor, "method": method, "path": path, "body": copy.deepcopy(body)})
            self.shown += 1 if self.counting else 0
            if self.echo and self.counting:
                log("> %s %s%s %s" % (method, path, " (as %s)" % actor if actor else "", json.dumps(masked(body), ensure_ascii=False)), 2)
        return self.instance.handle(method, path, params, copy.deepcopy(body), user_id)
