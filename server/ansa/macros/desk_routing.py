from superdesk import get_resource_service
from superdesk.logging import logger


def get_destination_desk(desk, limit=10):
    if not limit or not desk:
        return
    if not desk.get("is_closed"):
        return desk
    if not desk.get("closed_destination"):
        return desk
    return get_destination_desk(
        get_resource_service("desks").find_one(
            req=None, _id=desk["closed_destination"]
        ),
        limit - 1,
    )


def routing(item, desk=None, task=None, **kwargs):
    if not task:
        logger.info("no task for item %s", item)
        return item
    if desk is None:
        desk_id = item.get("task", {}).get("desk")
        if desk_id:
            desk = get_resource_service("desks").find_one(req=None, _id=desk_id)
    dest = get_destination_desk(desk)
    if dest and str(desk["_id"]) != str(dest["_id"]):
        logger.info(
            'auto-routing item "%s" from desk "%s" to "%s"',
            item.get("headline"),
            desk.get("name"),
            dest.get("name"),
        )
        task.update({"desk": dest["_id"], "stage": dest.get("working_stage")})
    return item


name = "desk_routing"
label = "Desk Routing"
callback = routing
access_type = "backend"
action_type = "direct"
