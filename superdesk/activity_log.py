
import logging
import superdesk
from superdesk.utc import utcnow

class MongoDBHandler(logging.Handler):
    """Logging handler storing data into mongodb."""

    level = logging.INFO

    def emit(self, record):
        data = {}
        data['created'] = data['updated'] = utcnow()
        data['action'] = getattr(record, 'msg')
        data['level'] = getattr(record, 'levelname')
        data['module'] = getattr(record, 'name')
        data['user'] = getattr(record, 'user', {}).get('_id')
        superdesk.app.data.insert('activity', [data])

superdesk.logger.addHandler(MongoDBHandler())

superdesk.domain('activity', {
    'resource_methods': ['GET'],
    'item_methods': ['GET'],
    'schema': {
        'action': {'type': 'string'},
        'level': {'type': 'string'},
        'module': {'type': 'string'},
        'user': {
            'type': 'objectid',
            'data_relation': {
                'collection': 'users',
                'field': '_id',
                'embeddable': True
            }
        }
    }
})
