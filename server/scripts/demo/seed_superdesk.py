#!/usr/bin/env python3
"""Populate a freshly deployed Superdesk instance into the Briefdesk demo state.

    SUPERDESK_URL=https://... SUPERDESK_USER=admin SUPERDESK_PASSWORD=... \
    PORTAL_URL=https://... OPENROUTER_API_KEY=... \
    python3 server/scripts/demo/seed_superdesk.py

Re-runnable: everything is looked up by name or by a deterministic id and then created or
updated, never duplicated. See README.md in this directory.
"""

import argparse
import datetime
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import definitions as D  # noqa: E402
from sdapi import ApiError, DryRunId, Superdesk, log  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
VOCABULARIES_FILE = os.path.normpath(os.path.join(HERE, "..", "..", "data", "vocabularies.json"))
CONTENT_DIR = os.path.join(HERE, "content")
GUID_PREFIX = "urn:briefdesk:demo:"

# Fields of the default content profile that a Briefdesk report type does not use. `urgency` is
# not here: it carries the severity level and is part of every report type.
NEWSROOM_ONLY_FIELDS = [
    "genre", "place", "priority", "anpa_category", "subject", "authors", "dateline",
    "sign_off", "feature_media", "media_description", "keywords", "language", "usageterms",
    "anpa_take_key", "company_codes", "sms", "footer", "body_footer", "attachments",
]

SECTIONS = [
    "vocabularies",
    "roles",
    "users",
    "profiles",
    "desks",
    "templates",
    "ingest",
    "publishing",
    "highlights",
    "dashboards",
    "ai",
    "planning",
    "content",
    "triage",
    "workflow",
]


WEEKDAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]


def utc_iso(hours_ago=0, days_ahead=0):
    moment = datetime.datetime.now(datetime.timezone.utc)
    moment -= datetime.timedelta(hours=hours_ago)
    moment += datetime.timedelta(days=days_ahead)
    return moment.strftime("%Y-%m-%dT%H:%M:%S+0000")


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%S+0000")


def utc_at(days=0, hour=9):
    """A whole hour, so many days from today. Calendar entries are placed relative to the run so
    the demo always looks current."""
    moment = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    return moment.replace(hour=hour, minute=0, second=0, microsecond=0)


def utc_in(hours=0):
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)


def html_list(lines):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % line for line in lines)


def load_vocabularies():
    with open(VOCABULARIES_FILE, encoding="utf-8") as handle:
        everything = json.load(handle)
    return [v for v in everything if v["_id"] in D.BRIEFDESK_VOCABULARIES]


class Seeder:
    def __init__(self, api, portal_url, openrouter_key, ai_model, portal_push_url=None, insecure=False,
                 pace=D.WORKFLOW_PACE_SECONDS):
        self.api = api
        self.insecure = insecure
        self.pace = pace
        self.portal_url = (portal_url or "").rstrip("/")
        # Where this server reaches the portal, which is not always the address a browser uses:
        # two instances on the same host may only see each other by their internal names.
        self.portal_push_url = (portal_push_url or "").rstrip("/") or self.portal_url
        self.openrouter_key = openrouter_key
        self.ai_model = ai_model
        self.vocabularies = load_vocabularies()
        self.cv_names = {
            vocabulary["_id"]: {item["qcode"]: item["name"] for item in vocabulary["items"]}
            for vocabulary in self.vocabularies
        }
        self._cache = {}
        self._sessions = {}
        self.notes = []
        self.ai_action_ids = {}

    # -- generic upsert ---------------------------------------------------

    def upsert(self, resource, lookup, doc, label, immutable=(), existing=None):
        """Create the document, or patch the fields of an existing one that differ."""
        if existing is None:
            existing = self.api.find_one(resource, **lookup)
        if not existing:
            created = self.api.post(resource, doc)
            log("created %s" % label, 1)
            return created
        updates = {}
        for key, value in doc.items():
            if key in immutable or key == "_id":
                continue
            if existing.get(key) != value:
                updates[key] = value
        if not updates:
            log("unchanged %s" % label, 1)
            return existing
        self.api.patch(resource, existing["_id"], updates, etag=existing.get("_etag"))
        log("updated %s (%s)" % (label, ", ".join(sorted(updates))), 1)
        merged = dict(existing)
        merged.update(updates)
        return merged

    def note(self, message):
        self.notes.append(message)
        log("NOTE: %s" % message, 1)

    # -- lookups ----------------------------------------------------------

    def _cached(self, key, loader):
        if self.api.dry_run:
            return DryRunId("dry-run:%s" % key)
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

    def _by_name(self, kind, resource, field, name):
        def load():
            found = self.api.find_one(resource, **{field: name})
            return found["_id"] if found else None

        return self._cached("%s:%s" % (kind, name), load)

    def role_id(self, name):
        return self._by_name("role", "roles", "name", name)

    def user(self, username):
        def load():
            return self.api.find_one("users", username=username)

        if self.api.dry_run:
            return None
        key = "user:%s" % username
        if key not in self._cache:
            self._cache[key] = load()
        return self._cache[key]

    def user_id(self, username):
        if self.api.dry_run:
            return DryRunId("dry-run:user:%s" % username)
        found = self.user(username)
        return found["_id"] if found else None

    def desk(self, name):
        def load():
            return self.api.find_one("desks", name=name)

        if self.api.dry_run:
            return None
        key = "desk:%s" % name
        if key not in self._cache:
            self._cache[key] = load()
        return self._cache[key]

    def desk_id(self, name):
        if self.api.dry_run:
            return DryRunId("dry-run:desk:%s" % name)
        found = self.desk(name)
        if not found:
            raise SystemExit("Team %r does not exist yet. Run the desks section first." % name)
        return found["_id"]

    def stage_id(self, desk_name, stage_name):
        if self.api.dry_run:
            return DryRunId("dry-run:stage:%s:%s" % (desk_name, stage_name))

        def load():
            desk = self.desk(desk_name)
            if not desk:
                return None
            for stage in self.api.find_all("stages", {"desk": desk["_id"]}):
                if stage["name"] == stage_name:
                    return stage["_id"]
            return None

        stage = self._cached("stage:%s:%s" % (desk_name, stage_name), load)
        if stage is None:
            raise SystemExit("Stage %r on team %r does not exist." % (stage_name, desk_name))
        return stage

    def template(self, template_name):
        """Find a template whatever the case of its stored name.

        Superdesk lower-cases a template name on create, keeps the case it is given on update,
        and checks uniqueness without regard to case, so an exact match on the name misses.
        """
        if self.api.dry_run:
            return None
        for found in self.api.find_all("content_templates", max_results=500):
            if (found.get("template_name") or "").lower() == template_name.lower():
                return found
        return None

    def template_id(self, template_name):
        found = self.template(template_name)
        return found["_id"] if found else None

    def content_filter_id(self, name):
        return self._by_name("content_filter", "content_filters", "name", name)

    def filter_condition_id(self, name):
        return self._by_name("filter_condition", "filter_conditions", "name", name)

    def product_id(self, name):
        return self._by_name("product", "products", "name", name)

    # -- subject helper ---------------------------------------------------

    def subject(self, pairs):
        """Turn (scheme, qcode) pairs into the item `subject` entries the portal filters on."""
        terms = []
        for scheme, qcode in pairs:
            name = self.cv_names.get(scheme, {}).get(qcode)
            if name is None:
                raise SystemExit("Unknown %s value %r. Check server/data/vocabularies.json." % (scheme, qcode))
            terms.append({"name": name, "qcode": qcode, "scheme": scheme})
        return terms

    # -- sections ---------------------------------------------------------

    def section_vocabularies(self):
        log("Vocabularies")
        self._upsert_vocabularies(self.vocabularies)

    def _upsert_vocabularies(self, vocabularies):
        for vocabulary in vocabularies:
            doc = dict(vocabulary)
            existing = self.api.get_item("vocabularies", doc["_id"])
            if not existing:
                self.api.post("vocabularies", doc)
                log("created vocabulary %s" % doc["_id"], 1)
                continue
            updates = {key: value for key, value in doc.items() if key != "_id" and existing.get(key) != value}
            # The server strips is_active from items on read, so items always look different.
            if updates:
                self.api.patch("vocabularies", doc["_id"], updates, etag=existing.get("_etag"))
                log("updated vocabulary %s" % doc["_id"], 1)
            else:
                log("unchanged vocabulary %s" % doc["_id"], 1)

    def section_roles(self):
        log("Roles")
        for role in D.ROLES:
            doc = {
                "name": role["name"],
                "description": role["description"],
                "privileges": {name: 1 for name in sorted(set(role["privileges"]))},
            }
            for optional in ("author_role", "editor_role"):
                if role.get(optional):
                    doc[optional] = role[optional]
            self.upsert("roles", {"name": role["name"]}, doc, "role %s" % role["name"])
            self._cache.pop("role:%s" % role["name"], None)

    def section_users(self):
        log("Users")
        for user in D.USERS:
            doc = {
                "username": user["username"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "display_name": "%s %s" % (user["first_name"], user["last_name"]),
                "email": "%s@%s" % (user["username"], D.EMAIL_DOMAIN),
                "sign_off": user["sign_off"],
                "byline": "%s %s" % (user["first_name"], user["last_name"]),
                "job_title": user["job_title"],
                "user_type": "user",
                "is_active": True,
                "is_enabled": True,
                "is_author": True,
                "needs_activation": False,
                "language": "en",
            }
            role_id = self.role_id(user["role"])
            if role_id:
                doc["role"] = role_id
            existing = self.api.find_one("users", username=user["username"])
            if not existing:
                doc["password"] = D.DEMO_PASSWORD
                self.api.post("users", doc)
                log("created user %s (%s)" % (user["username"], user["role"]), 1)
            else:
                updates = {k: v for k, v in doc.items() if k != "username" and existing.get(k) != v}
                if updates:
                    self.api.patch("users", existing["_id"], updates, etag=existing.get("_etag"))
                    log("updated user %s" % user["username"], 1)
                else:
                    log("unchanged user %s" % user["username"], 1)
            self._cache.pop("user:%s" % user["username"], None)

    def section_profiles(self):
        log("Report types")
        for profile in D.CONTENT_PROFILES:
            existing = self.api.get_item("content_types", profile["_id"])
            base = {
                "label": profile["label"],
                "description": profile["description"],
                "priority": profile["priority"],
                "enabled": True,
                # The client lists report types with `where type = text`. One without a type is
                # valid on the server but never appears in the editor's profile selector or in
                # the team settings.
                "type": "text",
            }
            if not existing:
                doc = dict(base)
                doc["_id"] = profile["_id"]
                self.api.post("content_types", doc)
                log("created report type %s" % profile["label"], 1)
            else:
                updates = {k: v for k, v in base.items() if existing.get(k) != v}
                if updates:
                    self.api.patch("content_types", profile["_id"], updates, etag=existing.get("_etag"))
            # The fields are sent in the expanded notation the content profile editor uses. The
            # server folds the custom vocabularies back into `subject` on save, which is what
            # makes selected values land in subject[] with their scheme.
            # Superdesk merges its default editor into every save, and the defaults switch the
            # newsroom fields on. A field only stays off when it is sent as disabled.
            editor = dict(profile["editor"])
            for field in NEWSROOM_ONLY_FIELDS:
                if not (editor.get(field) or {}).get("enabled"):
                    editor[field] = {"enabled": False}
            self.api.patch(
                "content_types",
                profile["_id"],
                {"editor": editor, "schema": profile["schema"]},
            )
            log("configured fields on %s" % profile["label"], 1)

    def section_desks(self):
        log("Teams and stages")
        for desk in D.DESKS:
            existing = self.api.find_one("desks", name=desk["name"])
            if not existing:
                created = self.api.post(
                    "desks",
                    {
                        "name": desk["name"],
                        "description": desk["description"],
                        "source": desk["source"],
                        "desk_type": "production",
                        "desk_language": "en",
                    },
                )
                log("created team %s" % desk["name"], 1)
                existing = created
            else:
                updates = {}
                for key, value in (
                    ("description", desk["description"]),
                    ("source", desk["source"]),
                    ("desk_type", "production"),
                    ("desk_language", "en"),
                    # Without a list of allowed report types the profile selector in the editor
                    # header is empty.
                    ("content_profiles", {profile["_id"]: True for profile in D.CONTENT_PROFILES}),
                ):
                    if existing.get(key) != value:
                        updates[key] = value
                if updates:
                    self.api.patch("desks", existing["_id"], updates, etag=existing.get("_etag"))
                log("team %s present" % desk["name"], 1)
            self._cache.pop("desk:%s" % desk["name"], None)
            self._rename_default_stages(existing, desk["stages"])
            self._extra_stages(existing, desk["stages"])
            self._order_stages(existing, desk["stages"])

        for desk in D.DESKS:
            self._desk_members(desk["name"])
            self._monitoring_settings(desk["name"], desk["stages"])

        log("Default team per user", 1)
        for user in D.USERS:
            if self.api.dry_run:
                log("would set the default team of %s to %s" % (user["username"], user["default_desk"]), 2)
                continue
            found = self.user(user["username"])
            if not found:
                continue
            desk_id = self.desk_id(user["default_desk"])
            if found.get("desk") != desk_id:
                self.api.patch("users", found["_id"], {"desk": desk_id})
                log("default team of %s set to %s" % (user["username"], user["default_desk"]), 2)

    def _rename_default_stages(self, desk, stages):
        """A new desk arrives with Working Stage and Incoming Stage. Rename them in place so the
        board reads in Briefdesk terms and the default incoming stage keeps its meaning."""
        if self.api.dry_run:
            log("would rename the two default stages to %s and %s" % (stages[0], stages[1]), 2)
            return
        renames = [
            (desk.get("incoming_stage"), stages[0]),
            (desk.get("working_stage"), stages[1]),
        ]
        for stage_id, name in renames:
            if not stage_id:
                continue
            stage = self.api.get_item("stages", stage_id)
            if not stage or stage.get("name") == name:
                continue
            self.api.patch("stages", stage_id, {"name": name}, etag=stage.get("_etag"))
            log("renamed stage to %s" % name, 2)

    def _extra_stages(self, desk, stages):
        if self.api.dry_run:
            for name in stages[2:]:
                log("would create stage %s" % name, 2)
            return
        present = {stage["name"] for stage in self.api.find_all("stages", {"desk": desk["_id"]})}
        for name in stages[2:]:
            if name in present:
                continue
            self.api.post(
                "stages",
                {
                    "name": name,
                    "desk": desk["_id"],
                    "description": "%s stage" % name,
                    "is_visible": True,
                    "task_status": D.STAGE_TASK_STATUS.get(name, "in_progress"),
                },
            )
            log("created stage %s" % name, 2)

    def _order_stages(self, desk, stages):
        """The two automatic stages are created working-first, so without this the board reads
        Analysis, Incoming, Review, Released."""
        if self.api.dry_run:
            log("would order the stages as %s" % ", ".join(stages), 2)
            return
        by_name = {stage["name"]: stage for stage in self.api.find_all("stages", {"desk": desk["_id"]})}
        ordered = [by_name[name] for name in stages if name in by_name]
        if len(ordered) != len(stages):
            return
        if [stage.get("desk_order") for stage in ordered] == list(range(1, len(stages) + 1)):
            return
        self.api.post("stages_order", {"desk": str(desk["_id"]), "stages": [str(s["_id"]) for s in ordered]})
        log("ordered the stages as %s" % ", ".join(stages), 2)

    def _desk_members(self, desk_name):
        members = [user["username"] for user in D.USERS if desk_name in user["desks"]]
        if self.api.dry_run:
            log("would set members of %s to %s" % (desk_name, ", ".join(members)), 2)
            return
        desk = self.desk(desk_name)
        if not desk:
            return
        wanted = [str(self.user_id(name)) for name in members if self.user_id(name)]
        # The account running the seed joins every team. Superdesk shows a user only the teams
        # they belong to, so an administrator who is no member sees no teams and an empty board.
        if self.api.user_id and str(self.api.user_id) not in wanted:
            wanted.append(str(self.api.user_id))
        wanted = sorted(wanted)
        current = sorted(str(member["user"]) for member in desk.get("members") or [])
        if wanted == current:
            log("members of %s unchanged" % desk_name, 2)
            return
        self.api.patch("desks", desk["_id"], {"members": [{"user": member} for member in wanted]})
        log("members of %s set to %s" % (desk_name, ", ".join(members)), 2)

    def _monitoring_settings(self, desk_name, stages):
        """Without this the board shows the default groups, not the team's own stages."""
        shown = [name for name in stages if name not in D.BOARD_HIDDEN_STAGES]
        if self.api.dry_run:
            log("would set the board of %s to %s" % (desk_name, ", ".join(shown)), 2)
            return
        desk = self.desk(desk_name)
        if not desk:
            return
        settings = []
        for name in shown:
            stage_id = self.stage_id(desk_name, name)
            if stage_id:
                settings.append({"_id": str(stage_id), "type": "stage", "max_items": 30})
        settings.append({"_id": "%s:output" % desk["_id"], "type": "deskOutput", "max_items": 30})
        if desk.get("monitoring_settings") == settings:
            log("board of %s unchanged" % desk_name, 2)
            return
        self.api.patch("desks", desk["_id"], {"monitoring_settings": settings})
        log("board of %s set to %s" % (desk_name, ", ".join(shown)), 2)

    def section_templates(self):
        log("Templates")
        for template in D.TEMPLATES + [D.HIGHLIGHT_TEMPLATE]:
            data = dict(template["data"])
            if "subject" in data:
                data["subject"] = self.subject(data["subject"])
            data.setdefault("type", "text")
            data["profile"] = template["profile"]
            data.setdefault("language", "en")
            doc = {
                "template_name": template["template_name"],
                "template_type": template.get("template_type", "create"),
                "is_public": True,
                "template_desks": [self.desk_id(name) for name in template["desks"]],
                "data": data,
            }
            self.upsert(
                "content_templates",
                {"template_name": template["template_name"]},
                doc,
                "template %s" % template["template_name"],
                existing=self.template(template["template_name"]),
            )

        log("Team defaults", 1)
        for desk in D.DESKS:
            if self.api.dry_run:
                log("would default %s to %s / %s" % (desk["name"], desk["default_profile"], desk["default_template"]), 2)
                continue
            found = self.desk(desk["name"])
            if not found:
                continue
            updates = {}
            if found.get("default_content_profile") != desk["default_profile"]:
                updates["default_content_profile"] = desk["default_profile"]
            template_id = self.template_id(desk["default_template"])
            if template_id and str(found.get("default_content_template") or "") != str(template_id):
                updates["default_content_template"] = template_id
            if updates:
                self.api.patch("desks", found["_id"], updates)
                log("%s defaults to %s / %s" % (desk["name"], desk["default_profile"], desk["default_template"]), 2)
            else:
                log("%s defaults unchanged" % desk["name"], 2)

    def section_ingest(self):
        log("Sources and routing")
        watch_desk = self.desk_id("Watch")
        incoming = self.stage_id("Watch", "Incoming")
        scheme = {
            "name": D.ROUTING_SCHEME_NAME,
            "rules": [
                {
                    "name": "Everything to Watch Incoming",
                    "handler": "desk_fetch_publish",
                    "filter": None,
                    "actions": {"fetch": [{"desk": watch_desk, "stage": incoming}], "exit": True},
                    "schedule": {
                        "day_of_week": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
                        "hour_of_day_from": None,
                        "hour_of_day_to": None,
                        "time_zone": "UTC",
                    },
                }
            ],
        }
        saved = self.upsert(
            "routing_schemes",
            {"name": D.ROUTING_SCHEME_NAME},
            scheme,
            "routing scheme %s" % D.ROUTING_SCHEME_NAME,
        )
        scheme_id = saved["_id"]

        for provider in D.INGEST_PROVIDERS:
            doc = {
                "name": provider["name"],
                "source": provider["source"],
                "feeding_service": "rss",
                "content_types": ["text"],
                "is_closed": False,
                "update_schedule": {"minutes": 5},
                "idle_time": {"hours": 0, "minutes": 0},
                "routing_scheme": scheme_id,
                # The instance may sit behind a proxy that cannot reach the feed at create time,
                # and a failed config test rejects the whole POST.
                "skip_config_test": True,
                "config": {"url": provider["url"], "auth_required": False},
            }
            self.upsert("ingest_providers", {"name": provider["name"]}, doc, "source %s" % provider["name"])

    def section_publishing(self):
        log("Content filters, packages and recipients")
        if not self.portal_push_url:
            self.note(
                "Neither PORTAL_URL nor PORTAL_PUSH_URL is set, so the Briefdesk Portal push destination "
                "has no resource_url."
            )

        for condition in D.FILTER_CONDITIONS:
            self.upsert(
                "filter_conditions",
                {"name": condition["name"]},
                dict(condition),
                "filter condition %s" % condition["name"],
            )
            self._cache.pop("filter_condition:%s" % condition["name"], None)

        for content_filter in D.CONTENT_FILTERS:
            expressions = []
            for group in content_filter["expressions"]:
                ids = [self.filter_condition_id(name) for name in group]
                expressions.append({"expression": {"fc": [str(i) for i in ids if i]}})
            doc = {"name": content_filter["name"], "content_filter": expressions, "is_global": False}
            self.upsert(
                "content_filters",
                {"name": content_filter["name"]},
                doc,
                "content filter %s" % content_filter["name"],
            )
            self._cache.pop("content_filter:%s" % content_filter["name"], None)

        for product in D.PRODUCTS:
            doc = {
                "name": product["name"],
                "description": product["description"],
                "product_type": product["product_type"],
            }
            if product.get("content_filter"):
                doc["content_filter"] = {
                    "filter_id": str(self.content_filter_id(product["content_filter"])),
                    "filter_type": "permitting",
                }
            self.upsert("products", {"name": product["name"]}, doc, "package %s" % product["name"])
            self._cache.pop("product:%s" % product["name"], None)

        portal_product = str(self.product_id("Briefdesk Portal feed"))
        portal = {
            "name": D.PORTAL_SUBSCRIBER_NAME,
            "subscriber_type": "all",
            "email": "portal@%s" % D.EMAIL_DOMAIN,
            "is_active": True,
            "is_targetable": True,
            "sequence_num_settings": {"min": 1, "max": 9999},
            "products": [portal_product],
            "api_products": [portal_product],
            "destinations": [
                {
                    "name": "Briefdesk Portal push",
                    "format": "newsroom ninjs",
                    "delivery_type": "http_push",
                    "config": {
                        "resource_url": "%s/push" % self.portal_push_url if self.portal_push_url else "",
                        "assets_url": "%s/push_binary" % self.portal_push_url if self.portal_push_url else "",
                        "secret_token": D.PUSH_KEY,
                    },
                }
            ],
        }
        self._upsert_subscriber(portal, "recipient %s" % D.PORTAL_SUBSCRIBER_NAME)

        calendar_product = str(self.product_id(D.PORTAL_CALENDAR_PRODUCT))
        calendar = {
            "name": D.PORTAL_CALENDAR_SUBSCRIBER_NAME,
            "subscriber_type": "all",
            "email": "portal@%s" % D.EMAIL_DOMAIN,
            "is_active": True,
            "is_targetable": True,
            "sequence_num_settings": {"min": 1, "max": 9999},
            "products": [calendar_product],
            "api_products": [calendar_product],
            "destinations": [
                {
                    "name": name,
                    "format": output_format,
                    "delivery_type": "http_push",
                    "config": {
                        "resource_url": "%s/push" % self.portal_push_url if self.portal_push_url else "",
                        "assets_url": "%s/push_binary" % self.portal_push_url if self.portal_push_url else "",
                        "secret_token": D.PUSH_KEY,
                    },
                }
                for name, output_format in D.PORTAL_CALENDAR_DESTINATIONS
            ],
        }
        self._upsert_subscriber(calendar, "recipient %s" % D.PORTAL_CALENDAR_SUBSCRIBER_NAME)

        for company in D.CLIENT_COMPANIES:
            doc = {
                "name": company["name"],
                "subscriber_type": "all",
                "email": company["emails"][0],
                "is_active": True,
                "is_targetable": True,
                "sequence_num_settings": {"min": 1, "max": 9999},
                "products": [str(self.product_id(company["product"]))],
                "destinations": [
                    {
                        "name": "Email to %s" % company["name"],
                        "format": "email",
                        "delivery_type": "email",
                        "config": {"recipients": ";".join(company["emails"])},
                    }
                ],
            }
            self._upsert_subscriber(doc, "recipient %s" % company["name"])

    def _upsert_subscriber(self, doc, label):
        """The server gives every destination an id and a preview url and never returns the secret
        token, so comparing the stored destinations to the ones sent always shows a difference."""
        def comparable(destinations):
            return [
                {
                    "name": destination.get("name"),
                    "format": destination.get("format"),
                    "delivery_type": destination.get("delivery_type"),
                    "config": {
                        key: value
                        for key, value in (destination.get("config") or {}).items()
                        if key != "secret_token"
                    },
                }
                for destination in destinations or []
            ]

        existing = self.api.find_one("subscribers", name=doc["name"])
        if existing and comparable(existing.get("destinations")) == comparable(doc["destinations"]):
            doc = {key: value for key, value in doc.items() if key != "destinations"}
        self.upsert("subscribers", {"name": doc["name"]}, doc, label, existing=existing)

    def section_highlights(self):
        log("Briefing lists")
        doc = {
            "name": D.HIGHLIGHT["name"],
            "desks": [self.desk_id(name) for name in D.HIGHLIGHT["desks"]],
            "auto_insert": D.HIGHLIGHT["auto_insert"],
            "groups": D.HIGHLIGHT["groups"],
        }
        template_id = self.template_id(D.HIGHLIGHT["template"])
        if template_id:
            doc["template"] = str(template_id)
        else:
            self.note("Highlight template %r is missing, run the templates section." % D.HIGHLIGHT["template"])
        self.upsert("highlights", {"name": D.HIGHLIGHT["name"]}, doc, "briefing list %s" % D.HIGHLIGHT["name"])

    def section_dashboards(self):
        """Give every team a dashboard, which is empty until somebody adds widgets by hand."""
        log("Dashboards")
        for desk_def in D.DESKS:
            name = desk_def["name"]
            if self.api.dry_run:
                log("would set the dashboard of %s" % name, 1)
                continue
            desk = self.desk(name)
            if not desk:
                continue
            groups = [
                {"_id": group["_id"], "type": group["type"]}
                for group in desk.get("monitoring_settings") or []
                if group.get("type") == "stage"
            ]
            widgets = [
                {
                    "_id": "aggregate", "multiple_id": 1, "active": True,
                    "row": 1, "col": 1, "sizex": 2, "sizey": 2,
                    "configuration": {"label": "%s board" % name, "groups": groups},
                },
                {
                    "_id": "activity", "multiple_id": 1, "active": True,
                    "row": 1, "col": 3, "sizex": 1, "sizey": 2,
                    "configuration": {"maxItems": 8},
                },
                {
                    "_id": "ingest-stats", "multiple_id": 1, "active": True,
                    "row": 3, "col": 1, "sizex": 1, "sizey": 1,
                    "configuration": {"source": "provider", "colorScheme": "superdesk", "updateInterval": 5},
                },
                {
                    "_id": "world-clock", "multiple_id": 1, "active": True,
                    "row": 3, "col": 2, "sizex": 2, "sizey": 1,
                    "configuration": {"zones": ["Europe/Prague", "Europe/London", "Asia/Dubai", "America/New_York"]},
                },
            ]
            existing = self.api.find_one("workspaces", desk=str(desk["_id"]))
            if existing:
                self.api.patch("workspaces", existing["_id"], {"widgets": widgets}, etag=existing.get("_etag"))
                log("updated dashboard of %s" % name, 1)
            else:
                self.api.post("workspaces", {"desk": str(desk["_id"]), "widgets": widgets})
                log("created dashboard of %s" % name, 1)

    def section_ai(self):
        log("AI provider and actions")
        provider = self.api.find_one("ai_providers", name=D.AI_PROVIDER_NAME)
        if not self.openrouter_key:
            # A provider is valid without a key and the actions only need its id, so everything is
            # still created. The key is left out of the payload entirely: an explicit null is the
            # one value that clears a key somebody pasted in by hand.
            self.note(
                "OPENROUTER_API_KEY is not set. The %r provider and both AI actions exist, but runs "
                "fail until the key is pasted into Settings, AI providers." % D.AI_PROVIDER_NAME
            )
        doc = {
            "name": D.AI_PROVIDER_NAME,
            "provider_type": "openai_compatible",
            "base_url": "https://openrouter.ai/api/v1",
            "default_model": self.ai_model,
            "is_default": True,
            "active": True,
            "label": "OpenRouter (bring your own endpoint)",
        }
        if self.openrouter_key:
            doc["api_key"] = self.openrouter_key
        if not provider:
            provider = self.api.post("ai_providers", doc)
            log("created AI provider %s" % D.AI_PROVIDER_NAME, 1)
        elif self.openrouter_key:
            # An existing provider belongs to whoever configured it in Settings: its models, base
            # URL and label are left alone. Only a key given explicitly to this run is written.
            self.api.patch(
                "ai_providers", provider["_id"], {"api_key": self.openrouter_key}, etag=provider.get("_etag")
            )
            log("set the API key of AI provider %s" % D.AI_PROVIDER_NAME, 1)
        else:
            log("kept AI provider %s as configured" % D.AI_PROVIDER_NAME, 1)

        for action in D.AI_ACTIONS:
            doc = {
                "name": action["name"],
                "action_type": action["action_type"],
                "input_fields": action["input_fields"],
                "output_field": action["output_field"],
                "content_profiles": action["content_profiles"],
                # No model on the action: it then runs with the provider's default model, which is
                # the one place an administrator changes it.
                "provider": str(provider["_id"]),
                "active": True,
                "parameters": action["parameters"],
            }
            saved = self.upsert("ai_actions", {"name": action["name"]}, doc, "AI action %s" % action["name"])
            self.ai_action_ids[action["name"]] = str(saved.get("_id"))

    # -- planning ---------------------------------------------------------

    def section_planning(self):
        log("Programmes, risk calendar, client requests and taskings")
        agendas = self._programmes()
        self._event_calendars()
        events = self._events()
        requests = self._requests(agendas, events)
        self._post_to_portal(events, requests)

    def _programmes(self):
        agendas = {}
        for name in D.PROGRAMMES:
            existing = next((a for a in self.api.find_all("agenda") if a.get("name") == name), None)
            if existing:
                log("unchanged programme %s" % name, 1)
                agendas[name] = existing["_id"]
                continue
            created = self.api.post("agenda", {"name": name, "is_enabled": True})
            log("created programme %s" % name, 1)
            agendas[name] = created["_id"]
        return agendas

    def _event_calendars(self):
        """Replace the stock calendars with the ones a risk desk sorts its diary by."""
        wanted = [{"name": name, "qcode": qcode, "is_active": True} for qcode, name in D.EVENT_CALENDARS]
        if self.api.dry_run:
            log("would set the event calendars to %s" % ", ".join(name for _, name in D.EVENT_CALENDARS), 1)
            return
        existing = self.api.get_item("vocabularies", "event_calendars")
        if not existing:
            self.api.post(
                "vocabularies",
                {
                    "_id": "event_calendars",
                    "display_name": "Event Calendars",
                    "type": "manageable",
                    "unique_field": "qcode",
                    "selection_type": "do not show",
                    "items": wanted,
                },
            )
            log("created the event calendars vocabulary", 1)
            return
        # is_active is stripped from items on read, so only the pairs that matter are compared.
        current = [(item.get("qcode"), item.get("name")) for item in existing.get("items") or []]
        if current == [(item["qcode"], item["name"]) for item in wanted]:
            log("event calendars unchanged", 1)
            return
        self.api.patch("vocabularies", "event_calendars", {"items": wanted}, etag=existing.get("_etag"))
        log("set the event calendars to %s" % ", ".join(name for _, name in D.EVENT_CALENDARS), 1)

    # -- risk calendar ----------------------------------------------------

    def _event_doc(self, spec):
        start = utc_at(days=spec["days"], hour=spec["hour"])
        dates = {
            "start": iso(start),
            "end": iso(start + datetime.timedelta(hours=spec["hours"])),
            "tz": spec["tz"],
        }
        repeat = spec.get("repeat")
        if repeat:
            dates["recurring_rule"] = {
                "frequency": repeat["frequency"],
                "interval": repeat.get("interval", 1),
                "byday": WEEKDAYS[start.weekday()],
                "count": repeat["count"],
                "endRepeatMode": "count",
            }
        place = spec["location"]
        doc = {
            "name": spec["name"],
            "slugline": spec["key"],
            "definition_short": spec["summary"],
            "definition_long": spec["detail"],
            "internal_note": spec["internal_note"],
            "dates": dates,
            "occur_status": D.OCCUR_STATUS[spec["occur_status"]],
            "calendars": [{"qcode": spec["calendar"], "name": dict(D.EVENT_CALENDARS)[spec["calendar"]],
                           "is_active": True}],
            "location": [
                {
                    "qcode": GUID_PREFIX + "place:" + spec["key"],
                    "name": place["name"],
                    "address": {"city": place["city"], "country": place["country"], "line": [""]},
                    "location": {"lat": place["lat"], "lon": place["lon"]},
                }
            ],
            "subject": self.subject(spec["subject"]),
            "language": "en",
            "state": "draft",
        }
        if not repeat:
            # A recurring POST generates its own ids for the whole series and drops the guid, so
            # only single entries get a readable one.
            doc["guid"] = GUID_PREFIX + "event:" + spec["key"]
        return doc

    def _events(self):
        """Create the risk calendar. Returns the id of the first occurrence of each entry."""
        log("Risk calendar", 1)
        if self.api.dry_run:
            for spec in D.EVENTS:
                log("would create event %s (%s)" % (spec["key"], spec["name"]), 2)
            return {}
        by_slugline = {}
        for item in self.api.find_all("events", max_results=500):
            by_slugline.setdefault(item.get("slugline"), []).append(item)
        ids = {}
        for spec in D.EVENTS:
            found = sorted(by_slugline.get(spec["key"]) or [], key=lambda e: e["dates"]["start"])
            if found:
                ids[spec["key"]] = found[0]["_id"]
                self._sync_subject("events", found, self.subject(spec["subject"]), "event %s" % spec["key"])
                continue
            created = self.api.post("events", [self._event_doc(spec)])
            ids[spec["key"]] = created["_id"]
            occurrences = spec.get("repeat", {}).get("count", 1)
            log("created event %s (%s, %d occurrence%s)"
                % (spec["key"], spec["name"], occurrences, "" if occurrences == 1 else "s"), 2)
        return ids

    def _sync_subject(self, resource, items, subject, label):
        """The taxonomy values decide which client company sees an entry in the portal, so they are
        the one part of an existing entry the seed keeps authoritative."""
        stale = [item for item in items if item.get("subject") != subject]
        if not stale:
            log("unchanged %s" % label, 2)
            return
        for item in stale:
            self.api.patch(resource, item["_id"], {"subject": subject}, etag=item.get("_etag"))
        log("retagged %s" % label, 2)

    # -- client requests, deliverables and taskings ------------------------

    def _request_doc(self, spec, agendas, events):
        coverages = [self._coverage_doc(deliverable) for deliverable in spec["deliverables"]]
        if spec.get("event") and events.get(spec["event"]):
            event = next(e for e in D.EVENTS if e["key"] == spec["event"])
            planning_date = iso(utc_at(days=event["days"], hour=event["hour"]))
        else:
            planning_date = min(coverage["planning"]["scheduled"] for coverage in coverages)
        doc = {
            "guid": GUID_PREFIX + "request:" + spec["slugline"],
            "name": spec["name"],
            "slugline": spec["slugline"],
            "headline": spec["headline"],
            "description_text": spec["description"],
            "planning_date": planning_date,
            "language": "en",
            "ednote": spec["ednote"],
            "internal_note": spec["internal_note"],
            "agendas": [str(agendas[spec["agenda"]])] if spec.get("agenda") in agendas else [],
            "subject": self.subject(spec["subject"]),
            "urgency": spec["urgency"],
            "coverages": coverages,
        }
        if spec.get("event") and events.get(spec["event"]):
            doc["related_events"] = [{"_id": str(events[spec["event"]]), "link_type": "primary"}]
        return doc

    def _coverage_doc(self, deliverable):
        return {
            "workflow_status": "active",
            "news_coverage_status": {"qcode": "ncostat:int", "name": "coverage intended"},
            "planning": {
                "g2_content_type": "text",
                "slugline": deliverable["ref"],
                "headline": deliverable["headline"],
                "description_text": deliverable["description"],
                "ednote": deliverable["ednote"],
                "internal_note": deliverable["internal_note"],
                "scheduled": iso(utc_in(hours=deliverable["due_hours"])),
                "language": "en",
                "priority": deliverable.get("priority", 2),
            },
            "assigned_to": {
                "desk": str(self.desk_id(deliverable["desk"])),
                "user": str(self.user_id(deliverable["user"])),
                "state": "assigned",
            },
        }

    def _requests(self, agendas, events):
        log("Client requests, deliverables and taskings", 1)
        if self.api.dry_run:
            for spec in D.REQUESTS:
                log("would create request %s with %d deliverable(s)"
                    % (spec["slugline"], len(spec["deliverables"])), 2)
                for deliverable in spec["deliverables"]:
                    log("would drive tasking %s (%s, %s) to %s"
                        % (deliverable["ref"], deliverable["desk"], deliverable["user"], deliverable["state"]), 3)
            return {}
        by_slugline = {item.get("slugline"): item for item in self.api.find_all("planning", max_results=500)}
        created = {}
        for spec in D.REQUESTS:
            item = by_slugline.get(spec["slugline"])
            if item:
                self._sync_subject("planning", [item], self.subject(spec["subject"]),
                                   "request %s" % spec["slugline"])
            else:
                item = self.api.post("planning", self._request_doc(spec, agendas, events))
                log("created request %s with %d deliverable(s)"
                    % (spec["slugline"], len(spec["deliverables"])), 2)
            created[spec["slugline"]] = item["_id"]
            self._drive_taskings(spec, item)
        return created

    def _session(self, username):
        """A signed-in client for one staff member. Some tasking actions are refused to anybody but
        the assignee, and starting work reassigns the tasking to whoever asked for it."""
        if str(self.user_id(username)) == str(self.api.user_id):
            return self.api
        if username not in self._sessions:
            client = Superdesk(self.api.base_url, verbose=self.api.verbose, insecure=self.insecure)
            client.login(username, D.DEMO_PASSWORD)
            self._sessions[username] = client
        return self._sessions[username]

    def _drive_taskings(self, spec, item):
        for deliverable in spec["deliverables"]:
            coverage = next(
                (
                    c
                    for c in item.get("coverages") or []
                    if (c.get("planning") or {}).get("slugline") == deliverable["ref"]
                ),
                None,
            )
            if not coverage:
                self.note(
                    "Request %s has no deliverable %s, so its tasking was not touched."
                    % (spec["slugline"], deliverable["ref"])
                )
                continue
            assigned_to = coverage.get("assigned_to") or {}
            assignment_id = assigned_to.get("assignment_id")
            if not assignment_id:
                self.note("Deliverable %s came back without a tasking." % deliverable["ref"])
                continue
            try:
                self._advance_tasking(deliverable, assignment_id, assigned_to.get("state"))
            except ApiError as err:
                self.note(
                    "Could not move tasking %s to %s: %s %s"
                    % (deliverable["ref"], deliverable["state"], err.status, err.body[:200])
                )

    def _advance_tasking(self, deliverable, assignment_id, state):
        """Walk one tasking to its demo state through the real workflow, and no further."""
        target = deliverable["state"]
        started = ("in_progress", "submitted", "completed")
        if target == "assigned" or (target == "linked" and state in started):
            log("tasking %s is %s" % (deliverable["ref"], state), 3)
            return
        if target == "linked":
            self.api.post(
                "assignments/link",
                [
                    {
                        "assignment_id": str(assignment_id),
                        "item_id": GUID_PREFIX + deliverable["link"],
                        # The released report keeps its author; only the delivery is recorded.
                        "reassign": False,
                    }
                ],
            )
            log("tasking %s delivered by linking %s" % (deliverable["ref"], deliverable["link"]), 3)
            return
        if state == "assigned":
            payload = {"assignment_id": str(assignment_id)}
            template = self.template(deliverable["template"]) if deliverable.get("template") else None
            if template:
                payload["template_name"] = template["template_name"]
            self._session(deliverable["user"]).post("assignments/content", [payload])
            state = "in_progress"
            log("tasking %s started by %s" % (deliverable["ref"], deliverable["user"]), 3)
            if target == "in_progress":
                return
        if target == "completed" and state in ("in_progress", "submitted"):
            assignment = self.api.get_item("assignments", str(assignment_id))
            self.api.patch("assignments/complete", str(assignment_id), {}, etag=assignment.get("_etag"))
            log("tasking %s completed" % deliverable["ref"], 3)
            return
        log("tasking %s is %s" % (deliverable["ref"], state), 3)

    # -- release to the portal ---------------------------------------------

    def _post_to_portal(self, events, requests):
        """Post the client-visible part of the calendar. Posting is what hands an entry to the
        recipients, so anything left unposted stays inside Halden."""
        log("Releasing the risk calendar to the portal", 1)
        if self.api.dry_run:
            for spec in D.EVENTS:
                log("would %s event %s" % ("post" if spec.get("post") is not False else "keep internal",
                                           spec["key"]), 2)
            for spec in D.REQUESTS:
                log("would %s request %s" % ("post" if spec.get("post") else "keep internal",
                                             spec["slugline"]), 2)
            return
        for spec in D.EVENTS:
            if spec.get("post") is False:
                log("event %s stays internal" % spec["key"], 2)
                continue
            self._post_one("events", events.get(spec["key"]), spec["key"], "event",
                           update_method="all" if spec.get("repeat") else None)
        for spec in D.REQUESTS:
            if not spec.get("post"):
                log("request %s stays internal" % spec["slugline"], 2)
                continue
            self._post_one("planning", requests.get(spec["slugline"]), spec["slugline"], "planning")

    def _post_one(self, resource, item_id, label, field, update_method=None):
        if not item_id:
            self.note("Nothing to post for %s, it was not created." % label)
            return
        item = self.api.get_item(resource, str(item_id))
        if not item:
            self.note("Nothing to post for %s, it is gone from %s." % (label, resource))
            return
        if item.get("pubstatus") == "usable":
            log("%s already released" % label, 2)
            return
        doc = {field: str(item_id), "etag": item["_etag"], "pubstatus": "usable"}
        if update_method:
            # Posting one occurrence of a series only posts that one.
            doc["update_method"] = update_method
        try:
            self.api.post("%s/post" % resource, doc)
            log("released %s" % label, 2)
        except ApiError as err:
            self.note("Could not release %s: %s %s" % (label, err.status, err.body[:200]))

    # -- content ----------------------------------------------------------

    def _content_entries(self):
        files = [
            ("alerts.json", "alert"),
            ("daily_briefs.json", "daily_brief"),
            ("country_assessments.json", "country_assessment"),
        ]
        for filename, profile in files:
            path = os.path.join(CONTENT_DIR, filename)
            with open(path, encoding="utf-8") as handle:
                for entry in json.load(handle):
                    yield entry, profile

    def _article(self, entry, profile):
        pairs = []
        if entry.get("severity"):
            pairs.append(("severity", entry["severity"]))
        for scheme in ("region", "country", "sector", "threat_type"):
            for qcode in entry.get(scheme, []):
                pairs.append((scheme, qcode))
        if entry.get("tlp"):
            pairs.append(("tlp", entry["tlp"]))

        if entry.get("body_html"):
            body = entry["body_html"]
        else:
            body = (
                "<h2>Situation</h2><p>%s</p>"
                "<h2>Assessment</h2><p>%s</p>"
                "<h2>Outlook</h2><p>%s</p>"
                % (entry["situation"], entry["assessment"], entry["outlook"])
            )

        extra = {}
        if entry.get("recommended_actions"):
            extra["recommended_actions"] = html_list(entry["recommended_actions"])
        if entry.get("location_text"):
            extra["location_text"] = entry["location_text"]
        if entry.get("sources"):
            extra["sources"] = html_list(entry["sources"])

        stage = {
            "released": "Released",
            "review": "Review",
            "held": "Held",
            "analysis": "Analysis",
            "triage": "Triage",
            "incoming": "Incoming",
        }[entry["workflow"]]
        created = utc_iso(hours_ago=entry["hours_ago"])

        doc = {
            "guid": GUID_PREFIX + entry["reference"],
            "type": "text",
            "profile": profile,
            "state": "fetched",
            "language": "en",
            "headline": entry["title"],
            "slugline": entry["reference"],
            "abstract": entry["summary"],
            "body_html": body,
            "byline": entry["byline"],
            "urgency": D.SEVERITY_URGENCY.get(entry.get("severity"), 3),
            "priority": D.SEVERITY_URGENCY.get(entry.get("severity"), 3),
            "subject": self.subject(pairs),
            "extra": extra,
            "firstcreated": created,
            "versioncreated": created,
            "task": {
                "desk": self.desk_id(entry["desk"]),
                "stage": self.stage_id(entry["desk"], stage),
                "user": self.user_id(entry["author"]),
            },
        }
        if entry.get("ednote"):
            doc["ednote"] = entry["ednote"]
        return doc

    def section_content(self):
        log("Sample reports")
        created_ids = {}
        published = []
        for entry, profile in self._content_entries():
            guid = GUID_PREFIX + entry["reference"]
            existing = self.api.get_item("archive", guid)
            if existing:
                log("report %s already exists (%s)" % (entry["reference"], existing.get("state")), 1)
                created_ids[entry["reference"]] = existing["_id"]
                continue
            doc = self._article(entry, profile)
            item = self.api.post("archive", doc)
            created_ids[entry["reference"]] = item["_id"]
            log("created %s %s (%s)" % (profile, entry["reference"], entry["workflow"]), 1)
            if entry["workflow"] == "released":
                published.append((entry, item))

        if published:
            log("Releasing", 1)
        for entry, item in published:
            if self._release(self.api, item["_id"], entry["reference"], etag=item.get("_etag")):
                log("released %s" % entry["reference"], 2)

        self._review_comments(created_ids)
        self._mark_for_briefing(created_ids)

    def _release(self, session, item_id, label, etag=None):
        """Release a report through the endpoint the Release button uses, which hands it to every
        recipient it matches: the portal push and an email per entitled client company."""
        if etag is None:
            item = session.get_item("archive", str(item_id))
            if not item:
                self.note("Cannot release %s, it is not in archive." % label)
                return False
            etag = item.get("_etag")
        try:
            session.patch("archive/publish", str(item_id), {"state": "published"}, etag=etag)
            return True
        except ApiError as err:
            self.note("Could not release %s: %s" % (label, err.body[:300]))
            return False

    def _review_comments(self, created_ids):
        """Comments are always attributed to the session user, so the reviewer posts its own."""
        in_review = [
            (entry, created_ids.get(entry["reference"]))
            for entry, _ in self._content_entries()
            if entry["workflow"] == "review"
        ]
        in_review = [(entry, item_id) for entry, item_id in in_review if item_id]
        if not in_review:
            return
        log("Review comments", 1)
        if self.api.dry_run:
            for entry, _ in in_review:
                log("would comment on %s as tomas.havel" % entry["reference"], 2)
            return
        reviewer = Superdesk(self.api.base_url, verbose=self.api.verbose)
        try:
            reviewer.login("tomas.havel", D.DEMO_PASSWORD)
        except ApiError as err:
            self.note("Could not sign in as tomas.havel to leave review comments: %s" % err.status)
            return
        texts = {
            "review": "Confidence language in the Assessment is doing a lot of work. Say what the "
            "two sources actually support, then release."
        }
        for entry, item_id in in_review:
            try:
                reviewer.post(
                    "item_comments",
                    {"item": str(item_id), "text": texts["review"]},
                )
                log("commented on %s" % entry["reference"], 2)
            except ApiError as err:
                self.note("Could not comment on %s: %s" % (entry["reference"], err.status))

    def _mark_for_briefing(self, created_ids):
        highlight = self.api.find_one("highlights", name=D.HIGHLIGHT["name"])
        if not highlight and not self.api.dry_run:
            self.note("Briefing list %r is missing, nothing was marked." % D.HIGHLIGHT["name"])
            return
        log("Briefing list", 1)
        for entry, profile in self._content_entries():
            if profile != "alert" or entry["desk"] != "Europe":
                continue
            if entry["workflow"] != "released" or entry["hours_ago"] > 24:
                continue
            item_id = created_ids.get(entry["reference"])
            if not item_id:
                continue
            if self.api.dry_run:
                log("would add %s to %s" % (entry["reference"], D.HIGHLIGHT["name"]), 2)
                continue
            item = self.api.get_item("archive", str(item_id))
            marks = [str(mark) for mark in (item or {}).get("highlights") or []]
            if str(highlight["_id"]) in marks:
                log("%s already on the briefing list" % entry["reference"], 2)
                continue
            try:
                # Posting the same pair twice unmarks it, hence the check above.
                self.api.post(
                    "marked_for_highlights",
                    {"highlights": [str(highlight["_id"])], "marked_item": str(item_id)},
                )
                log("added %s to %s" % (entry["reference"], D.HIGHLIGHT["name"]), 2)
            except ApiError as err:
                self.note("Could not add %s to the briefing list: %s" % (entry["reference"], err.status))

    # -- triage -----------------------------------------------------------

    def section_triage(self):
        """Severity on the native field, the cross-team review queue, and enough work in
        progress for the queue to be worth looking at.

        Separate from `content` because `content` releases what it creates and must not be run
        again on a live instance. Everything here is a create-if-missing or a patch.
        """
        log("Triage")
        relabelled = D.NATIVE_VOCABULARIES + ["severity"]
        self._upsert_vocabularies([v for v in self.vocabularies if v["_id"] in relabelled])
        self._triage_reports()
        self._triage_existing_reports()
        search_id = self._review_queue_search()
        self._triage_workspaces(search_id)

    def _triage_entries(self):
        path = os.path.join(CONTENT_DIR, "triage_items.json")
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    def _triage_reports(self):
        log("Reports in Held, Review and Analysis", 1)
        for entry in self._triage_entries():
            guid = GUID_PREFIX + entry["reference"]
            if self.api.get_item("archive", guid):
                log("report %s already exists" % entry["reference"], 2)
                continue
            if self.api.dry_run:
                log("would create %s in %s / %s" % (entry["reference"], entry["desk"], entry["workflow"]), 2)
                continue
            self.api.post("archive", self._article(entry, "alert"))
            log("created %s in %s / %s" % (entry["reference"], entry["desk"], entry["workflow"]), 2)

    def _triage_existing_reports(self):
        """Bring every unreleased report in line: `urgency` mirrors the severity taxonomy, and
        reports the planning section made from a template get the severity they never had.

        Released reports are left alone. They already carry the right urgency, and the only way
        to change one is a correction, which would push it to the portal a second time.
        """
        log("Severity on reports already on the instance", 1)
        if self.api.dry_run:
            log("would patch urgency and severity on unreleased reports", 2)
            return
        query = {"query": {"match_all": {}}, "size": 200, "sort": [{"versioncreated": "desc"}]}
        items = self.api.get("archive", {"source": json.dumps(query)}).get("_items") or []
        for item in items:
            if item.get("state") in ("spiked", "killed", "recalled"):
                continue
            reference = item.get("slugline")
            subject = list(item.get("subject") or [])
            severity = next((t.get("qcode") for t in subject if t.get("scheme") == "severity"), None)
            updates = {}
            if severity is None and reference in D.TRIAGE_SEVERITY:
                severity = D.TRIAGE_SEVERITY[reference]
                subject.extend(self.subject([("severity", severity)]))
                updates["subject"] = subject
            if severity is None:
                continue
            urgency = D.SEVERITY_URGENCY[severity]
            if item.get("urgency") != urgency:
                updates["urgency"] = urgency
            if item.get("priority") != urgency:
                updates["priority"] = urgency
            if not updates:
                continue
            if item.get("lock_user") and str(item["lock_user"]) != str(self.api.user_id):
                self.note("%s is locked by another user, severity not set." % reference)
                continue
            try:
                self.api.patch("archive", item["_id"], updates, etag=item.get("_etag"))
                log("%s set to %s" % (reference, severity), 2)
            except ApiError as err:
                self.note("Could not set severity on %s: %s" % (reference, err.body[:200]))

    def _review_queue_search(self):
        """One global saved search covering the Review stage of every team."""
        log("Review queue", 1)
        spec = D.REVIEW_QUEUE_SEARCH
        stages = [str(self.stage_id(desk, stage)) for desk, stage in spec["stages"]]
        doc = {
            "name": spec["name"],
            "description": spec["description"],
            "is_global": True,
            "shortcut": True,
            "filter": {
                "query": {
                    # `raw` rather than `q`: both end up in the same query string, but only `q`
                    # is turned into a removable chip above the results, and a chip reading
                    # `task.stage:(6aad50...)` is not what a reviewer should be looking at.
                    "raw": "task.stage:(%s)" % " OR ".join(stages),
                    "repo": "archive",
                    "spike": "exclude",
                    "sort": spec["sort"],
                }
            },
        }
        if self.api.dry_run:
            log("would create the saved search %r" % spec["name"], 2)
            return DryRunId("dry-run:saved_search")
        existing = next(
            (s for s in self.api.find_all("all_saved_searches") if s.get("name") == spec["name"]),
            None,
        )
        if not existing:
            created = self.api.post("saved_searches", doc)
            log("created the saved search %r" % spec["name"], 2)
            return created["_id"]
        updates = {key: value for key, value in doc.items() if existing.get(key) != value}
        if updates:
            self.api.patch("saved_searches", existing["_id"], updates, etag=existing.get("_etag"))
            log("updated the saved search %r" % spec["name"], 2)
        else:
            log("saved search %r unchanged" % spec["name"], 2)
        return existing["_id"]

    def _triage_workspaces(self, search_id):
        """A custom workspace holding the review queue, for the team lead and for whoever runs
        the seed. A custom workspace keeps its monitoring groups in the owner's `agg:view`
        preference rather than on the workspace itself, so both have to be written per user."""
        log("Triage workspace", 1)
        usernames = list(D.TRIAGE_WORKSPACE["users"])
        if self.api.dry_run:
            for username in usernames:
                log("would give %s the %r workspace" % (username, D.TRIAGE_WORKSPACE["name"]), 2)
            return
        sessions = [(self.api.user_id, self.api)]
        for username in usernames:
            user_id = self.user_id(username)
            if not user_id or str(user_id) == str(self.api.user_id):
                continue
            try:
                sessions.append((user_id, self._session(username)))
            except ApiError as err:
                self.note("Could not sign in as %s to build the triage workspace: %s" % (username, err.status))
        for user_id, session in sessions:
            try:
                self._triage_workspace(user_id, session, search_id)
            except ApiError as err:
                self.note("Could not build the triage workspace for %s: %s" % (user_id, err.body[:200]))

    def _triage_workspace(self, user_id, session, search_id):
        name = D.TRIAGE_WORKSPACE["name"]
        existing = next(
            (
                w
                for w in session.find_all("workspaces")
                if w.get("name") == name and str(w.get("user")) == str(user_id)
            ),
            None,
        )
        # A workspace may only be created by its own owner, which is why every user needs a
        # session of their own here.
        workspace = existing or session.post("workspaces", {"name": name, "user": str(user_id)})
        groups = [{"_id": str(search_id), "type": "search", "max_items": 50}]
        preferences = session.get_item("preferences", session.session_id) or {}
        view = dict((preferences.get("user_preferences") or {}).get("agg:view") or {})
        if view.get(str(workspace["_id"])) == {"groups": groups}:
            log("workspace %r for %s unchanged" % (name, user_id), 2)
            return
        view[str(workspace["_id"])] = {"groups": groups}
        session.patch("preferences", session.session_id, {"user_preferences": {"agg:view": view}})
        log("workspace %r set for %s" % (name, user_id), 2)

    # -- workflow ---------------------------------------------------------

    def section_workflow(self):
        """Walk a set of new reports through the stages with the operations the product itself
        uses, signed in as the people who would do it.

        Everything else in the seed creates a report directly in the stage it ends up in, which
        leaves `archive_history` with no `move` at all and the workflow export with no stage visit
        that has both a beginning and an end. This section is what puts real workflow on the
        instance: who moved what, when, and how long it waited for a reviewer.
        """
        log("Workflow walk")
        entries = self._workflow_entries()
        if self.api.dry_run:
            for entry in entries:
                log("would walk %s (%s, %s) to %s in %d steps"
                    % (entry["reference"], entry["desk"], entry["severity"], entry["final"],
                       len(entry["steps"])), 1)
            return

        queue = []
        for entry in entries:
            start = self._workflow_pending_from(entry)
            if start is None:
                log("%s already walked, final state %s" % (entry["reference"], entry["final"]), 1)
                continue
            steps = self._workflow_steps(entry)
            for index in range(start, len(steps)):
                queue.append((steps[index]["at"], entry["reference"], index, entry, steps[index]))
        if not queue:
            log("every report in workflow_items.json has already been walked", 1)
            return

        # One flat schedule rather than one item at a time, so several reports sit in Review
        # together and their visits overlap the way a real shift does.
        queue.sort(key=lambda row: (row[0], row[1], row[2]))
        first_at = queue[0][0]
        span = (queue[-1][0] - first_at) * self.pace
        log("%d operations over about %d seconds (pace %gs)" % (len(queue), round(span), self.pace), 1)
        started = time.monotonic()
        for at, _reference, _index, entry, step in queue:
            delay = started + (at - first_at) * self.pace - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            self._workflow_step(entry, step)

        log("Final state", 1)
        for entry in entries:
            log("%-14s %-9s %-8s %s"
                % (entry["reference"], entry["desk"], entry["severity"], entry["final"]), 2)

    def _workflow_entries(self):
        path = os.path.join(CONTENT_DIR, "workflow_items.json")
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)

    def _workflow_steps(self, entry):
        """The create, then the walk. One list, so a position in it is the item's progress."""
        return [{"at": entry["at"], "op": "create", "user": entry["author"]}] + entry["steps"]

    def _workflow_pending_from(self, entry):
        """Index of the first step still to run, or None when the item is finished.

        Progress is read back from the instance rather than remembered between runs, so a run cut
        off halfway carries on where it stopped. Moves are counted from `archive_history`, an edit
        is recognised by the text it adds, and a release by the history record it leaves.
        """
        guid = GUID_PREFIX + entry["reference"]
        history = self.api.find_all("archive_history", {"item_id": guid}, max_results=200)
        if not history:
            return 0
        if any(record.get("operation") == "publish" for record in history):
            # A release is always the last step of a walk, so nothing can be left to do.
            return None
        moves = sum(1 for record in history if record.get("operation") == "move")
        item = self.api.get_item("archive", guid) or {}
        body = item.get("body_html") or ""
        index = 1
        for step in entry["steps"]:
            if step["op"] == "move":
                if moves <= 0:
                    break
                moves -= 1
            elif step["op"] == "edit":
                if step["add_html"] not in body:
                    break
            elif step["op"] == "release":
                break
            index += 1
        return None if index > len(entry["steps"]) else index

    def _workflow_step(self, entry, step):
        reference = entry["reference"]
        guid = GUID_PREFIX + reference
        try:
            session = self._session(step["user"])
            if step["op"] == "create":
                session.post("archive", self._article(entry, "alert"))
                log("%s created by %s in %s / %s"
                    % (reference, step["user"], entry["desk"], entry["workflow"].title()), 1)
            elif step["op"] == "move":
                session.post(
                    "archive/%s/move" % guid,
                    {"task": {"desk": str(self.desk_id(step["desk"])),
                              "stage": str(self.stage_id(step["desk"], step["stage"]))}},
                )
                log("%s moved to %s / %s by %s" % (reference, step["desk"], step["stage"], step["user"]), 1)
            elif step["op"] == "edit":
                self._workflow_edit(session, guid, step, reference)
            elif step["op"] == "release":
                if self._release(session, guid, reference):
                    log("%s released by %s" % (reference, step["user"]), 1)
        except ApiError as err:
            self.note(
                "Workflow step %s on %s failed: %s %s" % (step["op"], reference, err.status, err.body[:200])
            )

    def _workflow_edit(self, session, guid, step, reference):
        """A real change to the report, so the item gains a version and the history a record."""
        item = session.get_item("archive", guid)
        if not item:
            self.note("Cannot edit %s, it is not in archive." % reference)
            return
        if step["add_html"] in (item.get("body_html") or ""):
            log("%s already carries this edit" % reference, 1)
            return
        updates = {"body_html": (item.get("body_html") or "") + step["add_html"]}
        for field, key in (("abstract", "summary"), ("ednote", "ednote")):
            if step.get(key):
                updates[field] = step[key]
        session.patch("archive", guid, updates, etag=item.get("_etag"))
        log("%s edited by %s" % (reference, step["user"]), 1)


def write_geo_index():
    """The map mock in the portal reads this. `_demo_geo` never goes to Superdesk."""
    rows = []
    with open(os.path.join(CONTENT_DIR, "alerts.json"), encoding="utf-8") as handle:
        for entry in json.load(handle):
            geo = entry.get("_demo_geo") or {}
            countries = entry.get("country") or []
            regions = entry.get("region") or []
            sectors = entry.get("sector") or []
            rows.append(
                {
                    "reference": entry["reference"],
                    "title": entry["title"],
                    "severity": entry["severity"],
                    "lat": geo.get("lat"),
                    "lon": geo.get("lon"),
                    # The primary value, for a pin label. The full lists follow it.
                    "country": countries[0] if countries else None,
                    "region": regions[0] if regions else None,
                    "sector": sectors[0] if sectors else None,
                    "countries": countries,
                    "regions": regions,
                    "sectors": sectors,
                    "workflow": entry["workflow"],
                }
            )
    path = os.path.join(CONTENT_DIR, "geo_index.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(rows, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    return path, len(rows)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Seed a Superdesk instance into the Briefdesk demo state.")
    parser.add_argument("--dry-run", action="store_true", help="print the planned operations, make no request")
    parser.add_argument(
        "--only",
        action="append",
        choices=SECTIONS,
        help="run only this section, repeatable. Sections assume earlier ones already ran.",
    )
    parser.add_argument("--verbose", action="store_true", help="print every request")
    parser.add_argument(
        "--pace",
        type=float,
        default=D.WORKFLOW_PACE_SECONDS,
        help="seconds per unit of the workflow schedule, default %(default)g. 0 runs it back to back.",
    )
    parser.add_argument("--insecure", action="store_true", help="do not verify the TLS certificate")
    parser.add_argument("--write-geo-index", action="store_true", help="only regenerate content/geo_index.json")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv or sys.argv[1:])

    path, count = write_geo_index()
    log("geo index: %d alerts written to %s" % (count, path))
    if args.write_geo_index:
        return 0

    url = os.environ.get("SUPERDESK_URL")
    if not url:
        if not args.dry_run:
            log("SUPERDESK_URL is not set.")
            return 2
        url = "https://superdesk.invalid"

    api = Superdesk(url, dry_run=args.dry_run, verbose=args.verbose, insecure=args.insecure)
    log("")
    log("Briefdesk seeder%s" % (" (dry run, no request will be made)" if args.dry_run else ""))
    log("instance: %s" % api.base_url)

    if not args.dry_run:
        user = os.environ.get("SUPERDESK_USER", "admin")
        password = os.environ.get("SUPERDESK_PASSWORD")
        token = os.environ.get("SUPERDESK_TOKEN")
        if token:
            api.token = token
            log("using SUPERDESK_TOKEN")
        elif password:
            api.login(user, password)
            log("signed in as %s" % user)
        else:
            log("Set SUPERDESK_PASSWORD (or SUPERDESK_TOKEN).")
            return 2

    seeder = Seeder(
        api,
        portal_url=os.environ.get("PORTAL_URL"),
        portal_push_url=os.environ.get("PORTAL_PUSH_URL"),
        openrouter_key=os.environ.get("OPENROUTER_API_KEY"),
        ai_model=os.environ.get("BRIEFDESK_AI_MODEL", D.AI_DEFAULT_MODEL),
        insecure=args.insecure,
        pace=max(args.pace, 0.0),
    )

    wanted = args.only or SECTIONS
    for section in SECTIONS:
        if section not in wanted:
            continue
        log("")
        try:
            getattr(seeder, "section_%s" % section)()
        except ApiError as err:
            log("")
            log("Section %r failed." % section)
            log(str(err))
            return 1

    log("")
    log("Done.")
    if seeder.ai_action_ids:
        log("AI action ids (paste into ACTION_IDS in client/briefdesk/ai-actions.ts if needed):")
        for name, action_id in sorted(seeder.ai_action_ids.items()):
            log("%-16s %s" % (name, action_id), 1)
    if seeder.notes:
        log("Things to look at:")
        for note in seeder.notes:
            log("- %s" % note, 1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
