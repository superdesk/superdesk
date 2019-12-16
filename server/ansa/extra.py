
import superdesk
from superdesk.resource import not_indexed


def init_app(_app):
    # set mapping for extra to avoid mapping exceptions
    superdesk.register_item_schema_field('extra', {
        'type': 'dict',
        'nullable': True,
        'schema': {
            'DateCreated': {'type': 'string', 'nullable': True, 'mapping': not_indexed},
            'DateRelease': {'type': 'string', 'nullable': True, 'mapping': not_indexed},
        },
    }, _app)
