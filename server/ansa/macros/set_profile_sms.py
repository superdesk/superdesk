import logging
import superdesk

from apps.templates.content_templates import render_content_template_by_id

logger = logging.getLogger(__name__)

PROFILE = "SMS"


def callback(item, **kwargs):
    profile = superdesk.get_resource_service("content_types").find_one(
        req=None, label=PROFILE
    )
    if profile:
        item["profile"] = profile["_id"]
        template = superdesk.get_resource_service(
            "content_templates"
        ).get_template_by_name(PROFILE)
        if template:
            render_content_template_by_id(item, template["_id"], update=True)
        else:
            logger.warning("Template not found")
    else:
        logger.warning("Profile not found")
    return item


name = "Set Profile {}".format(PROFILE)
label = name
access_type = "backend"
action_type = "direct"
