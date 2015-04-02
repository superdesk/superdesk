
from superdesk.resource import Resource


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
        'desks': {
            'type': 'list',
            'schema': Resource.rel('desks', True)
        }
    }
    privileges = {'POST': 'highlights', 'PATCH': 'highlights', 'DELETE': 'highlights'}


class ArchiveHighlightsResource(Resource):
    datasource = {
        'source': 'archive'
    }
    schema = {
        'highlights': Resource.rel('highlights')
    }
    item_methods = ['GET', 'PATCH']
    privileges = {'PATCH': 'archive'}


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
