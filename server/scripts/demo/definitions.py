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
    "severity": _editor(4, "quarter", required=True),
    "region": _editor(5, "quarter", required=True),
    "country": _editor(6, "quarter"),
    "sector": _editor(7, "quarter"),
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
        "region": _editor(4, "quarter", required=True),
        "country": _editor(5, "quarter"),
        "sector": _editor(6, "quarter"),
        "threat_type": _editor(7, "quarter"),
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
RFI_EDITOR["severity"] = _editor(7, "quarter")
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
]

PRODUCTS = [
    {
        "name": "Briefdesk Portal feed",
        "description": "Every released report, pushed to the Briefdesk Portal.",
        "product_type": "both",
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

AI_PROVIDER_NAME = "OpenRouter"
AI_DEFAULT_MODEL = "openai/gpt-4o-mini"

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

CLIENT_REQUEST = {
    "agenda": "Castellan Energy",
    "slugline": "RFI-CASTELLAN-014",
    "headline": "Castellan Energy: road movement risk, Suez to Cairo corridor",
    "name": "Castellan Energy RFI 014",
    "description": (
        "Castellan Energy asks for an assessment of road movement risk on the Suez to Cairo "
        "corridor for a contractor rotation in the first half of next month."
    ),
    "internal_note": "Client contact: Karim Saleh. Deliverable is an RFI Response, TLP:AMBER.",
    "ednote": "800 words, RFI Response profile, cleared by the MENA team lead before release.",
    "desk": "MENA",
    "user": "omar.nasser",
    "due_in_days": 2,
    "subject": [("region", "mena"), ("country", "eg"), ("sector", "energy")],
}
