import logging
import superdesk
from superdesk.utc import utcnow
from .base_model import BaseModel
import flask


class ActivityLogHandler(logging.Handler):
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

# superdesk.logger.addHandler(ActivityLogHandler())


def init_app(app):
    ActivityModel(app=app)


class ActivityModel(BaseModel):
    endpoint_name = 'activity'
    resource_methods = ['GET']
    item_methods = []
    schema = {
        'resource': {'type': 'string'},
        'action': {'type': 'string'},
        'extra': {'type': 'dict'},
        'user': {
            'type': 'objectid',
            'data_relation': {
                'resource': 'users',
                'field': '_id',
                'embeddable': True
            }
        }
    }

    def on_create(self, data, resource, docs):
        if resource == 'activity':
            return

        if not getattr(flask.g, 'user', False):
            return

        activity = {}
        activity['created'] = activity['updated'] = utcnow()
        activity['user'] = getattr(flask.g, 'user', {}).get('_id')
        activity['resource'] = resource
        activity['action'] = 'create'
        activity['extra'] = docs[0]
        # always the activity is written on mongo
        super().create([activity])
