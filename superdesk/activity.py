from .base_model import BaseModel
import flask
from eve.methods.post import post_intern

# 
# class ActivityLogHandler(logging.Handler):
#     """Logging handler storing data into mongodb."""
# 
#     level = logging.INFO
# 
#     def emit(self, record):
#         data = {}
#         data['created'] = data['updated'] = utcnow()
#         data['action'] = getattr(record, 'msg')
#         data['level'] = getattr(record, 'levelname')
#         data['module'] = getattr(record, 'name')
#         data['user'] = getattr(record, 'user', {}).get('_id')
#         superdesk.app.data.insert('activity', [data])

# superdesk.logger.addHandler(ActivityLogHandler())

    
def init_app(app):
    activityModel = ActivityModel(app=app)
    app.on_insert += activityModel.on_generic_insert


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
    exclude = {endpoint_name, 'notification'}

    def on_generic_insert(self, resource, docs):
        if resource in self.exclude: return

        user = getattr(flask.g, 'user', None)
        if not user: return

        activity = {
            'user': user.get('_id'),
            'resource': resource,
            'action': 'create',
            'extra': docs[0]
        }
        post_intern(self.endpoint_name, activity)
