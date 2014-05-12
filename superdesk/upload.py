"""Upload module"""

import superdesk

superdesk.domain('upload', {
    'schema': {
        'name': {'type': 'string'},
        'media': {'type': 'media'}
    },
    'item_methods': ['GET'],
    'resource_methods': ['GET', 'POST'],
    'public_methods': ['GET', 'POST']
})
