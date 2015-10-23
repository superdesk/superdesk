
from superdesk.resource import Resource

TODAY_DATE = 'now/d'
WEEK_DATE = 'now/w'

allowed_times = ['now-{0}h'.format(hour) for hour in range(1, 25)]
allowed_times.append(TODAY_DATE)
allowed_times.append(WEEK_DATE)


class HighlightsResource(Resource):
    '''
    Highlights schema
    '''
    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True
        },
        'template': Resource.rel('content_templates', nullable=True),
        'desks': {
            'type': 'list',
            'schema': Resource.rel('desks', True)
        },
        'auto_insert': {
            'type': 'string',
            'allowed': allowed_times,
            'default': TODAY_DATE,
        },
        'groups': {
            'type': 'list',
            'schema': {
                'type': 'string'
            }
        }
    }
    privileges = {'POST': 'highlights', 'PATCH': 'highlights', 'DELETE': 'highlights'}


class MarkedForHighlightsResource(Resource):
    '''
    Marked for highlights Schema
    '''
    schema = {
        'highlights': {
            'type': 'string',
            'required': True
        },
        'marked_item': {
            'type': 'string',
            'required': True
        }
    }
    privileges = {'POST': 'mark_for_highlights'}
