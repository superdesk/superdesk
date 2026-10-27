"""Seed a Superdesk instance into a market's demo state, from the market's contract and content.

Re-runnable: everything is looked up by name or by a deterministic id and then created or updated,
never duplicated. Sections run in dependency order; `--only` picks some of them and assumes the
earlier ones already ran.
"""
import argparse
import contextlib
import datetime
import getpass
import io
import json
import os
import sys
import time
import urllib.parse

from . import model as M
from .contract import Market
from .sdapi import ApiError, HttpTransport, Superdesk, log
from .sim import SimInstance, SimTransport, develop_vocabularies

SECTIONS = [
    "vocabularies",
    "roles",
    "users",
    "profiles",
    "teams",
    "templates",
    "ingest",
    "publishing",
    "briefing",
    "dashboards",
    "ai",
    "planning",
    "content",
    "triage",
    "workflow",
]
ALIASES = {"desks": "teams", "highlights": "briefing"}

WEEKDAYS = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

# Widget layout on a team dashboard, by widget id. Anything a contract lists that is not here is
# placed below the others at its default size.
WIDGETS = {
    "aggregate": {"row": 1, "col": 1, "sizex": 2, "sizey": 2},
    "activity": {"row": 1, "col": 3, "sizex": 1, "sizey": 2},
    "ingest-stats": {"row": 3, "col": 1, "sizex": 1, "sizey": 1},
    "world-clock": {"row": 3, "col": 2, "sizex": 2, "sizey": 1},
}


def iso(moment):
    return moment.strftime("%Y-%m-%dT%H:%M:%S+0000")


def utc_iso(hours_ago=0):
    return iso(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours_ago))


def utc_at(days=0, hour=9):
    """A whole hour, so many days from today. Calendar entries are placed relative to the run so the
    demo always looks current."""
    moment = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days)
    return moment.replace(hour=hour, minute=0, second=0, microsecond=0)


def utc_in(hours=0):
    return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=hours)


def html_list(lines):
    return "<ul>%s</ul>" % "".join("<li>%s</li>" % line for line in lines)


class Seeder:
    def __init__(self, api, market, demo_password=None, portal_url=None, portal_push_url=None, push_key=None, ai_key=None, pace=None):
        self.api = api
        self.market = market
        self.demo_password = demo_password
        self.portal_url = (portal_url or "").rstrip("/")
        # Where this server reaches the portal, which is not always the address a browser uses: two
        # instances on the same host may only see each other by their internal names.
        self.portal_push_url = (portal_push_url or "").rstrip("/") or self.portal_url
        self.push_key = push_key
        self.ai_key = ai_key
        self.pace = market.get("superdesk.workflow.pace_seconds", 20) if pace is None else pace
        self.guid_prefix = market.get("fiction.sample_content.guid_prefix") or "urn:%s:demo:" % market.slug
        self.cv_names = M.vocabulary_names(market)
        self.severity_urgency = M.severity_urgency(market)
        self.severity_scheme = market.get("severity.taxonomy")
        self._cache = {}
        self._sessions = {}
        self.notes = []
        self.ai_action_ids = {}

    # -- generic upsert -------------------------------------------------------

    def upsert(self, resource, lookup, doc, label, existing=None):
        """Create the document, or patch the fields of an existing one that differ."""
        if existing is None:
            existing = self.api.find_one(resource, **lookup)
        if not existing:
            created = self.api.post(resource, doc)
            log("created %s" % label, 1)
            return created
        updates = {key: value for key, value in doc.items() if key != "_id" and existing.get(key) != value}
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

    # -- lookups --------------------------------------------------------------

    def _cached(self, key, loader):
        if key not in self._cache:
            self._cache[key] = loader()
        return self._cache[key]

    def _id_by_name(self, resource, name):
        def load():
            found = self.api.find_one(resource, name=name)
            return found["_id"] if found else None

        return self._cached("%s:%s" % (resource, name), load)

    def user(self, username):
        return self._cached("user:%s" % username, lambda: self.api.find_one("users", username=username))

    def user_id(self, username):
        found = self.user(username)
        return found["_id"] if found else None

    def desk(self, name):
        return self._cached("desk:%s" % name, lambda: self.api.find_one("desks", name=name))

    def desk_id(self, name):
        found = self.desk(name)
        if not found:
            raise SystemExit("Team %r does not exist yet. Run the teams section first." % name)
        return found["_id"]

    def stage_id(self, desk_name, stage_name):
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

        Superdesk lower-cases a template name on create, keeps the case it is given on update, and
        checks uniqueness without regard to case, so an exact match on the name misses.
        """
        for found in self.api.find_all("content_templates", max_results=500):
            if (found.get("template_name") or "").lower() == template_name.lower():
                return found
        return None

    def template_id(self, template_name):
        found = self.template(template_name)
        return found["_id"] if found else None

    def subject(self, pairs):
        """(scheme, qcode) pairs to the item `subject` entries the portal filters on."""
        terms = []
        for scheme, qcode in pairs:
            name = self.cv_names.get(scheme, {}).get(qcode)
            if name is None:
                raise SystemExit("Unknown %s value %r. Check the vocabularies in the contract." % (scheme, qcode))
            terms.append({"name": name, "qcode": qcode, "scheme": scheme})
        return terms

    def _session(self, username):
        """A signed-in client for one staff member. Comments are attributed to the session user,
        some tasking actions are refused to anybody but the assignee, and starting work reassigns
        the tasking to whoever asked for it."""
        if username == self.api.username or str(self.user_id(username)) == str(self.api.user_id):
            return self.api
        if username not in self._sessions:
            if not self.demo_password:
                raise SystemExit("Signing in as %s needs the demo password (see `demo_password_env` in the README)." % username)
            client = self.api.another()
            client.login(username, self.demo_password)
            self._sessions[username] = client
        return self._sessions[username]

    # -- vocabularies ---------------------------------------------------------

    def _vocabularies(self):
        """The relabelled native field is derived from the vocabulary as the product ships it, never
        from the instance's copy, which after the first run is already relabelled."""
        native = self.market.get("severity.native_field") or "urgency"
        if not self.market.get("severity.levels"):
            return M.market_vocabularies(self.market, {})
        base = next((v for v in develop_vocabularies() if v["_id"] == native), None) or self.api.get_item("vocabularies", native)
        if not base:
            raise SystemExit("The instance has no `%s` vocabulary to relabel." % native)
        return M.market_vocabularies(self.market, base)

    def section_vocabularies(self):
        log("Vocabularies")
        self._upsert_vocabularies(self._vocabularies())

    def _upsert_vocabularies(self, vocabularies):
        for doc in vocabularies:
            existing = self.api.get_item("vocabularies", doc["_id"])
            if not existing:
                self.api.post("vocabularies", doc)
                log("created vocabulary %s" % doc["_id"], 1)
                continue
            # The server strips is_active from items on read, so items compare on what matters.
            updates = {k: v for k, v in doc.items() if k != "_id" and _comparable(existing.get(k)) != _comparable(v)}
            if updates:
                self.api.patch("vocabularies", doc["_id"], updates, etag=existing.get("_etag"))
                log("updated vocabulary %s (%s)" % (doc["_id"], ", ".join(sorted(updates))), 1)
            else:
                log("unchanged vocabulary %s" % doc["_id"], 1)

    # -- people -----------------------------------------------------------------

    def section_roles(self):
        log("Roles")
        for role in M.roles(self.market):
            doc = {"name": role["name"], "description": role["description"], "privileges": {name: 1 for name in sorted(set(role["privileges"]))}}
            for optional in ("author_role", "editor_role"):
                if role.get(optional):
                    doc[optional] = role[optional]
            self.upsert("roles", {"name": role["name"]}, doc, "role %s" % role["name"])
            self._cache.pop("roles:%s" % role["name"], None)

    def section_users(self):
        log("Users")
        for user in M.staff(self.market):
            name = "%s %s" % (user["first_name"], user["last_name"])
            doc = {
                "username": user["username"],
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "display_name": name,
                "email": M.staff_email(self.market, user["username"]),
                "sign_off": user["sign_off"],
                "byline": name,
                "job_title": user.get("job_title", ""),
                "user_type": "user",
                "is_active": True,
                "is_enabled": True,
                "is_author": True,
                "needs_activation": False,
                "language": self.market.language,
            }
            role_id = self._id_by_name("roles", user["role"])
            if role_id:
                doc["role"] = role_id
            existing = self.api.find_one("users", username=user["username"])
            if not existing:
                if not self.demo_password:
                    raise SystemExit("Creating %s needs the demo password (see `demo_password_env` in the README)." % user["username"])
                doc["password"] = self.demo_password
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

    # -- report types -------------------------------------------------------------

    def section_profiles(self):
        log("Report types")
        for spec in M.report_types(self.market):
            profile = M.content_profile(self.market, spec)
            existing = self.api.get_item("content_types", profile["_id"])
            # The client lists report types with `where type = text`. One without a type is valid
            # on the server but never appears in the editor's selector or in the team settings.
            base = {"label": profile["label"], "description": profile["description"], "priority": profile["priority"], "enabled": True, "type": "text"}
            if not existing:
                doc = dict(base)
                doc["_id"] = profile["_id"]
                self.api.post("content_types", doc)
                log("created report type %s" % profile["label"], 1)
            else:
                updates = {k: v for k, v in base.items() if existing.get(k) != v}
                if updates:
                    self.api.patch("content_types", profile["_id"], updates, etag=existing.get("_etag"))
            # Sent on every run: the fields are the part a redeploy has been seen to lose. The
            # server folds the custom vocabularies back into `subject` on save, which is what makes
            # selected values land in subject[] with their scheme.
            editor = dict(profile["editor"])
            editor.update(M.disabled_default_fields(editor))
            self.api.patch("content_types", profile["_id"], {"editor": editor, "schema": profile["schema"]})
            log("configured fields on %s" % profile["label"], 1)

    # -- teams ----------------------------------------------------------------------

    def section_teams(self):
        log("Teams and stages")
        profiles = {spec["id"]: True for spec in M.report_types(self.market)}
        for spec in M.teams(self.market):
            wanted = {
                "description": spec.get("description", ""),
                "source": spec.get("source", ""),
                "desk_type": "production",
                "desk_language": self.market.language,
                # Without a list of allowed report types the profile selector in the editor header
                # is empty.
                "content_profiles": profiles,
            }
            existing = self.api.find_one("desks", name=spec["name"])
            if not existing:
                doc = {"name": spec["name"]}
                doc.update(wanted)
                existing = self.api.post("desks", doc)
                log("created team %s" % spec["name"], 1)
            else:
                updates = {k: v for k, v in wanted.items() if existing.get(k) != v}
                if updates:
                    self.api.patch("desks", existing["_id"], updates, etag=existing.get("_etag"))
                log("team %s present" % spec["name"], 1)
            self._cache.pop("desk:%s" % spec["name"], None)
            self._rename_default_stages(existing, spec["stages"])
            self._extra_stages(existing, spec["stages"])
            self._order_stages(existing, spec["stages"])

        for spec in M.teams(self.market):
            self._team_members(spec["name"])
            self._board(spec["name"], spec["stages"])

        log("Default team per user", 1)
        for user in M.staff(self.market):
            self._default_team(user["username"], user["default_team"])
        admin_team = self.market.get("fiction.admin_default_team")
        if admin_team and self.api.username:
            self._default_team(self.api.username, admin_team)

    def _default_team(self, username, team_name):
        found = self.user(username)
        if not found:
            return
        desk_id = self.desk_id(team_name)
        if str(found.get("desk") or "") != str(desk_id):
            self.api.patch("users", found["_id"], {"desk": desk_id})
            log("default team of %s set to %s" % (username, team_name), 2)

    def _rename_default_stages(self, desk, stages):
        """A new desk arrives with an Incoming and a Working stage. They are renamed in place so the
        board reads in the market's terms and the default incoming stage keeps its meaning."""
        for stage_id, name in ((desk.get("incoming_stage"), stages[0]), (desk.get("working_stage"), stages[1] if len(stages) > 1 else None)):
            if not stage_id or not name:
                continue
            stage = self.api.get_item("stages", stage_id)
            if not stage or stage.get("name") == name:
                continue
            self.api.patch("stages", stage_id, {"name": name}, etag=stage.get("_etag"))
            log("renamed stage to %s" % name, 2)

    def _extra_stages(self, desk, stages):
        task_status = self.market.get("fiction.stage_task_status") or {}
        present = {stage["name"] for stage in self.api.find_all("stages", {"desk": desk["_id"]})}
        for name in stages[2:]:
            if name in present:
                continue
            # What a stage does to the tasking linked to an item that lands in it. Without it the
            # order of the stage list would decide, which silently changes what Planning shows.
            self.api.post(
                "stages",
                {"name": name, "desk": desk["_id"], "description": "%s stage" % name, "is_visible": True, "task_status": task_status.get(name, "in_progress")},
            )
            log("created stage %s" % name, 2)

    def _order_stages(self, desk, stages):
        """The two automatic stages are created working-first, so without this the board would read
        Analysis, Incoming, Review."""
        by_name = {stage["name"]: stage for stage in self.api.find_all("stages", {"desk": desk["_id"]})}
        ordered = [by_name[name] for name in stages if name in by_name]
        if len(ordered) != len(stages):
            return
        if [stage.get("desk_order") for stage in ordered] == list(range(1, len(stages) + 1)):
            return
        self.api.post("stages_order", {"desk": str(desk["_id"]), "stages": [str(s["_id"]) for s in ordered]})
        log("ordered the stages as %s" % ", ".join(stages), 2)

    def _team_members(self, team_name):
        members = [user["username"] for user in M.staff(self.market) if team_name in user["teams"]]
        desk = self.desk(team_name)
        if not desk:
            return
        wanted = [str(self.user_id(name)) for name in members if self.user_id(name)]
        # Superdesk shows a user only the teams they belong to, so an administrator who is no
        # member sees no teams and an empty board.
        if self.market.get("fiction.admin_member_of_all_teams", True) and self.api.user_id and str(self.api.user_id) not in wanted:
            wanted.append(str(self.api.user_id))
        wanted = sorted(wanted)
        current = sorted(str(member["user"]) for member in desk.get("members") or [])
        if wanted == current:
            log("members of %s unchanged" % team_name, 2)
            return
        self.api.patch("desks", desk["_id"], {"members": [{"user": member} for member in wanted]})
        self._cache.pop("desk:%s" % team_name, None)
        log("members of %s set to %s" % (team_name, ", ".join(members)), 2)

    def _board(self, team_name, stages):
        """Without monitoring settings the board shows the default groups, not the team's stages.
        A released report lives in `published`, which a stage group never queries, so hidden stages
        stay on the team but off the board."""
        hidden = set(self.market.get("fiction.board_hidden_stages") or [])
        shown = [name for name in stages if name not in hidden]
        desk = self.desk(team_name)
        if not desk:
            return
        settings = [{"_id": str(self.stage_id(team_name, name)), "type": "stage", "max_items": 30} for name in shown]
        settings.append({"_id": "%s:output" % desk["_id"], "type": "deskOutput", "max_items": 30})
        if desk.get("monitoring_settings") == settings:
            log("board of %s unchanged" % team_name, 2)
            return
        self.api.patch("desks", desk["_id"], {"monitoring_settings": settings})
        self._cache.pop("desk:%s" % team_name, None)
        log("board of %s set to %s" % (team_name, ", ".join(shown)), 2)

    # -- templates --------------------------------------------------------------------

    def section_templates(self):
        log("Templates")
        for template in M.templates(self.market):
            data = dict(template["data"])
            if "subject" in data:
                data["subject"] = self.subject(data["subject"])
            data.setdefault("type", "text")
            data["profile"] = template["profile"]
            data.setdefault("language", self.market.language)
            doc = {
                "template_name": template["template_name"],
                "template_type": template["template_type"],
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
        for spec in M.teams(self.market):
            found = self.desk(spec["name"])
            if not found:
                continue
            updates = {}
            if found.get("default_content_profile") != spec["default_report_type"]:
                updates["default_content_profile"] = spec["default_report_type"]
            template_id = self.template_id(spec["default_template"])
            if template_id and str(found.get("default_content_template") or "") != str(template_id):
                updates["default_content_template"] = template_id
            if updates:
                self.api.patch("desks", found["_id"], updates)
                self._cache.pop("desk:%s" % spec["name"], None)
                log("%s defaults to %s / %s" % (spec["name"], spec["default_report_type"], spec["default_template"]), 2)
            else:
                log("%s defaults unchanged" % spec["name"], 2)

    # -- sources ------------------------------------------------------------------------

    def section_ingest(self):
        log("Sources and routing")
        ingest = self.market.get("superdesk.ingest") or {}
        if not ingest.get("providers"):
            log("no sources in the contract", 1)
            return
        route = ingest["route_to"]
        name = ingest.get("routing_scheme") or "%s intake" % route["team"]
        scheme = {
            "name": name,
            "rules": [
                {
                    "name": "Everything to %s %s" % (route["team"], route["stage"]),
                    "handler": "desk_fetch_publish",
                    "filter": None,
                    "actions": {"fetch": [{"desk": self.desk_id(route["team"]), "stage": self.stage_id(route["team"], route["stage"])}], "exit": True},
                    "schedule": {
                        "day_of_week": ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"],
                        "hour_of_day_from": None,
                        "hour_of_day_to": None,
                        "time_zone": "UTC",
                    },
                }
            ],
        }
        saved = self.upsert("routing_schemes", {"name": name}, scheme, "routing scheme %s" % name)
        for provider in ingest["providers"]:
            doc = {
                "name": provider["name"],
                "source": provider["source"],
                # The rss feeding service reads Atom as well.
                "feeding_service": "rss" if provider.get("feed", "rss") in ("rss", "atom") else provider["feed"],
                "content_types": ["text"],
                "is_closed": False,
                "update_schedule": {"minutes": provider.get("update_minutes", 5)},
                "idle_time": {"hours": 0, "minutes": 0},
                "routing_scheme": saved["_id"],
                # The instance may sit behind a proxy that cannot reach the feed at create time, and
                # a failed config test rejects the whole POST.
                "skip_config_test": True,
                "config": {"url": provider["url"], "auth_required": False},
            }
            self.upsert("ingest_providers", {"name": provider["name"]}, doc, "source %s" % provider["name"])

    # -- delivery ---------------------------------------------------------------------------

    def section_publishing(self):
        log("Content filters, packages and recipients")
        names = M.portal_names(self.market)
        if not self.portal_push_url:
            self.note("Neither PORTAL_URL nor PORTAL_PUSH_URL is set, so the %s push destinations have no resource_url." % names["recipient"])
        if not self.push_key:
            self.note("The portal push key is not set (%s), so the push destinations carry no secret token." % self.push_key_env())

        for condition in M.filter_conditions(self.market):
            self.upsert("filter_conditions", {"name": condition["name"]}, dict(condition), "filter condition %s" % condition["name"])
            self._cache.pop("filter_conditions:%s" % condition["name"], None)

        for content_filter in M.content_filters(self.market):
            expressions = []
            for group in content_filter["expressions"]:
                ids = [self._id_by_name("filter_conditions", name) for name in group]
                expressions.append({"expression": {"fc": [str(i) for i in ids if i]}})
            doc = {"name": content_filter["name"], "content_filter": expressions, "is_global": False}
            self.upsert("content_filters", {"name": content_filter["name"]}, doc, "content filter %s" % content_filter["name"])
            self._cache.pop("content_filters:%s" % content_filter["name"], None)

        for product in M.products(self.market):
            doc = {"name": product["name"], "description": product["description"], "product_type": product["product_type"]}
            doc["content_filter"] = {"filter_id": str(self._id_by_name("content_filters", product["content_filter"])), "filter_type": "permitting"}
            self.upsert("products", {"name": product["name"]}, doc, "package %s" % product["name"])
            self._cache.pop("products:%s" % product["name"], None)

        firm_domain = self.market.require("fiction.firm.email_domain")
        push_path = self.market.get("superdesk.recipients.portal.push_path") or "/push"
        portal_product = str(self._id_by_name("products", names["product"]))
        self._upsert_subscriber(self._push_recipient(names["recipient"], portal_product, [("%s push" % names["recipient"], "newsroom ninjs")], firm_domain, push_path))
        # A second recipient for the calendar. Superdesk applies a recipient's products once and then
        # hands the item to every destination it has, so the only way to keep the NINJS destination
        # away from calendar entries is a recipient of their own.
        calendar_product = str(self._id_by_name("products", names["calendar_product"]))
        self._upsert_subscriber(self._push_recipient(names["calendar_recipient"], calendar_product, M.calendar_destinations(self.market), firm_domain, push_path))

        if self.market.get("superdesk.recipients.email_per_client", True):
            for client in self.market.get("fiction.clients") or []:
                emails = M.client_emails(client)
                if not emails:
                    continue
                doc = {
                    "name": client["name"],
                    "subscriber_type": "all",
                    "email": emails[0],
                    "is_active": True,
                    "is_targetable": True,
                    "sequence_num_settings": {"min": 1, "max": 9999},
                    "products": [str(self._id_by_name("products", "%s entitlement" % client["name"]))],
                    "destinations": [{"name": "Email to %s" % client["name"], "format": "email", "delivery_type": "email", "config": {"recipients": ";".join(emails)}}],
                }
                self._upsert_subscriber(doc)

    def push_key_env(self):
        return self.market.get("superdesk.recipients.portal.push_key_env") or "PORTAL_PUSH_KEY"

    def _push_recipient(self, name, product_id, destinations, firm_domain, push_path):
        config = {
            "resource_url": "%s%s" % (self.portal_push_url, push_path) if self.portal_push_url else "",
            "assets_url": "%s%s_binary" % (self.portal_push_url, push_path) if self.portal_push_url else "",
        }
        if self.push_key:
            config["secret_token"] = self.push_key
        return {
            "name": name,
            "subscriber_type": "all",
            "email": "portal@%s" % firm_domain,
            "is_active": True,
            "is_targetable": True,
            "sequence_num_settings": {"min": 1, "max": 9999},
            "products": [product_id],
            "api_products": [product_id],
            "destinations": [{"name": dname, "format": fmt, "delivery_type": "http_push", "config": dict(config)} for dname, fmt in destinations],
        }

    def _upsert_subscriber(self, doc):
        """The server gives every destination an id and a preview url and never returns the secret
        token, so stored destinations always look different from the ones sent. They are compared
        on what matters and only sent when that differs."""

        def comparable(destinations):
            return [
                {
                    "name": d.get("name"),
                    "format": d.get("format"),
                    "delivery_type": d.get("delivery_type"),
                    "config": {k: v for k, v in (d.get("config") or {}).items() if k != "secret_token"},
                }
                for d in destinations or []
            ]

        existing = self.api.find_one("subscribers", name=doc["name"])
        if existing and comparable(existing.get("destinations")) == comparable(doc["destinations"]):
            doc = {k: v for k, v in doc.items() if k != "destinations"}
        self.upsert("subscribers", {"name": doc["name"]}, doc, "recipient %s" % doc["name"], existing=existing)

    # -- briefing list ------------------------------------------------------------------------

    def section_briefing(self):
        spec = self.market.get("briefing_list") or {}
        if not spec.get("name"):
            return
        log("Briefing lists")
        doc = {
            "name": spec["name"],
            "desks": [self.desk_id(name) for name in spec["teams"]],
            "auto_insert": spec.get("auto_insert", "now-24h"),
            "groups": spec.get("groups") or list(spec["teams"]),
        }
        export = spec.get("export_template") or {}
        template_id = self.template_id(export["name"]) if export.get("name") else None
        if template_id:
            doc["template"] = str(template_id)
        elif export.get("name"):
            self.note("Briefing list template %r is missing, run the templates section." % export["name"])
        self.upsert("highlights", {"name": spec["name"]}, doc, "briefing list %s" % spec["name"])

    # -- dashboards ---------------------------------------------------------------------------

    def section_dashboards(self):
        """A dashboard per team; an empty one would wait for somebody to add widgets by hand."""
        log("Dashboards")
        config = self.market.get("superdesk.dashboards") or {}
        wanted = config.get("per_team_widgets") or list(WIDGETS)
        zones = config.get("world_clock_zones") or [self.market.timezone]
        for spec in M.teams(self.market):
            desk = self.desk(spec["name"])
            if not desk:
                continue
            groups = [{"_id": g["_id"], "type": g["type"]} for g in desk.get("monitoring_settings") or [] if g.get("type") == "stage"]
            configuration = {
                "aggregate": {"label": "%s board" % spec["name"], "groups": groups},
                "activity": {"maxItems": 8},
                "ingest-stats": {"source": "provider", "colorScheme": "superdesk", "updateInterval": 5},
                "world-clock": {"zones": zones},
            }
            widgets = []
            for index, widget in enumerate(wanted):
                layout = WIDGETS.get(widget) or {"row": 4 + index, "col": 1, "sizex": 1, "sizey": 1}
                entry = {"_id": widget, "multiple_id": 1, "active": True}
                entry.update(layout)
                entry["configuration"] = configuration.get(widget, {})
                widgets.append(entry)
            existing = self.api.find_one("workspaces", desk=str(desk["_id"]))
            if existing and existing.get("widgets") == widgets:
                log("dashboard of %s unchanged" % spec["name"], 1)
            elif existing:
                self.api.patch("workspaces", existing["_id"], {"widgets": widgets}, etag=existing.get("_etag"))
                log("updated dashboard of %s" % spec["name"], 1)
            else:
                self.api.post("workspaces", {"desk": str(desk["_id"]), "widgets": widgets})
                log("created dashboard of %s" % spec["name"], 1)

    # -- AI -------------------------------------------------------------------------------------

    def section_ai(self):
        """The provider is created only when it does not exist. An existing provider, its key, its
        models and its base URL belong to whoever configured it in Settings and are never sent a
        single write, whatever the environment holds."""
        ai = self.market.get("superdesk.ai") or {}
        if not ai.get("provider_name"):
            return
        log("AI provider and actions")
        provider = self.api.find_one("ai_providers", name=ai["provider_name"])
        if provider:
            log("kept AI provider %s as configured" % ai["provider_name"], 1)
        else:
            doc = {
                "name": ai["provider_name"],
                "provider_type": ai.get("provider_type", "openai_compatible"),
                "default_model": os.environ.get("AI_DEFAULT_MODEL") or ai.get("default_model"),
                "is_default": True,
                "active": True,
            }
            if ai.get("base_url"):
                doc["base_url"] = ai["base_url"]
            if ai.get("label"):
                doc["label"] = ai["label"]
            # A provider is valid without a key and the actions only need its id. The key is left
            # out rather than sent empty, because an explicit null is what clears a stored key.
            if self.ai_key:
                doc["api_key"] = self.ai_key
            else:
                self.note(
                    "%s is not set. The %r provider and the AI actions exist, but runs fail until the key is pasted into Settings, AI providers."
                    % (ai.get("provider_key_env", "AI_PROVIDER_KEY"), ai["provider_name"])
                )
            provider = self.api.post("ai_providers", doc)
            log("created AI provider %s" % ai["provider_name"], 1)

        for action in M.ai_actions(self.market):
            doc = dict(action)
            doc["provider"] = str(provider["_id"])
            doc["active"] = True
            saved = self.upsert("ai_actions", {"name": action["name"]}, doc, "AI action %s" % action["name"])
            self.ai_action_ids[action["name"]] = str(saved.get("_id"))

    # -- planning -------------------------------------------------------------------------------

    def section_planning(self):
        if not (self.market.get("fiction.sample_content.calendar_events") or self.market.get("fiction.sample_content.client_requests")):
            return
        log("Programmes, calendar, requests and taskings")
        agendas = self._programmes()
        self._event_calendars()
        events = self._events()
        requests = self._requests(agendas, events)
        self._post_to_portal(events, requests)

    def _programmes(self):
        agendas = {}
        present = self.api.find_all("agenda")
        for name in self.market.get("superdesk.planning.programmes") or []:
            existing = next((a for a in present if a.get("name") == name), None)
            if existing:
                log("unchanged programme %s" % name, 1)
                agendas[name] = existing["_id"]
                continue
            agendas[name] = self.api.post("agenda", {"name": name, "is_enabled": True})["_id"]
            log("created programme %s" % name, 1)
        return agendas

    def _calendars(self):
        return [(c["qcode"], c["name"]) for c in self.market.get("superdesk.planning.event_calendars") or []]

    def _event_calendars(self):
        """Replace the stock calendars with the market's."""
        calendars = self._calendars()
        if not calendars:
            return
        wanted = [{"name": name, "qcode": qcode, "is_active": True} for qcode, name in calendars]
        existing = self.api.get_item("vocabularies", "event_calendars")
        if not existing:
            self.api.post(
                "vocabularies",
                {"_id": "event_calendars", "display_name": "Event Calendars", "type": "manageable", "unique_field": "qcode", "selection_type": "do not show", "items": wanted},
            )
            log("created the event calendars vocabulary", 1)
            return
        # is_active is stripped from items on read, so only the pairs that matter are compared.
        if [(i.get("qcode"), i.get("name")) for i in existing.get("items") or []] == [(i["qcode"], i["name"]) for i in wanted]:
            log("event calendars unchanged", 1)
            return
        self.api.patch("vocabularies", "event_calendars", {"items": wanted}, etag=existing.get("_etag"))
        log("set the event calendars to %s" % ", ".join(name for _, name in calendars), 1)

    def _event_specs(self):
        return self.market.content("fiction.sample_content.calendar_events")

    def _request_specs(self):
        return self.market.content("fiction.sample_content.client_requests")

    def _event_doc(self, spec):
        start = utc_at(days=spec["days"], hour=spec["hour"])
        dates = {"start": iso(start), "end": iso(start + datetime.timedelta(hours=spec["hours"])), "tz": spec["tz"]}
        repeat = spec.get("repeat")
        if repeat:
            dates["recurring_rule"] = {
                "frequency": repeat["frequency"],
                "interval": repeat.get("interval", 1),
                "byday": WEEKDAYS[start.weekday()],
                "count": repeat["count"],
                "endRepeatMode": "count",
            }
        occur = self.market.require("superdesk.planning.occur_status")[spec["occur_status"]]
        place = spec["location"]
        doc = {
            "name": spec["name"],
            "slugline": spec["key"],
            "definition_short": spec["summary"],
            "definition_long": spec["detail"],
            "internal_note": spec["internal_note"],
            "dates": dates,
            "occur_status": dict(occur),
            "calendars": [{"qcode": spec["calendar"], "name": dict(self._calendars())[spec["calendar"]], "is_active": True}],
            "location": [
                {
                    "qcode": self.guid_prefix + "place:" + spec["key"],
                    "name": place["name"],
                    "address": {"city": place["city"], "country": place["country"], "line": [""]},
                    "location": {"lat": place["lat"], "lon": place["lon"]},
                }
            ],
            "subject": self.subject(spec["subject"]),
            "language": self.market.language,
            "state": "draft",
        }
        if not repeat:
            # A recurring POST generates its own ids for the whole series and drops the guid, so only
            # single entries get a readable one.
            doc["guid"] = self.guid_prefix + "event:" + spec["key"]
        return doc

    def _events(self):
        """Create the calendar. Returns the id of the first occurrence of each entry."""
        log("Calendar", 1)
        by_slugline = {}
        for item in self.api.find_all("events", max_results=500):
            by_slugline.setdefault(item.get("slugline"), []).append(item)
        ids = {}
        for spec in self._event_specs():
            found = sorted(by_slugline.get(spec["key"]) or [], key=lambda e: e["dates"]["start"])
            if found:
                ids[spec["key"]] = found[0]["_id"]
                self._sync_subject("events", found, self.subject(spec["subject"]), "event %s" % spec["key"])
                continue
            created = self.api.post("events", [self._event_doc(spec)])
            ids[spec["key"]] = created["_id"]
            count = spec.get("repeat", {}).get("count", 1)
            log("created event %s (%s, %d occurrence%s)" % (spec["key"], spec["name"], count, "" if count == 1 else "s"), 2)
        return ids

    def _sync_subject(self, resource, items, subject, label):
        """The taxonomy values decide which client sees an entry in the portal, so they are the one
        part of an existing entry the seed keeps authoritative."""
        stale = [item for item in items if item.get("subject") != subject]
        if not stale:
            log("unchanged %s" % label, 2)
            return
        for item in stale:
            self.api.patch(resource, item["_id"], {"subject": subject}, etag=item.get("_etag"))
        log("retagged %s" % label, 2)

    def _request_doc(self, spec, agendas, events):
        coverages = [self._coverage_doc(deliverable) for deliverable in spec["deliverables"]]
        event = next((e for e in self._event_specs() if e["key"] == spec.get("event")), None)
        if event and events.get(spec["event"]):
            planning_date = iso(utc_at(days=event["days"], hour=event["hour"]))
        else:
            planning_date = min(coverage["planning"]["scheduled"] for coverage in coverages)
        doc = {
            "guid": self.guid_prefix + "request:" + spec["slugline"],
            "name": spec["name"],
            "slugline": spec["slugline"],
            "headline": spec["headline"],
            "description_text": spec["description"],
            "planning_date": planning_date,
            "language": self.market.language,
            "ednote": spec["ednote"],
            "internal_note": spec["internal_note"],
            "agendas": [str(agendas[spec["agenda"]])] if spec.get("agenda") in agendas else [],
            "subject": self.subject(spec["subject"]),
            "urgency": spec["urgency"],
            "coverages": coverages,
        }
        if event and events.get(spec["event"]):
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
                "language": self.market.language,
                "priority": deliverable.get("priority", 2),
            },
            "assigned_to": {"desk": str(self.desk_id(deliverable["desk"])), "user": str(self.user_id(deliverable["user"])), "state": "assigned"},
        }

    def _requests(self, agendas, events):
        log("Client requests, deliverables and taskings", 1)
        by_slugline = {item.get("slugline"): item for item in self.api.find_all("planning", max_results=500)}
        created = {}
        for spec in self._request_specs():
            item = by_slugline.get(spec["slugline"])
            if item:
                self._sync_subject("planning", [item], self.subject(spec["subject"]), "request %s" % spec["slugline"])
            else:
                item = self.api.post("planning", self._request_doc(spec, agendas, events))
                log("created request %s with %d deliverable(s)" % (spec["slugline"], len(spec["deliverables"])), 2)
            created[spec["slugline"]] = item["_id"]
            self._drive_taskings(spec, item)
        return created

    def _drive_taskings(self, spec, item):
        for deliverable in spec["deliverables"]:
            coverage = next((c for c in item.get("coverages") or [] if (c.get("planning") or {}).get("slugline") == deliverable["ref"]), None)
            if not coverage:
                self.note("Request %s has no deliverable %s, so its tasking was not touched." % (spec["slugline"], deliverable["ref"]))
                continue
            assigned_to = coverage.get("assigned_to") or {}
            assignment_id = assigned_to.get("assignment_id")
            if not assignment_id:
                self.note("Deliverable %s came back without a tasking." % deliverable["ref"])
                continue
            try:
                self._advance_tasking(deliverable, assignment_id, assigned_to.get("state"))
            except ApiError as err:
                self.note("Could not move tasking %s to %s: %s %s" % (deliverable["ref"], deliverable["state"], err.status, err.body[:200]))

    def _advance_tasking(self, deliverable, assignment_id, state):
        """Walk one tasking to its demo state through the real workflow, and no further.

        States: assigned (left in To Do), in_progress (the assignee starts work, which creates a
        report from `template`), completed (started, then completed), linked (an already released
        report is linked to the deliverable, which completes it).
        """
        target = deliverable["state"]
        started = ("in_progress", "submitted", "completed")
        if target == "assigned" or (target == "linked" and state in started):
            log("tasking %s is %s" % (deliverable["ref"], state), 3)
            return
        if target == "linked":
            # The released report keeps its author; only the delivery is recorded.
            self.api.post("assignments/link", [{"assignment_id": str(assignment_id), "item_id": self.guid_prefix + deliverable["link"], "reassign": False}])
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

    def _post_to_portal(self, events, requests):
        """Post the client-visible part of the calendar. Posting is what hands an entry to the
        recipients, so anything left unposted stays inside the firm. Events are posted unless they
        say `post: false`; requests only when they say `post: true`."""
        log("Releasing the calendar to the portal", 1)
        for spec in self._event_specs():
            if spec.get("post") is False:
                log("event %s stays internal" % spec["key"], 2)
                continue
            self._post_one("events", events.get(spec["key"]), spec["key"], "event", update_method="all" if spec.get("repeat") else None)
        for spec in self._request_specs():
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

    # -- sample reports -----------------------------------------------------------------------------

    def _content_entries(self):
        for type_id, relative in (self.market.get("fiction.sample_content.reports") or {}).items():
            with open(self.market.path(relative), encoding="utf-8") as handle:
                for entry in json.load(handle):
                    yield entry, type_id

    def _default_type(self, entry):
        return entry.get("report_type") or M.team(self.market, entry["desk"])["default_report_type"]

    def _article(self, entry, type_id):
        pairs = []
        for spec in self.market.get("vocabularies") or []:
            value = entry.get(spec["id"])
            for qcode in value if isinstance(value, list) else [value] if value else []:
                pairs.append((spec["id"], qcode))

        if entry.get("body_html"):
            body = entry["body_html"]
        else:
            skeleton = M.report_type(self.market, type_id).get("body_skeleton", "")
            body = "".join("<h2>%s</h2><p>%s</p>" % (heading, entry.get(heading.lower().replace(" ", "_"), "")) for heading in M.body_headings(skeleton))

        extra = {}
        for field in self.market.get("custom_text_fields") or []:
            value = entry.get(field["id"])
            if value:
                extra[field["id"]] = html_list(value) if isinstance(value, list) else value

        created = utc_iso(hours_ago=entry.get("hours_ago", 0))
        level = self.severity_urgency.get(entry.get(self.severity_scheme or "severity"), M.default_urgency(self.market))
        doc = {
            "guid": self.guid_prefix + entry["reference"],
            "type": "text",
            "profile": type_id,
            "state": "fetched",
            "language": self.market.language,
            "headline": entry["title"],
            "slugline": entry["reference"],
            "abstract": entry["summary"],
            "body_html": body,
            "byline": entry["byline"],
            "urgency": level,
            "priority": level,
            "subject": self.subject(pairs),
            "extra": extra,
            "firstcreated": created,
            "versioncreated": created,
            "task": {
                "desk": self.desk_id(entry["desk"]),
                "stage": self.stage_id(entry["desk"], M.stage_named(self.market, entry["desk"], entry["workflow"])),
                "user": self.user_id(entry["author"]),
            },
        }
        if entry.get("ednote"):
            doc["ednote"] = entry["ednote"]
        return doc

    def _released(self, entry):
        """An entry whose stage closes its tasking (task status `done`) is released after creation."""
        done = {stage for stage, status in (self.market.get("fiction.stage_task_status") or {}).items() if status == "done"}
        return M.stage_named(self.market, entry["desk"], entry["workflow"]) in done or entry["workflow"].lower() == "released"

    def section_content(self):
        """Creates what is missing and releases only what it created, so a second run releases
        nothing. A release reaches every recipient it matches: the portal and client emails."""
        log("Sample reports")
        created_ids = {}
        published = []
        for entry, type_id in self._content_entries():
            guid = self.guid_prefix + entry["reference"]
            existing = self.api.get_item("archive", guid)
            if existing:
                log("report %s already exists (%s)" % (entry["reference"], existing.get("state")), 1)
                created_ids[entry["reference"]] = existing["_id"]
                continue
            item = self.api.post("archive", self._article(entry, type_id))
            created_ids[entry["reference"]] = item["_id"]
            log("created %s %s (%s)" % (type_id, entry["reference"], entry["workflow"]), 1)
            if self._released(entry):
                published.append((entry, item))

        if published:
            log("Releasing", 1)
        for entry, item in published:
            if self._release(self.api, item["_id"], entry["reference"], etag=item.get("_etag")):
                log("released %s" % entry["reference"], 2)

        self._review_comments(created_ids)
        self._mark_for_briefing(created_ids)

    def _release(self, session, item_id, label, etag=None):
        """Release through the endpoint the Release button uses."""
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
        """Comments are attributed to the session user, so the reviewer signs in and posts its own.
        A comment already there is not posted again."""
        spec = self.market.get("fiction.sample_content.review_comment") or {}
        if not spec.get("user"):
            return
        stage = (spec.get("stage") or "review").lower()
        in_review = [(entry, created_ids.get(entry["reference"])) for entry, _ in self._content_entries() if entry["workflow"].lower() == stage]
        in_review = [(entry, item_id) for entry, item_id in in_review if item_id]
        if not in_review:
            return
        log("Review comments", 1)
        try:
            reviewer = self._session(spec["user"])
        except ApiError as err:
            self.note("Could not sign in as %s to leave review comments: %s" % (spec["user"], err.status))
            return
        for entry, item_id in in_review:
            present = self.api.find_all("item_comments", {"item": str(item_id)})
            if any(c.get("text") == spec["text"] for c in present):
                log("%s already carries the review comment" % entry["reference"], 2)
                continue
            try:
                reviewer.post("item_comments", {"item": str(item_id), "text": spec["text"]})
                log("commented on %s" % entry["reference"], 2)
            except ApiError as err:
                self.note("Could not comment on %s: %s" % (entry["reference"], err.status))

    def _mark_for_briefing(self, created_ids):
        spec = self.market.get("briefing_list") or {}
        rule = spec.get("mark") or {}
        if not spec.get("name") or not rule:
            return
        highlight = self.api.find_one("highlights", name=spec["name"])
        if not highlight:
            self.note("Briefing list %r is missing, nothing was marked." % spec["name"])
            return
        log("Briefing list", 1)
        types = rule.get("report_types")
        within = rule.get("released_within_hours", 24)
        for entry, type_id in self._content_entries():
            if (types and type_id not in types) or entry["desk"] not in spec["teams"]:
                continue
            if not self._released(entry) or entry.get("hours_ago", 0) > within:
                continue
            item_id = created_ids.get(entry["reference"])
            if not item_id:
                continue
            item = self.api.get_item("archive", str(item_id))
            if str(highlight["_id"]) in [str(mark) for mark in (item or {}).get("highlights") or []]:
                log("%s already on the briefing list" % entry["reference"], 2)
                continue
            try:
                # Posting the same pair twice unmarks it, hence the check above.
                self.api.post("marked_for_highlights", {"highlights": [str(highlight["_id"])], "marked_item": str(item_id)})
                log("added %s to %s" % (entry["reference"], spec["name"]), 2)
            except ApiError as err:
                self.note("Could not add %s to the briefing list: %s" % (entry["reference"], err.status))

    # -- triage -------------------------------------------------------------------------------------

    def section_triage(self):
        """Severity on the native field, the cross-team review queue, and enough work in progress
        for the queue to be worth looking at. Everything here is a create-if-missing or a patch."""
        triage = self.market.get("superdesk.triage") or {}
        if not triage:
            return
        log("Triage")
        relabelled = {self.market.get("severity.native_field") or "urgency", self.severity_scheme}
        self._upsert_vocabularies([v for v in self._vocabularies() if v["_id"] in relabelled])
        self._triage_reports()
        self._triage_existing_reports(triage.get("severity_for_tasking_reports") or {})
        search_id = self._review_queue_search(triage.get("review_queue") or {})
        if search_id and triage.get("workspace"):
            self._triage_workspaces(triage["workspace"], search_id)

    def _triage_reports(self):
        entries = self.market.content("fiction.sample_content.triage_reports")
        if not entries:
            return
        log("Reports waiting in the triage stages", 1)
        for entry in entries:
            if self.api.get_item("archive", self.guid_prefix + entry["reference"]):
                log("report %s already exists" % entry["reference"], 2)
                continue
            self.api.post("archive", self._article(entry, self._default_type(entry)))
            log("created %s in %s / %s" % (entry["reference"], entry["desk"], entry["workflow"]), 2)

    def _triage_existing_reports(self, severity_for):
        """Bring every unreleased report in line: the native field mirrors the severity taxonomy, and
        reports the planning section made from a template get the severity they never had.

        Released reports are left alone. Changing one takes a correction, which would push it to the
        portal a second time.
        """
        log("Severity on reports already on the instance", 1)
        native = self.market.get("severity.native_field") or "urgency"
        scheme = self.severity_scheme
        query = {"query": {"match_all": {}}, "size": 200, "sort": [{"versioncreated": "desc"}]}
        for item in self.api.get("archive", {"source": json.dumps(query)}).get("_items") or []:
            if item.get("state") in ("spiked", "killed", "recalled", "published", "corrected"):
                continue
            reference = item.get("slugline")
            subject = list(item.get("subject") or [])
            severity = next((t.get("qcode") for t in subject if t.get("scheme") == scheme), None)
            updates = {}
            if severity is None and reference in severity_for:
                severity = severity_for[reference]
                subject.extend(self.subject([(scheme, severity)]))
                updates["subject"] = subject
            if severity is None:
                continue
            level = self.severity_urgency[severity]
            for field in (native, "priority"):
                if item.get(field) != level:
                    updates[field] = level
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

    def _review_queue_search(self, spec):
        """One saved search over the review stages of every team.

        `sort` is not part of the saved search model, but the search view replaces the whole URL
        query with `filter.query` when a saved search is opened and the sort bar reads its field from
        there, so it takes effect in Search. Monitoring uses `monitoring.stage.sort` instead.
        """
        if not spec.get("name"):
            return None
        log("Review queue", 1)
        stages = [str(self.stage_id(team, stage)) for team, stage in spec["stages"]]
        doc = {
            "name": spec["name"],
            "description": spec.get("description", ""),
            "is_global": bool(spec.get("global", True)),
            "shortcut": bool(spec.get("shortcut", True)),
            "filter": {
                "query": {
                    # `raw` rather than `q`: both end up in the same query string, but only `q` turns
                    # into a removable chip above the results, and a chip of stage ids helps nobody.
                    "raw": "task.stage:(%s)" % " OR ".join(stages),
                    "repo": "archive",
                    "spike": "exclude",
                    "sort": spec.get("sort", "%s:asc" % (self.market.get("severity.native_field") or "urgency")),
                }
            },
        }
        existing = next((s for s in self.api.find_all("all_saved_searches") if s.get("name") == spec["name"]), None)
        if not existing:
            created = self.api.post("saved_searches", doc)
            log("created the saved search %r" % spec["name"], 2)
            return created["_id"]
        updates = {k: v for k, v in doc.items() if existing.get(k) != v}
        if updates:
            self.api.patch("saved_searches", existing["_id"], updates, etag=existing.get("_etag"))
            log("updated the saved search %r" % spec["name"], 2)
        else:
            log("saved search %r unchanged" % spec["name"], 2)
        return existing["_id"]

    def _triage_workspaces(self, spec, search_id):
        """A custom workspace holding the review queue. Its monitoring groups live in the owner's
        `agg:view` preference rather than on the workspace, and a workspace may only be created by its
        owner, so every listed user gets a session of their own. The account running the seed comes
        first when it is listed."""
        log("Triage workspace", 1)
        usernames = list(spec.get("users") or [])
        if self.api.username in usernames:
            usernames.remove(self.api.username)
            usernames.insert(0, self.api.username)
        for username in usernames:
            try:
                session = self._session(username)
                user_id = session.user_id if session is not self.api else self.api.user_id
                self._triage_workspace(spec["name"], user_id, session, search_id)
            except ApiError as err:
                self.note("Could not build the triage workspace for %s: %s" % (username, err.body[:200]))

    def _triage_workspace(self, name, user_id, session, search_id):
        existing = next((w for w in session.find_all("workspaces") if w.get("name") == name and str(w.get("user")) == str(user_id)), None)
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

    # -- workflow walk ------------------------------------------------------------------------------

    def section_workflow(self):
        """Walk new reports through the stages with the operations the product itself uses, signed in
        as the people who would do it.

        Everything else creates a report straight in the stage it ends up in, which leaves
        `archive_history` with no `move` at all and the workflow export with no stage visit that has
        both ends. This is what puts real workflow on the instance. Progress is read back from the
        instance, so a run cut off halfway carries on where it stopped.
        """
        entries = self._workflow_entries()
        if not entries:
            return
        log("Workflow walk")
        queue = []
        for entry in entries:
            start = self._workflow_pending_from(entry)
            if start is None:
                log("%s already walked, final state %s" % (entry["reference"], entry.get("final", "")), 1)
                continue
            steps = [{"at": entry["at"], "op": "create", "user": entry["author"]}] + entry["steps"]
            for index in range(start, len(steps)):
                queue.append((steps[index]["at"], entry["reference"], index, entry, steps[index]))
        if not queue:
            log("every report has already been walked", 1)
            return

        # One flat schedule rather than one item at a time, so several reports sit in review
        # together and their visits overlap the way a real shift does.
        queue.sort(key=lambda row: (row[0], row[1], row[2]))
        first_at = queue[0][0]
        log("%d operations over about %d seconds (pace %gs)" % (len(queue), round((queue[-1][0] - first_at) * self.pace), self.pace), 1)
        started = time.monotonic()
        for at, _reference, _index, entry, step in queue:
            delay = started + (at - first_at) * self.pace - time.monotonic()
            if delay > 0:
                time.sleep(delay)
            self._workflow_step(entry, step)

        log("Final state", 1)
        for entry in entries:
            log("%-14s %-9s %-8s %s" % (entry["reference"], entry["desk"], entry.get(self.severity_scheme or "severity", ""), entry.get("final", "")), 2)

    def _workflow_entries(self):
        return self.market.content("superdesk.workflow.walk_items") or self.market.content("fiction.sample_content.workflow_walk")

    def _workflow_pending_from(self, entry):
        """Index of the first step still to run, or None when the item is finished. Moves are counted
        from `archive_history`, an edit is recognised by the text it adds, a release by its record."""
        guid = self.guid_prefix + entry["reference"]
        history = self.api.find_all("archive_history", {"item_id": guid}, max_results=200)
        if not history:
            return 0
        if any(record.get("operation") == "publish" for record in history):
            return None
        moves = sum(1 for record in history if record.get("operation") == "move")
        body = (self.api.get_item("archive", guid) or {}).get("body_html") or ""
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
        guid = self.guid_prefix + reference
        try:
            session = self._session(step["user"])
            if step["op"] == "create":
                session.post("archive", self._article(entry, self._default_type(entry)))
                log("%s created by %s in %s / %s" % (reference, step["user"], entry["desk"], entry["workflow"].title()), 1)
            elif step["op"] == "move":
                session.post("archive/%s/move" % guid, {"task": {"desk": str(self.desk_id(step["desk"])), "stage": str(self.stage_id(step["desk"], step["stage"]))}})
                log("%s moved to %s / %s by %s" % (reference, step["desk"], step["stage"], step["user"]), 1)
            elif step["op"] == "edit":
                self._workflow_edit(session, guid, step, reference)
            elif step["op"] == "release":
                if self._release(session, guid, reference):
                    log("%s released by %s" % (reference, step["user"]), 1)
        except ApiError as err:
            self.note("Workflow step %s on %s failed: %s %s" % (step["op"], reference, err.status, err.body[:200]))

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


def _comparable(value):
    if isinstance(value, list):
        return [_comparable(v) for v in value]
    if isinstance(value, dict):
        return {k: _comparable(v) for k, v in value.items() if k != "is_active"}
    return value


# -- command line ---------------------------------------------------------------------------------


def parse_args(argv):
    parser = argparse.ArgumentParser(prog="seed", description="Seed a Superdesk instance from a market contract.")
    parser.add_argument("--market", default=".", help="the market folder (contract.yaml or contract.json, content/)")
    parser.add_argument("--dry-run", action="store_true", help="simulate an empty instance and print every request; nothing is sent")
    parser.add_argument("--only", action="append", choices=SECTIONS + sorted(ALIASES), help="run only this section, repeatable; sections assume earlier ones already ran")
    parser.add_argument("--url", default=os.environ.get("SUPERDESK_URL"), help="instance URL, or SUPERDESK_URL")
    parser.add_argument("--yes", action="store_true", help="do not ask before writing to a live instance")
    parser.add_argument("--verbose", action="store_true", help="also print read requests")
    parser.add_argument("--quiet", action="store_true", help="dry run: do not print the request bodies")
    parser.add_argument("--pace", type=float, help="seconds per unit of the workflow walk schedule (contract default); 0 runs it back to back")
    parser.add_argument("--insecure", action="store_true", help="do not verify the TLS certificate")
    return parser.parse_args(argv)


def demo_password_env(market):
    return market.get("superdesk.demo_password_env") or "DEMO_PASSWORD"


def main(argv=None):
    args = parse_args(sys.argv[1:] if argv is None else argv)
    market = Market(args.market)
    ai_env = market.get("superdesk.ai.provider_key_env") or "AI_PROVIDER_KEY"
    push_env = market.get("superdesk.recipients.portal.push_key_env") or "PORTAL_PUSH_KEY"
    password_env = demo_password_env(market)
    demo_password = os.environ.get(password_env)
    problems = M.check(market)
    for problem in problems:
        log("contract: %s" % problem)
    if problems:
        return 2
    # The portal's settings fall back to the same value, so a demo pair works with neither side set.
    push_key = os.environ.get(push_env) or "%s-dev-push-key" % market.id

    if args.dry_run:
        instance = SimInstance()
        api = Superdesk(args.url or "https://superdesk.invalid", SimTransport(instance, echo=not args.quiet), verbose=args.verbose)
        log("%s seed, dry run: an empty instance is simulated in memory and nothing is sent anywhere." % market.product)
        log("Every write is printed as `> METHOD path body`; secrets print as ***.")
        api.login(os.environ.get("SUPERDESK_USER", "admin"), "dry-run")
        demo_password = demo_password or "<%s>" % password_env
    else:
        if not args.url:
            log("SUPERDESK_URL is not set.")
            return 2
        api = Superdesk(args.url, HttpTransport(insecure=args.insecure), verbose=args.verbose)
        if not args.yes:
            host = urllib.parse.urlsplit(api.base_url).hostname or ""
            answer = input("This writes to %s. Type the host name (%s) to go on: " % (api.base_url, host)) if sys.stdin.isatty() else ""
            if not host or answer.strip() != host:
                log("Not confirmed, nothing sent. Pass --yes when no one can answer the question.")
                return 1
        user = os.environ.get("SUPERDESK_USER", "admin")
        password = os.environ.get("SUPERDESK_PASSWORD")
        if not password:
            if not sys.stdin.isatty():
                log("Set SUPERDESK_PASSWORD.")
                return 2
            password = getpass.getpass("Password for %s: " % user)
        api.login(user, password)
        log("%s seed, signed in to %s as %s" % (market.product, api.base_url, user))
        if not demo_password and sys.stdin.isatty():
            demo_password = getpass.getpass("Password for the demo staff (%s, empty to skip the sections that need it): " % password_env) or None

    seeder = Seeder(
        api,
        market,
        demo_password=demo_password,
        portal_url=os.environ.get("PORTAL_URL"),
        portal_push_url=os.environ.get("PORTAL_PUSH_URL"),
        push_key=push_key,
        ai_key=os.environ.get(ai_env),
        pace=0 if args.dry_run else args.pace,
    )
    wanted = [ALIASES.get(name, name) for name in (args.only or SECTIONS)]
    last = max(SECTIONS.index(name) for name in wanted)
    for section in SECTIONS[: last + 1]:
        if section not in wanted:
            if args.dry_run:
                # The simulated instance starts empty, so the sections before a chosen one run
                # silently first; a live instance already has what they would create.
                api.transport.counting = False
                with contextlib.redirect_stdout(io.StringIO()):
                    getattr(seeder, "section_%s" % section)()
                api.transport.counting = True
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
    log("Done%s." % (" (dry run, nothing was sent)" if args.dry_run else ""))
    if seeder.ai_action_ids and not args.dry_run:
        log("AI action ids:")
        for name, action_id in sorted(seeder.ai_action_ids.items()):
            log("%-16s %s" % (name, action_id), 1)
    if seeder.notes:
        log("Things to look at:")
        for note in seeder.notes:
            log("- %s" % note, 1)
    if args.dry_run:
        log("%d write requests planned%s." % (api.transport.shown, " in the chosen sections" if args.only else ""))
    return 0
