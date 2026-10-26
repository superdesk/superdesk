"""Superdesk documents derived from a market contract.

Only what can be built without an instance lives here: vocabularies, content profiles, roles,
templates, entitlement filters, products, recipients and AI actions. The seed adds the ids.
The branch generator uses the same functions, so the vocabularies a branch ships and the ones
the seed upserts cannot drift apart.
"""

import copy
import re
import sys

# The default editor of a text content profile in superdesk-core
# (superdesk/default_schema.py, DEFAULT_EDITOR on origin/develop). Every one of these that a report
# type does not list is sent as {"enabled": false}: the server merges this default editor into
# every profile save, and a field that is simply left out comes back switched on.
DEFAULT_EDITOR_FIELDS = [
    "slugline",
    "keywords",
    "language",
    "usageterms",
    "genre",
    "anpa_take_key",
    "place",
    "priority",
    "urgency",
    "anpa_category",
    "subject",
    "company_codes",
    "ednote",
    "authors",
    "headline",
    "sms",
    "abstract",
    "byline",
    "dateline",
    "body_html",
    "footer",
    "body_footer",
    "sign_off",
    "feature_media",
    "media_description",
    "attachments",
]


def die(message):
    sys.exit("contract: %s" % message)


# -- vocabularies -------------------------------------------------------------


def taxonomy_vocabulary(spec):
    doc = {
        "_id": spec["id"],
        "display_name": spec["label"],
        "type": "manageable",
        "selection_type": (
            "single selection"
            if spec.get("selection") == "single"
            else "multi selection"
        ),
        "unique_field": "qcode",
        "service": {"all": 1},
    }
    if spec.get("helper_text"):
        doc["helper_text"] = spec["helper_text"]
    doc["init_version"] = spec.get("init_version", 1)
    doc["schema"] = {"name": {}, "qcode": {}}
    doc["items"] = [
        {"is_active": True, "name": item["name"], "qcode": item["qcode"]}
        for item in spec["items"]
    ]
    return doc


def custom_text_vocabulary(spec):
    doc = {
        "_id": spec["id"],
        "display_name": spec["label"],
        "type": "manageable",
        "field_type": "text",
    }
    if spec.get("helper_text"):
        doc["helper_text"] = spec["helper_text"]
    doc["init_version"] = spec.get("init_version", 1)
    doc["items"] = []
    doc["field_options"] = {"single": bool(spec.get("single_line"))}
    return doc


def severity_vocabulary(market, base):
    """The native field (urgency) relabelled and recoloured as severity.

    `base` is the vocabulary as the product ships it. Its schema, translations and type are kept;
    `init_version` goes up by one so `app:initialize_data` applies the change to an existing
    database.
    """
    severity = market.require("severity")
    doc = {}
    for key, value in base.items():
        doc[key] = copy.deepcopy(value)
        if key == "display_name":
            doc["display_name"] = severity.get("label", "Severity")
            if severity.get("helper_text"):
                doc["helper_text"] = severity["helper_text"]
    doc["init_version"] = base.get("init_version", 1) + 1
    doc["items"] = [
        {
            "is_active": True,
            "name": level["name"],
            "short": level["short"],
            "color": level["colour"],
            "qcode": level["urgency"],
        }
        for level in severity["levels"]
    ]
    return doc


def market_vocabularies(market, native_base):
    """Every vocabulary the market adds or changes: the relabelled native field first, as it sits
    earlier in the shipped file, then the taxonomies, then the custom text fields.
    """
    out = []
    if market.get("severity.levels"):
        out.append(severity_vocabulary(market, native_base))
    out.extend(taxonomy_vocabulary(spec) for spec in market.get("vocabularies") or [])
    out.extend(
        custom_text_vocabulary(spec) for spec in market.get("custom_text_fields") or []
    )
    return out


def merged_vocabulary_file(market, base_list):
    """The product's vocabularies.json with the native field replaced and the market's appended."""
    native = market.get("severity.native_field") or "urgency"
    by_id = {doc["_id"]: doc for doc in base_list}
    if native not in by_id:
        die("the base vocabularies have no `%s` to relabel" % native)
    ours = market_vocabularies(market, by_id[native])
    replacing = {doc["_id"]: doc for doc in ours}
    out = [replacing.get(doc["_id"], doc) for doc in base_list]
    present = {doc["_id"] for doc in base_list}
    out.extend(doc for doc in ours if doc["_id"] not in present)
    return out


def vocabulary_names(market):
    """{scheme: {qcode: name}} for every custom taxonomy."""
    return {
        spec["id"]: {item["qcode"]: item["name"] for item in spec["items"]}
        for spec in market.get("vocabularies") or []
    }


def vocabulary_labels(market):
    return {spec["id"]: spec["label"] for spec in market.get("vocabularies") or []}


def severity_urgency(market):
    return {
        level["qcode"]: level["urgency"]
        for level in market.get("severity.levels") or []
    }


def default_urgency(market):
    levels = market.get("severity.levels") or []
    return levels[len(levels) // 2]["urgency"] if levels else 3


# -- report types -----------------------------------------------------------


def report_types(market):
    return market.get("report_types") or []


def report_type(market, type_id):
    for spec in report_types(market):
        if spec["id"] == type_id:
            return spec
    die("unknown report type %r" % type_id)


def report_type_fields(market, spec):
    """The field list of a report type, with `fields_like`, `body_label` and `extra_fields` applied."""
    if spec.get("fields"):
        fields = copy.deepcopy(spec["fields"])
    elif spec.get("fields_like"):
        fields = copy.deepcopy(
            report_type_fields(market, report_type(market, spec["fields_like"]))
        )
    else:
        die("report type %s has no fields" % spec["id"])
    if spec.get("body_label"):
        for field in fields:
            if field["id"] == "body_html":
                field["label"] = spec["body_label"]
    for extra in spec.get("extra_fields") or []:
        extra = dict(extra)
        after = extra.pop("after", None)
        ids = [field["id"] for field in fields]
        position = ids.index(after) + 1 if after in ids else len(fields)
        fields.insert(position, extra)
    return fields


def content_profile(market, spec):
    formats = market.get("editor_formats") or {}
    native = market.get("severity.native_field") or "urgency"
    editor, schema = {}, {}
    for order, field in enumerate(report_type_fields(market, spec), start=1):
        name = field["id"]
        entry = {"order": order, "sdWidth": field.get("width", "full"), "enabled": True}
        if field["kind"] == "native" and "format" in field:
            if field["format"] != "none":
                entry["editor3"] = True
            if name == "body_html":
                entry["cleanPastedHTML"] = False
            entry["formatOptions"] = list(formats.get(field["format"], []))
        if field["kind"] == "taxonomy" and field.get("required"):
            entry["required"] = True
        if field.get("label"):
            entry["field_name"] = field["label"]
        editor[name] = entry

        required = bool(field.get("required"))
        if field["kind"] == "taxonomy":
            schema[name] = {
                "type": "list",
                "required": required,
                "readonly": False,
                "default": [],
            }
        elif field["kind"] == "custom_text":
            schema[name] = {"type": "text", "required": required}
        elif name == native:
            schema[name] = {"type": "integer", "required": required, "nullable": True}
        else:
            schema[name] = {"type": "string", "required": required}
            if field.get("maxlength"):
                schema[name]["maxlength"] = field["maxlength"]
    return {
        "_id": spec["id"],
        "label": spec["label"],
        "description": spec.get("description", ""),
        "priority": spec.get("priority", 0),
        "editor": editor,
        "schema": schema,
    }


def disabled_default_fields(editor):
    return {
        name: {"enabled": False}
        for name in DEFAULT_EDITOR_FIELDS
        if not (editor.get(name) or {}).get("enabled")
    }


def body_headings(skeleton):
    return re.findall(r"<h2>(.*?)</h2>", skeleton or "")


# -- people -------------------------------------------------------------------


def roles(market):
    specs = {role["name"]: role for role in market.get("fiction.roles") or []}

    def privileges(name, seen=()):
        role = specs.get(name) or die("unknown role %r" % name)
        if name in seen:
            die("role %r inherits from itself" % name)
        if role.get("inherits"):
            return privileges(role["inherits"], seen + (name,)) + list(
                role.get("privileges_add") or []
            )
        return list(role.get("privileges") or [])

    out = []
    for name, role in specs.items():
        doc = {
            "name": name,
            "description": role.get("description", ""),
            "privileges": privileges(name),
        }
        for optional in ("author_role", "editor_role"):
            if role.get(optional):
                doc[optional] = role[optional]
        out.append(doc)
    return out


def staff(market):
    return market.get("fiction.staff") or []


def staff_email(market, username):
    pattern = market.get("fiction.staff_email") or "{username}@" + market.require(
        "fiction.firm.email_domain"
    )
    return pattern.format(username=username)


def teams(market):
    return market.require("fiction.teams")


def team(market, name):
    for spec in teams(market):
        if spec["name"] == name:
            return spec
    die("unknown team %r" % name)


def stage_named(market, team_name, workflow):
    """The team's stage whose name matches a content entry's `workflow` value, ignoring case."""
    for stage in team(market, team_name)["stages"]:
        if stage.lower() == str(workflow).lower():
            return stage
    die("team %s has no stage %r" % (team_name, workflow))


# -- templates ----------------------------------------------------------------


def subject_pairs(subject):
    """{scheme: [qcodes]} to [(scheme, qcode)], in the order written."""
    return [
        (scheme, qcode)
        for scheme, qcodes in (subject or {}).items()
        for qcode in qcodes
    ]


def templates(market):
    out = []
    for spec in market.get("templates") or []:
        out.append(_template(market, spec, "create"))
    export = market.get("briefing_list.export_template")
    if export:
        out.append(
            _template(
                market,
                dict(
                    export,
                    teams=export.get("teams") or market.get("briefing_list.teams"),
                ),
                "highlights",
            )
        )
    return out


def _template(market, spec, template_type):
    data = {}
    for key in ("headline", "slugline"):
        if spec.get(key):
            data[key] = spec[key]
    data["body_html"] = report_type(market, spec["report_type"]).get(
        "body_skeleton", ""
    )
    if spec.get("ednote"):
        data["ednote"] = spec["ednote"]
    if spec.get("subject"):
        data["subject"] = subject_pairs(spec["subject"])
    return {
        "template_name": spec["name"],
        "template_type": template_type,
        "profile": spec["report_type"],
        "desks": spec["teams"],
        "data": data,
    }


# -- entitlement and delivery -------------------------------------------------

REPORT_CONDITION = {
    "name": "Item is a report",
    "field": "type",
    "operator": "in",
    "value": "text",
}
CALENDAR_CONDITION = {
    "name": "Item is a calendar entry or request",
    "field": "type",
    "operator": "in",
    "value": "event,planning",
}


def condition_name(market, scheme, qcodes):
    names = vocabulary_names(market).get(scheme) or die(
        "entitlement uses unknown vocabulary %r" % scheme
    )
    label = vocabulary_labels(market)[scheme]
    return "%s is %s" % (
        label,
        " or ".join(
            names.get(q) or die("unknown %s value %r" % (scheme, q)) for q in qcodes
        ),
    )


def entitlement_alternatives(client):
    """[[(scheme, [qcodes])]]: the client is entitled when any alternative matches; an alternative
    matches when every group in it does; a group matches any of its values. `all_of` is one
    alternative, `any_of` a list of `all_of` alternatives.
    """
    entitlement = client.get("entitlement") or {}
    options = [
        entry.get("all_of") or [] for entry in entitlement.get("any_of") or []
    ] or [entitlement.get("all_of") or []]
    return [
        [(scheme, list(qcodes)) for entry in option for scheme, qcodes in entry.items()]
        for option in options
    ]


def entitlement_groups(client):
    return [group for option in entitlement_alternatives(client) for group in option]


def filter_conditions(market):
    """Entitlement conditions grouped by vocabulary, then the two that sort reports from calendar
    entries. Without the type conditions every posted calendar entry would also reach the portal's
    NINJS destination, which pushes a stripped payload for the same guid over the good one.
    """
    by_scheme = {}
    for client in market.get("fiction.clients") or []:
        for scheme, qcodes in entitlement_groups(client):
            conditions = by_scheme.setdefault(scheme, [])
            name = condition_name(market, scheme, qcodes)
            if name not in [c["name"] for c in conditions]:
                conditions.append(
                    {
                        "name": name,
                        "field": scheme,
                        "operator": "in",
                        "value": ",".join(qcodes),
                    }
                )
    out = [condition for conditions in by_scheme.values() for condition in conditions]
    return out + [dict(REPORT_CONDITION), dict(CALENDAR_CONDITION)]


def portal_names(market):
    portal = market.get("superdesk.recipients.portal") or {}
    calendar = market.get("superdesk.recipients.portal_calendar") or {}
    name = (
        portal.get("name")
        or market.get("product.portal_name")
        or "%s Portal" % market.product
    )
    return {
        "recipient": name,
        "product": portal.get("product") or "%s feed" % name,
        "filter": "Portal reports",
        "calendar_recipient": calendar.get("name") or "%s calendar" % name,
        "calendar_product": calendar.get("product") or "%s calendar" % name,
        "calendar_filter": "Portal calendar",
    }


def client_filter_name(client):
    return "%s entitlement" % (client.get("short_name") or client["name"])


def content_filters(market):
    """Conditions inside an expression are AND-ed, expressions in the list are OR-ed."""
    names = portal_names(market)
    out = []
    for client in market.get("fiction.clients") or []:
        expressions = [
            [condition_name(market, scheme, qcodes) for scheme, qcodes in option]
            for option in entitlement_alternatives(client)
        ]
        out.append({"name": client_filter_name(client), "expressions": expressions})
    out.append({"name": names["filter"], "expressions": [[REPORT_CONDITION["name"]]]})
    out.append(
        {
            "name": names["calendar_filter"],
            "expressions": [[CALENDAR_CONDITION["name"]]],
        }
    )
    return out


def entitlement_words(market, client):
    names = vocabulary_names(market)
    options = []
    for option in entitlement_alternatives(client):
        groups = [
            " or ".join(names[scheme][q] for q in qcodes) for scheme, qcodes in option
        ]
        options.append(
            (", and " if any(" or " in group for group in groups) else " and ").join(
                groups
            )
        )
    return "; or ".join(options) + "."


def products(market):
    names = portal_names(market)
    portal = names["recipient"]
    out = [
        {
            "name": names["product"],
            "description": "Every released report, pushed to the %s." % portal,
            "product_type": "both",
            "content_filter": names["filter"],
        },
        {
            "name": names["calendar_product"],
            "description": "Every posted calendar entry and client request, pushed to the %s."
            % portal,
            "product_type": "both",
            "content_filter": names["calendar_filter"],
        },
    ]
    for client in market.get("fiction.clients") or []:
        out.append(
            {
                "name": "%s entitlement" % client["name"],
                "description": entitlement_words(market, client),
                "product_type": "direct",
                "content_filter": client_filter_name(client),
            }
        )
    return out


def calendar_destinations(market):
    destinations = market.get("superdesk.recipients.portal_calendar.destinations") or [
        {"name": "Calendar push", "format": "json_event"},
        {"name": "Requests push", "format": "json_planning"},
    ]
    return [(d["name"], d["format"]) for d in destinations]


def client_emails(client):
    return [user["email"] for user in client.get("users") or []]


# -- checks shared with the Newsroom half ------------------------------------------


def check(market):
    """Problems that would break the Superdesk to portal contract, as messages. The portal's product
    queries read `profile:<portal_profile>`, which the push derives from the content profile's label
    with the spaces removed, and its calendar entitlement reads every entitlement scheme on the event
    itself.
    """
    problems = []
    for spec in report_types(market):
        wanted = spec.get("portal_profile")
        if wanted and spec["label"].replace(" ", "") != wanted:
            problems.append(
                "report type %s: label %r does not strip to portal_profile %r"
                % (spec["id"], spec["label"], wanted)
            )
    allowed = {group["scheme"] for group in market.get("portal.filter_groups") or []}
    for spec in market.get("vocabularies") or []:
        if allowed and spec["id"] not in allowed:
            problems.append(
                "vocabulary %s is not a portal filter group, so the portal drops it from every push"
                % spec["id"]
            )
    schemes = {
        scheme
        for client in market.get("fiction.clients") or []
        for scheme, _ in entitlement_groups(client)
    }
    for event in market.content("fiction.sample_content.calendar_events"):
        missing = sorted(schemes - {pair[0] for pair in event.get("subject") or []})
        if missing:
            problems.append(
                "calendar event %s has no %s, so no client is entitled to it"
                % (event.get("key"), " or ".join(missing))
            )
    return problems


# -- AI -------------------------------------------------------------------------


def ai_actions(market):
    ai = market.get("superdesk.ai") or {}
    voice = (ai.get("voice") or "").strip()
    out = []
    for action in ai.get("actions") or []:
        parameters = {}
        for key in ("temperature", "max_characters", "suggestions_count"):
            if action.get(key) is not None:
                parameters[key] = action[key]
        prompt = (action.get("prompt") or "").strip()
        parameters["system_prompt"] = (voice + " " + prompt).strip()
        doc = {
            "name": action["name"],
            "action_type": action["type"],
            "input_fields": action["input_fields"],
            "output_field": action["output_field"],
            "content_profiles": action.get("report_types")
            or [spec["id"] for spec in report_types(market)],
            "parameters": parameters,
        }
        # Without a model of its own an action runs on the provider's default model, which is the one
        # place an administrator changes it. A model is only set when the contract names one.
        if action.get("model"):
            doc["model"] = action["model"]
        out.append(doc)
    return out
