
from superdesk.resource import Resource


class HighlightsResource(Resource):
    '''
    Highlights schema
    '''
    schema = {
        'name': {
            'type': 'string',
            'required': True
        },
        'desks': {
            'type': 'list',
            'schema': Resource.rel('desks', True)
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
