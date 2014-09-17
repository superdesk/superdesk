from superdesk.resource import Resource
from superdesk.notification import push_notification
from superdesk.services import BaseService
import superdesk


def init_app(app):
    endpoint_name = 'coverages'
    service = CoverageService(endpoint_name, backend=superdesk.get_backend())
    CoverageResource(endpoint_name, app=app, service=service)


class CoverageResource(Resource):
    schema = {
        'headline': {'type': 'string'},
        'coverage_type': {
            'type': 'string',
            'allowed': ['story', 'photo', 'video', 'graphics', 'live-blogging'],
            'default': 'story',
            'required': True
        },
        'ed_note': {'type': 'string'},
        'scheduled': {'type': 'datetime'},
        'delivery': {'type': 'string'},
        'assigned_user': Resource.rel('users', True),
        'assigned_desk': Resource.rel('desks', True),
        'planning_item': Resource.rel('planning', True, type='string'),
    }

    datasource = {'default_sort': [('_created', -1)]}


class CoverageService(BaseService):

    def on_created(self, docs):
        push_notification('coverages', created=1)

    def on_updated(self, updates, original):
        push_notification('coverages', updated=1)

    def on_deleted(self, doc):
        push_notification('coverages', deleted=1)
