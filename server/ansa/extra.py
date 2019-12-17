
import superdesk
from superdesk.resource import not_indexed


def init_app(_app):
    # set mapping for extra to avoid mapping exceptions
    superdesk.register_item_schema_field('extra', {
        'type': 'dict',
        'nullable': True,
        'mapping': {
            'type': 'object',
            'properties': {
                'DateCreated': not_indexed,
                'DateRelease': not_indexed,
            },
        },
    }, _app)
