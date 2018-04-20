
from superdesk import get_resource_service
from superdesk.utc import utcnow
from superdesk.logging import logger


def get_destination_desk(desk, limit=10):
    if not limit or not desk:
        return
    if not desk.get('is_closed'):
        return desk
    if not desk.get('closed_destination'):
        return desk
    return get_destination_desk(
        get_resource_service('desks').find_one(req=None, _id=desk['closed_destination']),
        limit - 1
    )


def routing(item, desk=None, **kwargs):
    if desk is None:
        desk_id = item.get('task', {}).get('desk')
        if desk_id:
            desk = get_resource_service('desks').find_one(req=None, _id=desk_id)
    dest = get_destination_desk(desk)
    if dest and str(desk['_id']) != str(dest['_id']):
        logger.info('auto-routing item "%s" from desk "%s" to "%s"',
                    item.get('headline'), desk.get('name'), dest.get('name'))
        try:
            marked_desks = item.get('marked_desks', [])
            existing = [mark for mark in marked_desks if str(mark['desk_id']) == str(dest['_id'])]
            if not existing:
                marked_desks.append({
                    'desk_id': str(dest['_id']),
                    'date_marked': utcnow(),
                })
                item['marked_desks'] = marked_desks
        except Exception:
            logger.exception('auto-routing error')
    return item


name = 'desk_routing'
label = 'Desk Routing'
callback = routing
access_type = 'backend'
action_type = 'direct'
