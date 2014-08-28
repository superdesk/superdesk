from superdesk.base_model import BaseModel
from superdesk.notification import push_notification


def init_app(app):
    CoverageModel(app=app)


class CoverageModel(BaseModel):
    endpoint_name = 'coverages'
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
        'assigned_user': BaseModel.rel('users', True),
        'assigned_desk': BaseModel.rel('desks', True),
        'planning_item': BaseModel.rel('planning', True, type='string'),
    }

    datasource = {'default_sort': [('_created', -1)]}

    def on_created(self, docs):
        push_notification('coverages', created=1)

    def on_updated(self, updates, original):
        push_notification('coverages', updated=1)

    def on_deleted(self, doc):
        push_notification('coverages', deleted=1)
