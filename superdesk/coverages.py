from superdesk.base_model import BaseModel


def init_app(app):
    CoverageModel(app=app)


def rel(resource, embeddable=False):
    return {
        'type': 'objectid',
        'data_relation': {'resource': resource, 'field': '_id', 'embeddable': embeddable}
    }


class CoverageModel(BaseModel):
    endpoint_name = 'coverages'
    schema = {
        'headline': {'type': 'string'},
        'type': {'type': 'string'},
        'ed_note': {'type': 'string'},
        'scheduled': {'type': 'datetime'},
        'delivery': rel('archive'),
        'assigned_user': rel('users', True),
        'assigned_desk': rel('desks', True),
        'planning_item': rel('planning'),
    }
