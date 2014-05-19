"""Upload module"""

import superdesk


superdesk.domain('upload', {
    'schema': {
        'media': {'type': 'media', 'required': True},
        'CropLeft': {'type': 'integer'},
        'CropRight': {'type': 'integer'},
        'CropTop': {'type': 'integer'},
        'CropBottom': {'type': 'integer'},
        'URL': {'type': 'string'}
    },
    'item_methods': ['GET'],
    'resource_methods': ['GET', 'POST'],
    'public_methods': ['GET', 'POST']
})
