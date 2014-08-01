from superdesk.base_model import BaseModel


def init_app(app):
    CoverageModel(app=app)


class CoverageModel(BaseModel):
    endpoint_name = 'coverages'
    schema = {
        'guid': {
            'type': 'string',
            'unique': True
        },
        'headline': {
            'type': 'string'
        },
        'scheduled': {
            'type': 'datetime'
        },
        'ed_note': {
            'type': 'string'
        },
        'delivery': {
            'type': 'string'
        }
    }

    datasource = {
        'search-backend': 'elastic'
    }
