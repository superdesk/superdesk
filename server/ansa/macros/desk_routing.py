
from superdesk import get_resource_service
from superdesk.utc import utcnow
from superdesk.logging import logger


def routing(item, desk=None, **kwargs):
    if desk is None:
        desk_id = item.get('task', {}).get('desk')
        if desk_id:
            desk = get_resource_service('desks').find_one(req=None, _id=desk_id)
    if desk and desk.get('is_closed') and desk.get('closed_destination'):  # do routing
        logger.info('auto-routing item "%s" from desk "%s"', item.get('headline'), desk.get('name'))
        try:
            marked_desks = item.get('marked_desks', [])
            existing = [mark for mark in marked_desks if str(mark['desk_id']) == str(desk['closed_destination'])]
            if not existing:
                marked_desks.append({
                    'desk_id': str(desk['closed_destination']),
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
