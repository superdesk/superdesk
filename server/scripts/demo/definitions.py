"""Static Briefdesk demo configuration: roles, users, teams, report types, recipients.

Names and ids here are the shared contract between the Superdesk instance, the portal and the
seeded sample content. Changing one means changing it everywhere.
"""

# Taxonomies are stored once, in server/data/vocabularies.json, and read from there by the
# seeder so the file that ships with the instance and the file the seeder upserts cannot drift.
TAXONOMY_VOCABULARIES = ["severity", "threat_type", "region", "country", "sector", "tlp"]
CUSTOM_FIELD_VOCABULARIES = ["recommended_actions", "location_text", "sources"]
BRIEFDESK_VOCABULARIES = TAXONOMY_VOCABULARIES + CUSTOM_FIELD_VOCABULARIES

DEMO_PASSWORD = "Briefdesk-demo-1"
PUSH_KEY = "briefdesk-demo-push-key"
EMAIL_DOMAIN = "halden.example"

# Privileges an analyst gets. Everything absent is denied, which is how the newsroom-only
# modules (broadcast, rundowns, SAMS, master desk, profiling, dictionaries) stay out of sight.
#
# `ai` runs an action, `ai_studio` is what LISTING /ai_actions requires. The editor glue lists
# the actions before it can run one, so a user without `ai_studio` sees no AI buttons at all.
# The trade-off is real: `ai_studio` is also write access to the stored provider credentials.
ANALYST_PRIVILEGES = [
    "archive",
    "ai",
    "ai_studio",
    "content_templates",
    "dashboard",
    "duplicate",
    "fetch",
    "highlights",
    "highlights_read",
    "mark_for_desks",
    "mark_for_highlights",
    "mark_for_user",
    "monitoring_view",
    "move",
    "personal_template",
    "planning_assignments_desk",
    "planning_assignments_view",
    "planning_planning_management",
    "saved_searches",
    "send_to_personal",
    "spike",
    "spike_read",
    "tasks",
    "unlock",
    "unspike",
    "upload",
]

# A reviewer may release, amend and withdraw. Retract (kill) and takedown stay with the team lead.
REVIEWER_PRIVILEGES = ANALYST_PRIVILEGES + [
    "correct",
    "embargo",
    "publish",
    "publish_queue",
    "resend",
    "unpublish",
    "planning_planning_post",
    "planning_planning_unpost",
]

TEAM_LEAD_PRIVILEGES = REVIEWER_PRIVILEGES + [
    "archived",
    "content_filters",
    "content_type",
    "desks",
    "global_saved_searches",
    "hold",
    "kill",
    "masterdesk",
    "products",
    "restore",
    "roles",
    "subscribers",
    "takedown",
    "users",
    "vocabularies",
    "planning_agenda_management",
    "planning_agenda_delete",
    "planning_manage_content_profiles",
    "planning_planning_featured",
    "planning_planning_spike",
    "planning_planning_unspike",
]

# The watch officer works the sources and the intake board, and never releases.
WATCH_OFFICER_PRIVILEGES = [
    "archive",
    "ai",
    "ai_studio",
    "dashboard",
    "duplicate",
    "fetch",
    "highlights_read",
    "ingest",
    "ingest_providers",
    "mark_for_desks",
    "mark_for_user",
    "monitoring_view",
    "move",
    "routing_rules",
    "rule_sets",
    "saved_searches",
    "spike",
    "spike_read",
    "tasks",
    "unlock",
    "unspike",
]

ROLES = [
    {
        "name": "Analyst",
        "description": "Writes reports. Cannot release.",
        "privileges": ANALYST_PRIVILEGES,
        "author_role": "writer",
    },
    {
        "name": "Reviewer",
        "description": "Reviews and releases reports.",
        "privileges": REVIEWER_PRIVILEGES,
        "author_role": "writer",
        "editor_role": "editor",
    },
    {
        "name": "Team lead",
        "description": "Runs a team and the Briefdesk configuration.",
        "privileges": TEAM_LEAD_PRIVILEGES,
        "author_role": "writer",
        "editor_role": "editor",
    },
    {
        "name": "Watch officer",
        "description": "Monitors sources and triages incoming material.",
        "privileges": WATCH_OFFICER_PRIVILEGES,
    },
]

USERS = [
    {
        "username": "maja.lindqvist",
        "first_name": "Maja",
        "last_name": "Lindqvist",
        "role": "Analyst",
        "desks": ["Europe"],
        "default_desk": "Europe",
        "sign_off": "ml",
        "job_title": "Senior analyst, Europe",
    },
    {
        "username": "tomas.havel",
        "first_name": "Tomas",
        "last_name": "Havel",
        "role": "Reviewer",
        "desks": ["Europe"],
        "default_desk": "Europe",
        "sign_off": "th",
        "job_title": "Reviewer, Europe",
    },
    {
        "username": "dana.reyes",
        "first_name": "Dana",
        "last_name": "Reyes",
        "role": "Watch officer",
        "desks": ["Watch"],
        "default_desk": "Watch",
        "sign_off": "dr",
        "job_title": "Watch officer",
    },
    {
        "username": "omar.nasser",
        "first_name": "Omar",
        "last_name": "Nasser",
        "role": "Analyst",
        "desks": ["MENA"],
        "default_desk": "MENA",
        "sign_off": "on",
        "job_title": "Senior analyst, MENA",
    },
    {
        "username": "lucia.ferro",
        "first_name": "Lucia",
        "last_name": "Ferro",
        "role": "Team lead",
        "desks": ["Watch", "Europe", "MENA", "Americas"],
        "default_desk": "Europe",
        "sign_off": "lf",
        "job_title": "Head of intelligence",
    },
]

REGIONAL_STAGES = ["Incoming", "Analysis", "Review", "Released"]

DESKS = [
    {
        "name": "Watch",
        "description": "24/7 intake and triage of source material.",
        "source": "WATCH",
        "stages": ["Incoming", "Triage"],
        "default_profile": "alert",
        "default_template": "Alert intake",
    },
    {
        "name": "Europe",
        "description": "Europe reporting team.",
        "source": "EUR",
        "stages": REGIONAL_STAGES,
        "default_profile": "alert",
        "default_template": "Alert - Europe",
    },
    {
        "name": "MENA",
        "description": "Middle East and North Africa reporting team.",
        "source": "MENA",
        "stages": REGIONAL_STAGES,
        "default_profile": "alert",
        "default_template": "Alert - MENA",
    },
    {
        "name": "Americas",
        "description": "Americas reporting team.",
        "source": "AMER",
        "stages": REGIONAL_STAGES,
        "default_profile": "alert",
        "default_template": "Alert - Americas",
    },
]

# Rich text controls offered on an assessment body. Names come from
# getEditor3RichTextFormattingOptions() in superdesk-client-core.
BODY_FORMAT_OPTIONS = [
    "h2",
    "h3",
    "bold",
    "italic",
    "underline",
    "quote",
    "unordered list",
    "ordered list",
    "table",
    "link",
    "annotation",
    "comments",
    "suggestions",
    "remove format",
]

SUMMARY_FORMAT_OPTIONS = ["bold", "italic", "underline", "link", "comments", "suggestions"]


def _editor(order, width="full", **extra):
    field = {"order": order, "sdWidth": width, "enabled": True}
    field.update(extra)
    return field


ALERT_EDITOR = {
    "headline": _editor(1, formatOptions=[], field_name="Title"),
    "slugline": _editor(2, "half", field_name="Reference"),
    "tlp": _editor(3, "half"),
    "severity": _editor(4, "half", required=True),
    "region": _editor(5, "half", required=True),
    "country": _editor(6, "half"),
    "sector": _editor(7, "half"),
    "threat_type": _editor(8, "half"),
    "location_text": _editor(9, "half"),
    "abstract": _editor(10, editor3=True, formatOptions=SUMMARY_FORMAT_OPTIONS, field_name="Summary"),
    "body_html": _editor(
        11,
        editor3=True,
        cleanPastedHTML=False,
        formatOptions=BODY_FORMAT_OPTIONS,
        field_name="Assessment",
    ),
    "recommended_actions": _editor(12),
    "sources": _editor(13),
    "byline": _editor(14, "half", field_name="Analyst"),
    "ednote": _editor(15, field_name="Handling note"),
}

ALERT_SCHEMA = {
    "headline": {"type": "string", "required": True, "maxlength": 120},
    "slugline": {"type": "string", "required": True, "maxlength": 30},
    "tlp": {"type": "list", "required": False, "readonly": False, "default": []},
    "severity": {"type": "list", "required": True, "readonly": False, "default": []},
    "region": {"type": "list", "required": True, "readonly": False, "default": []},
    "country": {"type": "list", "required": False, "readonly": False, "default": []},
    "sector": {"type": "list", "required": False, "readonly": False, "default": []},
    "threat_type": {"type": "list", "required": False, "readonly": False, "default": []},
    "location_text": {"type": "text", "required": False},
    "abstract": {"type": "string", "required": True, "maxlength": 400},
    "body_html": {"type": "string", "required": True},
    "recommended_actions": {"type": "text", "required": False},
    "sources": {"type": "text", "required": False},
    "byline": {"type": "string", "required": False},
    "ednote": {"type": "string", "required": False},
}


def _brief_editor(body_label):
    return {
        "headline": _editor(1, formatOptions=[], field_name="Title"),
        "slugline": _editor(2, "half", field_name="Reference"),
        "tlp": _editor(3, "half"),
        "region": _editor(4, "half", required=True),
        "country": _editor(5, "half"),
        "sector": _editor(6, "half"),
        "threat_type": _editor(7, "half"),
        "abstract": _editor(8, editor3=True, formatOptions=SUMMARY_FORMAT_OPTIONS, field_name="Summary"),
        "body_html": _editor(
            9,
            editor3=True,
            cleanPastedHTML=False,
            formatOptions=BODY_FORMAT_OPTIONS,
            field_name=body_label,
        ),
        "sources": _editor(10),
        "byline": _editor(11, "half", field_name="Analyst"),
        "ednote": _editor(12, field_name="Handling note"),
    }


def _brief_schema(headline_max=120):
    return {
        "headline": {"type": "string", "required": True, "maxlength": headline_max},
        "slugline": {"type": "string", "required": True, "maxlength": 30},
        "tlp": {"type": "list", "required": False, "readonly": False, "default": []},
        "region": {"type": "list", "required": True, "readonly": False, "default": []},
        "country": {"type": "list", "required": False, "readonly": False, "default": []},
        "sector": {"type": "list", "required": False, "readonly": False, "default": []},
        "threat_type": {"type": "list", "required": False, "readonly": False, "default": []},
        "abstract": {"type": "string", "required": True, "maxlength": 400},
        "body_html": {"type": "string", "required": True},
        "sources": {"type": "text", "required": False},
        "byline": {"type": "string", "required": False},
        "ednote": {"type": "string", "required": False},
    }


RFI_EDITOR = _brief_editor("Response")
RFI_EDITOR["severity"] = _editor(7, "half")
RFI_SCHEMA = _brief_schema()
RFI_SCHEMA["severity"] = {"type": "list", "required": False, "readonly": False, "default": []}

CONTENT_PROFILES = [
    {
        "_id": "alert",
        "label": "Alert",
        "description": "A single situation, what it means and what to do about it.",
        "priority": 40,
        "editor": ALERT_EDITOR,
        "schema": ALERT_SCHEMA,
    },
    {
        "_id": "daily_brief",
        "label": "Daily Brief",
        "description": "The day's picture for one region.",
        "priority": 30,
        "editor": _brief_editor("Brief"),
        "schema": _brief_schema(),
    },
    {
        "_id": "country_assessment",
        "label": "Country Assessment",
        "description": "Standing assessment of the operating environment in one country.",
        "priority": 20,
        "editor": _brief_editor("Assessment"),
        "schema": _brief_schema(),
    },
    {
        "_id": "rfi_response",
        "label": "RFI Response",
        "description": "Answer to a client request for information.",
        "priority": 10,
        "editor": RFI_EDITOR,
        "schema": RFI_SCHEMA,
    },
]

ALERT_BODY_SKELETON = (
    "<h2>Situation</h2><p>What happened, where and when. Facts only.</p>"
    "<h2>Assessment</h2><p>What it means for clients in scope, and how confident we are.</p>"
    "<h2>Outlook</h2><p>What to expect over the next 24 to 72 hours.</p>"
)

BRIEF_BODY_SKELETON = (
    "<h2>Headlines</h2><ul><li></li><li></li><li></li></ul>"
    "<h2>What changed</h2><p></p>"
    "<h2>Watch list</h2><ul><li></li></ul>"
)

ASSESSMENT_BODY_SKELETON = (
    "<h2>Operating environment</h2><p></p>"
    "<h2>Threat picture</h2><p></p>"
    "<h2>Outlook, next 90 days</h2><p></p>"
    "<h2>Implications for operations</h2><p></p>"
)

RFI_BODY_SKELETON = (
    "<h2>The question</h2><p></p>"
    "<h2>Answer</h2><p></p>"
    "<h2>Confidence and gaps</h2><p></p>"
)

TEMPLATES = [
    {
        "template_name": "Alert intake",
        "profile": "alert",
        "desks": ["Watch"],
        "data": {"body_html": ALERT_BODY_SKELETON, "ednote": "Raised from a source item. Triage before assigning."},
    },
    {
        "template_name": "Alert - Europe",
        "profile": "alert",
        "desks": ["Europe"],
        "data": {"body_html": ALERT_BODY_SKELETON, "subject": [("region", "europe")]},
    },
    {
        "template_name": "Alert - MENA",
        "profile": "alert",
        "desks": ["MENA"],
        "data": {"body_html": ALERT_BODY_SKELETON, "subject": [("region", "mena")]},
    },
    {
        "template_name": "Alert - Americas",
        "profile": "alert",
        "desks": ["Americas"],
        "data": {"body_html": ALERT_BODY_SKELETON, "subject": [("region", "americas")]},
    },
    {
        "template_name": "Daily Brief - Europe",
        "profile": "daily_brief",
        "desks": ["Europe"],
        "data": {
            "body_html": BRIEF_BODY_SKELETON,
            "slugline": "EU-BRIEF",
            "subject": [("region", "europe"), ("tlp", "amber")],
        },
    },
    {
        "template_name": "Daily Brief - MENA",
        "profile": "daily_brief",
        "desks": ["MENA"],
        "data": {
            "body_html": BRIEF_BODY_SKELETON,
            "slugline": "ME-BRIEF",
            "subject": [("region", "mena"), ("tlp", "amber")],
        },
    },
    {
        "template_name": "Country Assessment",
        "profile": "country_assessment",
        "desks": ["Europe", "MENA", "Americas"],
        "data": {"body_html": ASSESSMENT_BODY_SKELETON, "subject": [("tlp", "amber")]},
    },
    {
        "template_name": "RFI Response",
        "profile": "rfi_response",
        "desks": ["Europe", "MENA", "Americas"],
        "data": {
            "body_html": RFI_BODY_SKELETON,
            "ednote": "Name the client and the request reference in the handling note.",
            "subject": [("tlp", "amber")],
        },
    },
]

HIGHLIGHT_TEMPLATE = {
    "template_name": "Europe daily brief export",
    "template_type": "highlights",
    "profile": "daily_brief",
    "desks": ["Europe"],
    "data": {
        "headline": "Europe daily brief",
        "slugline": "EU-BRIEF",
        "body_html": BRIEF_BODY_SKELETON,
        "subject": [("region", "europe"), ("tlp", "amber")],
    },
}

HIGHLIGHT = {
    "name": "Europe daily brief",
    "desks": ["Europe"],
    "template": "Europe daily brief export",
    "auto_insert": "now-24h",
    "groups": ["Europe"],
}

INGEST_PROVIDERS = [
    {
        "name": "GDACS disaster alerts",
        "source": "GDACS",
        "url": "https://www.gdacs.org/xml/rss.xml",
    },
    {
        "name": "USGS significant earthquakes",
        "source": "USGS",
        "url": "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.atom",
    },
    {
        "name": "ReliefWeb updates",
        "source": "ReliefWeb",
        "url": "https://reliefweb.int/updates/rss.xml",
    },
]

ROUTING_SCHEME_NAME = "Watch intake"

# field is the vocabulary _id, which is also the scheme the values carry in subject.
FILTER_CONDITIONS = [
    {"name": "Region is Europe", "field": "region", "operator": "in", "value": "europe"},
    {"name": "Region is Europe or MENA", "field": "region", "operator": "in", "value": "europe,mena"},
    {"name": "Region is MENA", "field": "region", "operator": "in", "value": "mena"},
    {"name": "Sector is logistics", "field": "sector", "operator": "in", "value": "logistics"},
    {"name": "Sector is pharmaceuticals", "field": "sector", "operator": "in", "value": "pharma"},
    {"name": "Sector is energy", "field": "sector", "operator": "in", "value": "energy"},
    # `type` separates the three kinds of document the portal receives. Without it every posted
    # calendar entry would also reach the Newsroom NINJS destination, which pushes a stripped
    # payload for the same guid and overwrites the good one.
    {"name": "Item is a report", "field": "type", "operator": "in", "value": "text"},
    {"name": "Item is a calendar entry or request", "field": "type", "operator": "in", "value": "event,planning"},
]

# Conditions inside one expression are AND-ed, expressions in the list are OR-ed.
CONTENT_FILTERS = [
    {
        "name": "Nordfreight entitlement",
        "expressions": [["Region is Europe", "Sector is logistics"]],
    },
    {
        "name": "Aurelia Pharma entitlement",
        "expressions": [["Region is Europe or MENA", "Sector is pharmaceuticals"]],
    },
    {
        "name": "Castellan entitlement",
        "expressions": [["Region is MENA", "Sector is energy"]],
    },
    {
        "name": "Portal reports",
        "expressions": [["Item is a report"]],
    },
    {
        "name": "Portal risk calendar",
        "expressions": [["Item is a calendar entry or request"]],
    },
]

PRODUCTS = [
    {
        "name": "Briefdesk Portal feed",
        "description": "Every released report, pushed to the Briefdesk Portal.",
        "product_type": "both",
        "content_filter": "Portal reports",
    },
    {
        "name": "Briefdesk Portal risk calendar",
        "description": "Every posted calendar entry and client request, pushed to the Briefdesk Portal.",
        "product_type": "both",
        "content_filter": "Portal risk calendar",
    },
    {
        "name": "Nordfreight Logistics entitlement",
        "description": "Europe and logistics.",
        "product_type": "direct",
        "content_filter": "Nordfreight entitlement",
    },
    {
        "name": "Aurelia Pharma entitlement",
        "description": "Europe or MENA, and pharmaceuticals.",
        "product_type": "direct",
        "content_filter": "Aurelia Pharma entitlement",
    },
    {
        "name": "Castellan Energy entitlement",
        "description": "MENA and energy.",
        "product_type": "direct",
        "content_filter": "Castellan entitlement",
    },
]

CLIENT_COMPANIES = [
    {
        "name": "Nordfreight Logistics",
        "product": "Nordfreight Logistics entitlement",
        "emails": ["erik.dahl@nordfreight.example", "ines.morel@nordfreight.example"],
    },
    {
        "name": "Aurelia Pharma",
        "product": "Aurelia Pharma entitlement",
        "emails": ["hanna.weiss@aureliapharma.example"],
    },
    {
        "name": "Castellan Energy",
        "product": "Castellan Energy entitlement",
        "emails": ["karim.saleh@castellan.example"],
    },
]

PORTAL_SUBSCRIBER_NAME = "Briefdesk Portal"

# A second recipient for the calendar. Superdesk applies a subscriber's products once and then
# hands the item to every destination that recipient has, so the only way to keep the Newsroom
# NINJS destination away from calendar entries is to put them on a recipient of their own.
PORTAL_CALENDAR_SUBSCRIBER_NAME = "Briefdesk Portal calendar"
PORTAL_CALENDAR_PRODUCT = "Briefdesk Portal risk calendar"
PORTAL_CALENDAR_DESTINATIONS = [
    ("Risk calendar push", "json_event"),
    ("Client requests push", "json_planning"),
]

AI_PROVIDER_NAME = "OpenRouter"
AI_DEFAULT_MODEL = "z-ai/glm-5.3-flash"

ANALYST_VOICE = (
    "You write for Halden Risk Intelligence, a security and risk intelligence firm whose clients "
    "are corporate security and operations managers. Write in neutral, factual British English. "
    "Lead with what happened and where, then the impact on people, sites and movement, then the "
    "recommended posture. Never speculate, never use adjectives that dramatise, never invent "
    "detail that is not in the input. If the input does not support a claim, leave it out. "
    "No emoji, no exclamation marks, no marketing language."
)

AI_ACTIONS = [
    {
        "name": "Suggest titles",
        "action_type": "suggestion",
        "input_fields": ["body_html", "abstract"],
        "output_field": "headline",
        "content_profiles": ["alert", "daily_brief", "country_assessment", "rfi_response"],
        "parameters": {
            "temperature": 0.3,
            "max_characters": 110,
            "suggestions_count": 3,
            "system_prompt": ANALYST_VOICE
            + " Propose report titles. A title names the situation, the place and the effect, in "
            "that order, with no verb tense games and no question marks.",
        },
    },
    {
        "name": "Draft summary",
        "action_type": "summary",
        "input_fields": ["body_html"],
        "output_field": "abstract",
        "content_profiles": ["alert", "daily_brief", "country_assessment", "rfi_response"],
        "parameters": {
            "temperature": 0.2,
            "max_characters": 400,
            "system_prompt": ANALYST_VOICE
            + " Write the summary that sits at the top of the report: two or three sentences "
            "covering what happened and where, the impact on client operations, and the "
            "recommended posture. No headings, no bullet points, no closing flourish.",
        },
    },
]

PROGRAMMES = ["Nordfreight Logistics", "Aurelia Pharma", "Castellan Energy"]

# Replaces the stock Sport / Finance / Entertainment items of the `event_calendars` vocabulary.
# (qcode, name); an event carries a copy of the item, not a reference.
EVENT_CALENDARS = [
    ("political", "Political"),
    ("labour", "Labour"),
    ("legal", "Legal"),
    ("trade", "Trade and industry"),
    ("security", "Security"),
]

# Copies of `eventoccurstatus` vocabulary items, keyed by a short name used in EVENTS below.
OCCUR_STATUS = {
    "certain": {"qcode": "eocstat:eos5", "name": "Planned, occurs certainly"},
    "likely": {"qcode": "eocstat:eos4", "name": "Planned, occurence highly likely"},
    "possible": {"qcode": "eocstat:eos3", "name": "Planned, May occur"},
}

# The risk calendar. `days` is relative to the day the seed runs, so the demo is always current;
# negative values are last week. `hours` is how long the entry lasts. `repeat` turns the entry into
# a recurring series: the weekday comes from the computed start date, so only `frequency`, `count`
# and an optional `interval` are given here. `key` is the slugline and the stable lookup key.
EVENTS = [
    {
        "key": "EV-DE-RAIL-BALLOT",
        "name": "Rail freight union announces strike ballot result, Germany",
        "summary": "National rail freight union publishes the outcome of its strike ballot on the 2027 pay round.",
        "detail": (
            "The union has said it will announce the ballot outcome at a press conference in Berlin. A mandate "
            "would allow warning strikes from the following week, with intermodal terminals affected first."
        ),
        "internal_note": "If the mandate passes, Europe raises an alert the same afternoon.",
        "calendar": "labour",
        "occur_status": "certain",
        "days": -5,
        "hour": 10,
        "hours": 2,
        "tz": "Europe/Berlin",
        "location": {"name": "Union federal office", "city": "Berlin", "country": "Germany",
                     "lat": 52.5200, "lon": 13.4050},
        "subject": [("region", "europe"), ("country", "de"), ("threat_type", "industrial_action"),
                    ("sector", "logistics")],
    },
    {
        "key": "EV-EG-FUEL-REVIEW",
        "name": "Quarterly fuel price review announcement, Egypt",
        "summary": "Scheduled quarterly review of regulated fuel prices, announced by the pricing committee.",
        "detail": (
            "Previous reviews that raised pump prices were followed within days by small, short-lived protests "
            "in Cairo and the Delta governorates, and by higher haulage rates on the Suez corridor."
        ),
        "internal_note": "Castellan Energy asked to be told the same day. Watch keeps the protest tracker open.",
        "calendar": "political",
        "occur_status": "certain",
        "days": -3,
        "hour": 12,
        "hours": 1,
        "tz": "Africa/Cairo",
        "location": {"name": "Pricing committee briefing room", "city": "Cairo", "country": "Egypt",
                     "lat": 30.0444, "lon": 31.2357},
        "subject": [("region", "mena"), ("country", "eg"), ("threat_type", "political"), ("sector", "energy")],
    },
    {
        "key": "EV-MX-SECURITY-MEETING",
        "post": False,
        "name": "Federal and state cargo security coordination meeting, Mexico",
        "summary": "Federal transport ministry meets state authorities on highway cargo crime, Mexico City.",
        "detail": (
            "The meeting is expected to set the escort and convoy rules that apply to the Mexico City to "
            "Veracruz corridor for the rest of the year."
        ),
        "internal_note": "Outcome feeds the Americas convoy review. No public readout is guaranteed.",
        "calendar": "security",
        "occur_status": "certain",
        "days": -6,
        "hour": 15,
        "hours": 4,
        "tz": "America/Mexico_City",
        "location": {"name": "Transport ministry", "city": "Mexico City", "country": "Mexico",
                     "lat": 19.4326, "lon": -99.1332},
        "subject": [("region", "americas"), ("country", "mx"), ("threat_type", "crime"), ("sector", "logistics")],
    },
    {
        "key": "EV-PL-GDANSK-STRIKE",
        "name": "Warning strike at Gdansk container terminal",
        "summary": "Terminal branch of the dockers union has notified a 24 hour warning strike over shift rosters.",
        "detail": (
            "The notice covers quay and yard operations at the deepwater terminal. Gate operations are not "
            "named in the notice, so pre-gated boxes may still move. Feeder calls are the first to slip."
        ),
        "internal_note": "Nordfreight has three inbound calls that week. Confirm the gate position before we publish.",
        "calendar": "labour",
        "occur_status": "likely",
        "days": 4,
        "hour": 6,
        "hours": 24,
        "tz": "Europe/Warsaw",
        "location": {"name": "Deepwater container terminal", "city": "Gdansk", "country": "Poland",
                     "lat": 54.3960, "lon": 18.6880},
        "subject": [("region", "europe"), ("country", "pl"), ("threat_type", "industrial_action"),
                    ("sector", "logistics")],
    },
    {
        "key": "EV-GB-LONDON-DEMO",
        "name": "Announced demonstration, central London",
        "summary": "Organisers have notified a march from Embankment to Parliament Square on Saturday afternoon.",
        "detail": (
            "Police have published a rolling road closure plan. Counter-protest is advertised on the same route, "
            "which is the usual trigger for containment and for late changes to the closures."
        ),
        "internal_note": "We covered the last one in BD-EU-412. Reuse the closure map, check the times again.",
        "calendar": "security",
        "occur_status": "certain",
        "days": 5,
        "hour": 12,
        "hours": 6,
        "tz": "Europe/London",
        "location": {"name": "Embankment to Parliament Square", "city": "London", "country": "United Kingdom",
                     "lat": 51.5010, "lon": -0.1246},
        "subject": [("region", "europe"), ("country", "gb"), ("threat_type", "civil_unrest"),
                    ("sector", "retail")],
    },
    {
        "key": "EV-FR-REST-RULING",
        "name": "Court of appeal ruling on haulier rest period rules, France",
        "summary": "Appeal ruling on whether cross-border drivers may take reduced rest at unstaffed sites.",
        "detail": (
            "A ruling against the operators would force overnight stops at staffed facilities and add roughly "
            "half a day to Benelux to Iberia runs. Both sides have said they would appeal further."
        ),
        "internal_note": "Nordfreight legal want the operational reading, not the legal one. Keep it to a page.",
        "calendar": "legal",
        "occur_status": "certain",
        "days": 7,
        "hour": 9,
        "hours": 3,
        "tz": "Europe/Paris",
        "location": {"name": "Court of appeal", "city": "Paris", "country": "France",
                     "lat": 48.8556, "lon": 2.3452},
        "subject": [("region", "europe"), ("country", "fr"), ("threat_type", "political"),
                    ("sector", "logistics"), ("sector", "pharma")],
    },
    {
        "key": "EV-ES-PHARMA-FAIR",
        "name": "Iberian pharmaceutical logistics fair, Barcelona",
        "summary": "Three day trade fair drawing cold chain operators and their carriers to the Gran Via site.",
        "detail": (
            "Fairs of this size in the city have drawn organised theft against van loads in the surrounding "
            "industrial estates, and hotel districts see a rise in room and vehicle break-ins."
        ),
        "internal_note": "Aurelia Pharma is sending a delegation. They will want a travel annex.",
        "calendar": "trade",
        "occur_status": "certain",
        "days": 9,
        "hour": 8,
        "hours": 10,
        "tz": "Europe/Madrid",
        "location": {"name": "Gran Via exhibition centre", "city": "Barcelona", "country": "Spain",
                     "lat": 41.3540, "lon": 2.1280},
        "subject": [("region", "europe"), ("country", "es"), ("threat_type", "crime"), ("sector", "pharma")],
    },
    {
        "key": "EV-CZ-LOCAL-VOTE",
        "name": "Municipal elections, Czechia",
        "summary": "Nationwide municipal elections, with results expected the following morning.",
        "detail": (
            "Campaign rallies in Prague and Brno have drawn counter-demonstrations. City centre access on "
            "polling day is normally unaffected, the risk sits in the two evenings on either side."
        ),
        "internal_note": "Short read, one page. Do not attempt a political forecast.",
        "calendar": "political",
        "occur_status": "certain",
        "days": 11,
        "hour": 7,
        "hours": 15,
        "tz": "Europe/Prague",
        "location": {"name": "Polling stations nationwide", "city": "Prague", "country": "Czechia",
                     "lat": 50.0755, "lon": 14.4378},
        "subject": [("region", "europe"), ("country", "cz"), ("threat_type", "political"),
                    ("sector", "retail")],
    },
    {
        "key": "EV-BR-CUP-FINAL",
        "name": "State cup final, Sao Paulo",
        "summary": "Sold out state cup final with a fan march announced from the metro station to the stadium.",
        "detail": (
            "Both supporter groups have a history of clashes on the approach roads. The city normally closes "
            "the stadium ring three hours before kick-off and reopens it late."
        ),
        "internal_note": "Crowd risk only. No commentary on the match, and no club names in the report.",
        "calendar": "security",
        "occur_status": "certain",
        "days": 13,
        "hour": 21,
        "hours": 4,
        "tz": "America/Sao_Paulo",
        "location": {"name": "Municipal stadium", "city": "Sao Paulo", "country": "Brazil",
                     "lat": -23.5450, "lon": -46.4740},
        "subject": [("region", "americas"), ("country", "br"), ("threat_type", "civil_unrest"),
                    ("sector", "retail")],
    },
    {
        "key": "EV-AE-ENERGY-SUMMIT",
        "name": "Gulf energy security summit, Abu Dhabi",
        "summary": "Two day ministerial summit on regional energy infrastructure protection.",
        "detail": (
            "Venue and hotel districts run a closed traffic plan for the duration. Previous editions saw "
            "credential phishing aimed at delegates in the week before the opening session."
        ),
        "internal_note": "Castellan Energy is attending. Pair the physical annex with the phishing warning.",
        "calendar": "trade",
        "occur_status": "certain",
        "days": 14,
        "hour": 9,
        "hours": 9,
        "tz": "Asia/Dubai",
        "location": {"name": "National exhibition centre", "city": "Abu Dhabi", "country": "United Arab Emirates",
                     "lat": 24.4180, "lon": 54.4570},
        "subject": [("region", "mena"), ("country", "ae"), ("threat_type", "cyber"), ("sector", "energy")],
    },
    {
        "key": "EV-NL-FILING-DEADLINE",
        "name": "Pre-arrival filing rule takes effect, Netherlands",
        "summary": "Customs deadline after which short-form pre-arrival declarations are refused.",
        "detail": (
            "Consignments filed on the old form after the cut-off are held for manual clearance. The first "
            "week of similar changes has always produced a backlog at the Maasvlakte terminals."
        ),
        "internal_note": "Nordfreight need the date and the practical consequence, nothing more.",
        "calendar": "legal",
        "occur_status": "certain",
        "days": 16,
        "hour": 0,
        "hours": 24,
        "tz": "Europe/Amsterdam",
        "location": {"name": "Maasvlakte terminals", "city": "Rotterdam", "country": "Netherlands",
                     "lat": 51.9500, "lon": 4.0500},
        "subject": [("region", "europe"), ("country", "nl"), ("threat_type", "transport"),
                    ("sector", "logistics"), ("sector", "pharma")],
    },
    {
        "key": "EV-IT-PORT-REFERENDUM",
        "name": "Local referendum on port expansion, Genoa",
        "summary": "Binding local referendum on the terminal expansion plan, with campaign rallies at the gates.",
        "detail": (
            "Port access roads have been blocked twice during the campaign. A vote against the plan would "
            "most likely be followed by a celebratory blockade rather than by an immediate policy change."
        ),
        "internal_note": "Keep the wording neutral on the politics. The client question is gate access.",
        "calendar": "political",
        "occur_status": "certain",
        "days": 21,
        "hour": 7,
        "hours": 14,
        "tz": "Europe/Rome",
        "location": {"name": "Port district polling stations", "city": "Genoa", "country": "Italy",
                     "lat": 44.4056, "lon": 8.9463},
        "subject": [("region", "europe"), ("country", "it"), ("threat_type", "civil_unrest"),
                    ("sector", "logistics")],
    },
    {
        "key": "EV-SA-VISA-DEADLINE",
        "name": "Contractor work permit registration deadline, Saudi Arabia",
        "summary": "Last day for contractors to register staff under the revised work permit categories.",
        "detail": (
            "Unregistered staff lose site access from the following morning. Registration portals have been "
            "slow in the final days of previous rounds."
        ),
        "internal_note": "We flagged the rule change in BD-ME-207. This is the operational deadline note.",
        "calendar": "legal",
        "occur_status": "certain",
        "days": 26,
        "hour": 0,
        "hours": 24,
        "tz": "Asia/Riyadh",
        "location": {"name": "Labour ministry portal", "city": "Riyadh", "country": "Saudi Arabia",
                     "lat": 24.7136, "lon": 46.6753},
        "subject": [("region", "mena"), ("country", "sa"), ("threat_type", "political"),
                    ("sector", "energy"), ("sector", "pharma")],
    },
    {
        "key": "EV-EG-PORT-CONCESSION",
        "name": "Administrative court ruling on the Alexandria port concession",
        "summary": "Ruling on the challenge to the container and bulk terminal concession at Alexandria.",
        "detail": (
            "A ruling against the concession would put terminal operations under interim management while "
            "the tender is rerun. Fuel and chemical berths sit inside the same concession area."
        ),
        "internal_note": "Castellan and Nordfreight both asked about this one. Keep the two reads separate.",
        "calendar": "legal",
        "occur_status": "likely",
        "days": 19,
        "hour": 10,
        "hours": 3,
        "tz": "Africa/Cairo",
        "location": {"name": "Administrative court", "city": "Alexandria", "country": "Egypt",
                     "lat": 31.2001, "lon": 29.9187},
        "subject": [("region", "mena"), ("country", "eg"), ("threat_type", "political"),
                    ("sector", "energy"), ("sector", "logistics")],
    },
    {
        "key": "EV-MX-STATE-ELECTION",
        "name": "State gubernatorial election, Veracruz",
        "summary": "State election with a closed campaign period and a dry law over the polling weekend.",
        "detail": (
            "Road blockades by candidates' supporters are common on the day after the count. The port road "
            "was blocked for six hours at the last state election."
        ),
        "internal_note": "Americas leads. Coordinate the corridor annex with the convoy review.",
        "calendar": "political",
        "occur_status": "certain",
        "days": 33,
        "hour": 8,
        "hours": 12,
        "tz": "America/Mexico_City",
        "location": {"name": "State polling stations", "city": "Xalapa", "country": "Mexico",
                     "lat": 19.5438, "lon": -96.9102},
        "subject": [("region", "americas"), ("country", "mx"), ("threat_type", "political"),
                    ("sector", "logistics")],
    },
    {
        "key": "EV-NL-PORT-TALKS",
        "name": "Rotterdam port labour negotiation round",
        "summary": "Weekly negotiation round between the terminal operators and the dockers union.",
        "detail": (
            "Each round ends with a short statement. A breakdown is the trigger for an overtime ban, which is "
            "how the last dispute started."
        ),
        "internal_note": "Standing tasking: Europe files a two line note after every round, alert only on a breakdown.",
        "calendar": "labour",
        "occur_status": "likely",
        "days": 2,
        "hour": 9,
        "hours": 4,
        "tz": "Europe/Amsterdam",
        "repeat": {"frequency": "WEEKLY", "count": 5},
        "location": {"name": "Port authority building", "city": "Rotterdam", "country": "Netherlands",
                     "lat": 51.9050, "lon": 4.4850},
        "subject": [("region", "europe"), ("country", "nl"), ("threat_type", "industrial_action"),
                    ("sector", "logistics")],
    },
    {
        "key": "EV-MX-CONVOY-REVIEW",
        "post": False,
        "name": "Veracruz corridor convoy security review",
        "summary": "Weekly review of escorted convoy timings and incident reports on the Mexico City corridor.",
        "detail": (
            "Carriers, insurers and the state police compare the week's incidents and agree the departure "
            "windows for the following week."
        ),
        "internal_note": "Standing tasking: Americas files the corridor note the same evening.",
        "calendar": "security",
        "occur_status": "likely",
        "days": 3,
        "hour": 16,
        "hours": 2,
        "tz": "America/Mexico_City",
        "repeat": {"frequency": "WEEKLY", "count": 4},
        "location": {"name": "State police headquarters", "city": "Veracruz", "country": "Mexico",
                     "lat": 19.1738, "lon": -96.1342},
        "subject": [("region", "americas"), ("country", "mx"), ("threat_type", "crime"), ("sector", "logistics")],
    },
]

# Client requests and the deliverables under them.
#
# A deliverable's `state` is the state the seed drives the tasking to:
#   assigned     left in To Do
#   in_progress  the assignee starts work, which creates a report from `template`
#   completed    the assignee starts work, then the tasking is completed
#   linked       an already released report is linked to the deliverable, which completes it
# `due_hours` is relative to the run, so negative means overdue.
REQUESTS = [
    {
        "slugline": "RFI-CASTELLAN-014",
        "name": "Castellan Energy RFI 014",
        "headline": "Castellan Energy: road movement risk, Suez to Cairo corridor",
        "agenda": "Castellan Energy",
        "description": (
            "Castellan Energy asks for an assessment of road movement risk on the Suez to Cairo "
            "corridor for a contractor rotation in the first half of next month."
        ),
        "internal_note": "Client contact: Karim Saleh. Deliverable is an RFI Response, TLP:AMBER.",
        "ednote": "800 words, RFI Response profile, cleared by the MENA team lead before release.",
        "urgency": 3,
        "subject": [("region", "mena"), ("country", "eg"), ("sector", "energy")],
        "deliverables": [
            {
                "ref": "RFI-CASTELLAN-014",
                "headline": "Castellan Energy: road movement risk, Suez to Cairo corridor",
                "description": "Route by route read on the corridor for the rotation window.",
                "ednote": "800 words, RFI Response profile.",
                "internal_note": "Client contact: Karim Saleh. TLP:AMBER.",
                "desk": "MENA",
                "user": "omar.nasser",
                "due_hours": 48,
                "state": "assigned",
                "template": "RFI Response",
            },
        ],
    },
    {
        "slugline": "RFI-NORDFREIGHT-031",
        "name": "Nordfreight Logistics RFI 031",
        "headline": "Nordfreight: exposure to the Gdansk terminal warning strike",
        "agenda": "Nordfreight Logistics",
        "event": "EV-PL-GDANSK-STRIKE",
        "description": (
            "Nordfreight asks what the announced Gdansk warning strike means for three inbound calls and "
            "for the onward rail leg to Poznan."
        ),
        "internal_note": "Client contact: Erik Dahl. He wants the gate position stated explicitly, not implied.",
        "ednote": "RFI Response profile. Name the calls by ETA, not by vessel.",
        "urgency": 2,
        "subject": [("region", "europe"), ("country", "pl"), ("sector", "logistics"),
                    ("threat_type", "industrial_action")],
        "deliverables": [
            {
                "ref": "RFI-NFL-031-RESP",
                "headline": "Nordfreight RFI 031: Gdansk strike exposure",
                "description": "Call by call read, plus the rail leg and the alternative of Gdynia.",
                "ednote": "RFI Response profile, 600 words.",
                "internal_note": "Erik Dahl wants this before his Thursday planning call.",
                "desk": "Europe",
                "user": "maja.lindqvist",
                "due_hours": 26,
                "state": "in_progress",
                "template": "RFI Response",
            },
            {
                "ref": "RFI-NFL-031-SCAN",
                "headline": "Gdansk strike: union and terminal statements",
                "description": "Collect and timestamp every public statement from the union and the terminal.",
                "ednote": "Source notes only, no assessment. Hand to Europe when done.",
                "internal_note": "Terminal press office posts to its own site first, then the wires.",
                "desk": "Watch",
                "user": "dana.reyes",
                "due_hours": -4,
                "state": "assigned",
                "template": "Alert intake",
            },
        ],
    },
    {
        "slugline": "RFI-AURELIA-022",
        "name": "Aurelia Pharma RFI 022",
        "headline": "Aurelia Pharma: cold chain continuity around the Barcelona fair",
        "agenda": "Aurelia Pharma",
        "event": "EV-ES-PHARMA-FAIR",
        "description": (
            "Aurelia Pharma asks for a continuity read on its Barcelona cold chain during the logistics fair, "
            "including a travel annex for the delegation."
        ),
        "internal_note": "Client contact: Hanna Weiss. Van load theft is the concern, not the fair itself.",
        "ednote": "RFI Response profile with a short travel annex.",
        "urgency": 3,
        "subject": [("region", "europe"), ("country", "es"), ("sector", "pharma"), ("threat_type", "crime")],
        "deliverables": [
            {
                "ref": "RFI-AUR-022-RESP",
                "headline": "Aurelia RFI 022: Barcelona cold chain and delegation travel",
                "description": "Continuity read on the depot and the last mile, plus a delegation travel annex.",
                "ednote": "RFI Response profile, 700 words including the annex.",
                "internal_note": "Hanna Weiss asked for named streets around the industrial estate.",
                "desk": "Europe",
                "user": "tomas.havel",
                "due_hours": 72,
                "state": "assigned",
                "template": "RFI Response",
            },
            {
                "ref": "RFI-AUR-022-SCAN",
                "headline": "Barcelona fair week: theft reporting sweep",
                "description": "Daily sweep of local police and port reporting for cargo and vehicle theft.",
                "ednote": "Source notes only. Flag anything within two kilometres of the estate.",
                "internal_note": "Catalan police publish weekly, the city daily. Use both.",
                "desk": "Watch",
                "user": "dana.reyes",
                "due_hours": 20,
                "state": "in_progress",
                "template": "Alert intake",
            },
        ],
    },
    {
        "slugline": "RFI-CASTELLAN-015",
        "name": "Castellan Energy RFI 015",
        "headline": "Castellan Energy: delegation posture for the Abu Dhabi summit",
        "agenda": "Castellan Energy",
        "event": "EV-AE-ENERGY-SUMMIT",
        "description": (
            "Castellan Energy asks for a security posture for its summit delegation, covering venue access, "
            "hotel selection and the credential phishing seen before previous editions."
        ),
        "internal_note": "Client contact: Karim Saleh. He has asked for the cyber part to be usable by his IT team.",
        "ednote": "RFI Response profile. Physical and cyber in one document, clearly separated.",
        "urgency": 2,
        "subject": [("region", "mena"), ("country", "ae"), ("sector", "energy"), ("threat_type", "cyber")],
        "deliverables": [
            {
                "ref": "RFI-CAS-015-RESP",
                "headline": "Castellan RFI 015: Abu Dhabi summit delegation posture",
                "description": "Venue and hotel posture, movement plan, and the phishing indicators to watch.",
                "ednote": "RFI Response profile, 900 words.",
                "internal_note": "Cleared by the MENA team lead before it goes out.",
                "desk": "MENA",
                "user": "omar.nasser",
                "due_hours": 96,
                "state": "completed",
                "template": "RFI Response",
            },
        ],
    },
    {
        "slugline": "REQ-PL-GDANSK-STRIKE",
        "post": True,
        "name": "Gdansk terminal warning strike",
        "headline": "Gdansk terminal warning strike: alert and watch cover",
        "agenda": "Nordfreight Logistics",
        "event": "EV-PL-GDANSK-STRIKE",
        "description": "Standing cover for the announced 24 hour warning strike at the Gdansk deepwater terminal.",
        "internal_note": "Two deliverables: the alert from Europe, the statement log from Watch.",
        "ednote": "Alert profile. Severity high if gate operations are included in the notice.",
        "urgency": 2,
        "subject": [("region", "europe"), ("country", "pl"), ("sector", "logistics"),
                    ("threat_type", "industrial_action")],
        "deliverables": [
            {
                "ref": "BD-EU-GDANSK-ALERT",
                "headline": "Gdansk terminal warning strike: operational effect",
                "description": "What stops, what keeps moving, and for how long.",
                "ednote": "Alert profile, 400 words, recommended actions mandatory.",
                "internal_note": "Do not publish before the gate position is confirmed.",
                "desk": "Europe",
                "user": "maja.lindqvist",
                "due_hours": 48,
                "state": "assigned",
                "template": "Alert - Europe",
            },
            {
                "ref": "BD-WATCH-GDANSK",
                "headline": "Gdansk strike: overnight watch log",
                "description": "Overnight log of terminal, union and carrier notices.",
                "ednote": "Log only. Hand to Europe at the morning handover.",
                "internal_note": "Carrier advisories land between 02:00 and 05:00 local.",
                "desk": "Watch",
                "user": "dana.reyes",
                "due_hours": 12,
                "state": "completed",
                "template": "Alert intake",
            },
        ],
    },
    {
        "slugline": "REQ-GB-LONDON-DEMO",
        "post": True,
        "name": "Central London demonstration",
        "headline": "Central London demonstration: closures and follow-up",
        "event": "EV-GB-LONDON-DEMO",
        "description": "Cover for the announced march and the advertised counter-protest on the same route.",
        "internal_note": "Closures change late. The follow-up reuses the released alert BD-EU-412.",
        "ednote": "Alert profile. Movement advice for staff, no political framing.",
        "urgency": 3,
        "subject": [("region", "europe"), ("country", "gb"), ("threat_type", "civil_unrest")],
        "deliverables": [
            {
                "ref": "BD-EU-LONDON-ALERT",
                "headline": "Central London demonstration: road closures and movement advice",
                "description": "Closure map, timings and the advice for staff moving through the area.",
                "ednote": "Alert profile, 350 words.",
                "internal_note": "Police closure plan is republished the evening before. Check it again then.",
                "desk": "Europe",
                "user": "admin",
                "due_hours": 60,
                "state": "in_progress",
                "template": "Alert - Europe",
            },
            {
                "ref": "BD-EU-LONDON-FOLLOW",
                "headline": "Central London demonstration: what happened last time",
                "description": "Reference read on the previous march, delivered from the released alert.",
                "ednote": "Already covered. Link the released report rather than rewriting it.",
                "internal_note": "Delivered by linking BD-EU-412.",
                "desk": "Europe",
                "user": "maja.lindqvist",
                "due_hours": -30,
                "state": "linked",
                "link": "BD-EU-412",
            },
        ],
    },
    {
        "slugline": "REQ-FR-REST-RULING",
        "post": True,
        "name": "French rest period ruling",
        "headline": "French rest period ruling: operational reading",
        "agenda": "Nordfreight Logistics",
        "event": "EV-FR-REST-RULING",
        "description": "Cover for the appeal ruling on reduced rest at unstaffed sites and what it does to run times.",
        "internal_note": "Client wants the operational reading. Legal detail goes in one paragraph at most.",
        "ednote": "Alert profile. Say what changes for a Benelux to Iberia run.",
        "urgency": 3,
        "subject": [("region", "europe"), ("country", "fr"), ("sector", "logistics"), ("sector", "pharma"),
                    ("threat_type", "political")],
        "deliverables": [
            {
                "ref": "BD-EU-FR-RULING",
                "headline": "French rest period ruling: effect on cross-border run times",
                "description": "The ruling, the immediate effect, and whether a further appeal suspends it.",
                "ednote": "Alert profile, 450 words.",
                "internal_note": "Wait for the written judgment, not the courtroom summary.",
                "desk": "Europe",
                "user": "maja.lindqvist",
                "due_hours": 168,
                "state": "assigned",
                "template": "Alert - Europe",
            },
        ],
    },
    {
        "slugline": "REQ-NL-PORT-TALKS",
        "post": True,
        "name": "Rotterdam port labour talks",
        "headline": "Rotterdam port labour talks: standing round note",
        "agenda": "Nordfreight Logistics",
        "event": "EV-NL-PORT-TALKS",
        "description": "Standing cover for the weekly negotiation round between the operators and the dockers union.",
        "internal_note": "Two line note after every round. Alert only if the talks break down.",
        "ednote": "Alert profile used as a short note. No recommended actions unless the talks fail.",
        "urgency": 4,
        "subject": [("region", "europe"), ("country", "nl"), ("sector", "logistics"),
                    ("threat_type", "industrial_action")],
        "deliverables": [
            {
                "ref": "BD-EU-NL-TALKS",
                "headline": "Rotterdam port labour talks: round note",
                "description": "Outcome of the round and whether an overtime ban is back on the table.",
                "ednote": "Two lines unless the talks break down.",
                "internal_note": "The joint statement is posted to the port authority site within the hour.",
                "desk": "Europe",
                "user": "tomas.havel",
                "due_hours": 36,
                "state": "completed",
                "template": "Alert - Europe",
            },
        ],
    },
    {
        "slugline": "REQ-EG-FUEL-REVIEW",
        "post": True,
        "name": "Egypt fuel price review",
        "headline": "Egypt fuel price review: protest risk and haulage rates",
        "agenda": "Castellan Energy",
        "event": "EV-EG-FUEL-REVIEW",
        "description": "Cover for the quarterly fuel price review and the protest pattern that has followed it.",
        "internal_note": "Castellan asked to be told the same day. The protest read was delivered as BD-ME-202.",
        "ednote": "Alert profile. Separate the price change from the protest assessment.",
        "urgency": 2,
        "subject": [("region", "mena"), ("country", "eg"), ("sector", "energy"), ("threat_type", "civil_unrest")],
        "deliverables": [
            {
                "ref": "BD-ME-FUEL-READ",
                "headline": "Egypt fuel price review: effect on haulage rates",
                "description": "What the review does to contracted haulage rates on the Suez corridor.",
                "ednote": "Alert profile, 400 words.",
                "internal_note": "Overdue. Chase the haulier quotes before writing.",
                "desk": "MENA",
                "user": "omar.nasser",
                "due_hours": -2,
                "state": "assigned",
                "template": "Alert - MENA",
            },
            {
                "ref": "BD-ME-FUEL-DONE",
                "headline": "Egypt fuel price review: protest picture",
                "description": "Where protests appeared, how large, and how quickly they were dispersed.",
                "ednote": "Delivered. Linked to the released alert.",
                "internal_note": "Delivered by linking BD-ME-202.",
                "desk": "MENA",
                "user": "omar.nasser",
                "due_hours": -20,
                "state": "linked",
                "link": "BD-ME-202",
            },
        ],
    },
    {
        "slugline": "REQ-AE-ENERGY-SUMMIT",
        "post": True,
        "name": "Abu Dhabi energy summit",
        "headline": "Abu Dhabi energy summit: venue posture and phishing watch",
        "agenda": "Castellan Energy",
        "event": "EV-AE-ENERGY-SUMMIT",
        "description": "Cover for the ministerial summit, the closed traffic plan and the pre-summit phishing wave.",
        "internal_note": "Physical read from MENA, source sweep from Watch.",
        "ednote": "Alert profile. Keep the indicators in a list the client's IT team can use.",
        "urgency": 2,
        "subject": [("region", "mena"), ("country", "ae"), ("sector", "energy"), ("threat_type", "cyber")],
        "deliverables": [
            {
                "ref": "BD-ME-AE-SUMMIT",
                "headline": "Abu Dhabi energy summit: access, movement and phishing",
                "description": "Traffic plan, venue access and the phishing indicators seen so far.",
                "ednote": "Alert profile, 500 words with an indicator list.",
                "internal_note": "Team lead is writing this one herself.",
                "desk": "MENA",
                "user": "lucia.ferro",
                "due_hours": 240,
                "state": "in_progress",
                "template": "Alert - MENA",
            },
            {
                "ref": "BD-ME-AE-WATCH",
                "headline": "Summit week: phishing and spoofed domain sweep",
                "description": "Daily sweep for spoofed delegate registration and travel domains.",
                "ednote": "Source notes only. Hand the indicator list to MENA each morning.",
                "internal_note": "Previous edition used lookalike hotel booking domains.",
                "desk": "Watch",
                "user": "dana.reyes",
                "due_hours": 120,
                "state": "assigned",
                "template": "Alert intake",
            },
        ],
    },
    {
        "slugline": "REQ-BR-CUP-FINAL",
        "post": True,
        "name": "Sao Paulo cup final",
        "headline": "Sao Paulo cup final: crowd risk around the stadium ring",
        "event": "EV-BR-CUP-FINAL",
        "description": "Cover for the announced fan march and the closures around the stadium on final night.",
        "internal_note": "Crowd risk only. No club names, no match commentary.",
        "ednote": "Alert profile. Movement advice for staff and for site security.",
        "urgency": 3,
        "subject": [("region", "americas"), ("country", "br"), ("threat_type", "civil_unrest")],
        "deliverables": [
            {
                "ref": "BD-AM-BR-FINAL",
                "headline": "Sao Paulo cup final: closures and crowd risk",
                "description": "Closure ring, march route and the hours when movement is worst.",
                "ednote": "Alert profile, 350 words.",
                "internal_note": "City publishes the closure order two days out.",
                "desk": "Americas",
                "user": "lucia.ferro",
                "due_hours": 288,
                "state": "assigned",
                "template": "Alert - Americas",
            },
            {
                "ref": "BD-AM-BR-BRIEF",
                "headline": "Sao Paulo cup final: site security briefing note",
                "description": "One page note for the site security teams inside the closure ring.",
                "ednote": "Alert profile used as a briefing note.",
                "internal_note": "Reuse the closure map from the main alert once it exists.",
                "desk": "Americas",
                "user": "admin",
                "due_hours": 264,
                "state": "in_progress",
                "template": "Alert - Americas",
            },
        ],
    },
    {
        "slugline": "REQ-MX-CONVOY-REVIEW",
        "name": "Veracruz corridor convoy review",
        "headline": "Veracruz corridor convoy review: weekly corridor note",
        "event": "EV-MX-CONVOY-REVIEW",
        "description": "Standing cover for the weekly convoy security review on the Mexico City to Veracruz corridor.",
        "internal_note": "The corridor read for this round was delivered as BD-AM-101.",
        "ednote": "Alert profile used as a corridor note.",
        "urgency": 3,
        "subject": [("region", "americas"), ("country", "mx"), ("sector", "logistics"), ("threat_type", "crime")],
        "deliverables": [
            {
                "ref": "BD-AM-MX-CONVOY",
                "headline": "Veracruz corridor: hijacking pattern and departure windows",
                "description": "Incident pattern for the week and the departure windows agreed for the next one.",
                "ednote": "Delivered. Linked to the released alert.",
                "internal_note": "Delivered by linking BD-AM-101.",
                "desk": "Americas",
                "user": "lucia.ferro",
                "due_hours": -14,
                "state": "linked",
                "link": "BD-AM-101",
            },
        ],
    },
    {
        "slugline": "REQ-ES-PHARMA-FAIR",
        "post": True,
        "name": "Barcelona pharmaceutical fair",
        "headline": "Barcelona pharmaceutical fair: theft risk around the estate",
        "agenda": "Aurelia Pharma",
        "event": "EV-ES-PHARMA-FAIR",
        "description": "Cover for the fair week and the van load theft pattern in the surrounding industrial estates.",
        "internal_note": "Feeds the Aurelia RFI. Keep the two documents consistent on street names.",
        "ednote": "Alert profile. Name the estates, do not name the carriers.",
        "urgency": 3,
        "subject": [("region", "europe"), ("country", "es"), ("sector", "pharma"), ("threat_type", "crime")],
        "deliverables": [
            {
                "ref": "BD-EU-ES-FAIR",
                "headline": "Barcelona fair week: cargo theft risk around the estates",
                "description": "Where the thefts happened last time, and the hours they happened in.",
                "ednote": "Alert profile, 400 words.",
                "internal_note": "Cross-check with the Watch sweep before writing.",
                "desk": "Europe",
                "user": "maja.lindqvist",
                "due_hours": 192,
                "state": "assigned",
                "template": "Alert - Europe",
            },
        ],
    },
    {
        "slugline": "REQ-CZ-LOCAL-VOTE",
        "post": True,
        "name": "Czech municipal elections",
        "headline": "Czech municipal elections: city centre access on the two evenings",
        "event": "EV-CZ-LOCAL-VOTE",
        "description": "Cover for the municipal elections, focused on rally and counter-rally evenings in Prague and Brno.",
        "internal_note": "One page. No political forecast, and no party names beyond what the police notice says.",
        "ednote": "Alert profile, low severity unless the counter-rallies are confirmed.",
        "urgency": 4,
        "subject": [("region", "europe"), ("country", "cz"), ("threat_type", "political")],
        "deliverables": [
            {
                "ref": "BD-EU-CZ-VOTE",
                "headline": "Czech municipal elections: city centre access",
                "description": "Rally locations, expected closures and the two evenings that matter.",
                "ednote": "Alert profile, 300 words.",
                "internal_note": "Police publish rally notifications 48 hours ahead.",
                "desk": "Europe",
                "user": "tomas.havel",
                "due_hours": 240,
                "state": "assigned",
                "template": "Alert - Europe",
            },
        ],
    },
]
