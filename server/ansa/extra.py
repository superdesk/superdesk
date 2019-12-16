
import superdesk
from superdesk.resource import not_enabled


def init_app(_app):
    # set mapping for extra to avoid mapping exceptions
    superdesk.register_item_schema_field('extra', {
        'type': 'dict',
        'nullable': True,
        'mapping': not_enabled,
    }, _app)
