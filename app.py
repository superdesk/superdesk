import os
import eve
import superdesk
import settings
from superdesk import signals
from eve.io.mongo import MongoJSONEncoder
from superdesk.auth import SuperdeskTokenAuth
from cerberus.errors import ERROR_BAD_TYPE
import re

class SuperdeskEve(eve.Eve):
    """Superdesk API"""

    def load_config(self):
        """Let us override settings withing plugins"""
        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)

    def _validate_type_phone_number(self, field, value):
        """ Enables validation for `phone_number` schema attribute.
            :param field: field name.
            :param value: field value.
        """
        if not re.match("^(?:(?:0?[1-9][0-9]{8})|(?:(?:\+|00)[1-9][0-9]{9,11}))$", value):
            self._error(field, ERROR_BAD_TYPE % 'Phone Number')

def get_app(config=None):
    """App factory."""

    if config is None:
        config = {}

    for key in dir(settings):
        if key.isupper():
            config.setdefault(key, getattr(settings, key))

    app = SuperdeskEve(
        data=superdesk.SuperdeskDataLayer,
        auth=SuperdeskTokenAuth,
        settings=config,
        json_encoder=MongoJSONEncoder)

    app.on_fetch_resource = signals.proxy_resource_signal('read', app)
    app.on_fetch_item = signals.proxy_item_signal('read', app)

    for blueprint in superdesk.BLUEPRINTS:
        app.register_blueprint(blueprint, **blueprint.kwargs)

    superdesk.app = app
    return app


if __name__ == '__main__':

    if 'PORT' in os.environ:
        port = int(os.environ.get('PORT'))
        host = '0.0.0.0'
        debug = 'SUPERDESK_DEBUG' in os.environ
    else:
        port = 5000
        host = '127.0.0.1'
        debug = True

    app = get_app()
    app.run(host=host, port=port, debug=debug)
