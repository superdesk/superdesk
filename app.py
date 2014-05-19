import os
import eve
import settings
import superdesk
from superdesk import signals
from eve.io.mongo import MongoJSONEncoder
from eve.io.mongo.media import GridFSMediaStorage
from superdesk.auth import SuperdeskTokenAuth
from superdesk.validator import SuperdeskValidator
from eve.render import send_response


class SuperdeskEve(eve.Eve):
    """Superdesk app"""

    def load_config(self):
        """Let us override settings withing plugins"""
        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)


def get_app(config=None):
    """App factory.

    :param config: configuration that can override config from `settings.py`
    :return: a new SuperdeskEve app instance
    """

    if config is None:
        config = {}

    for key in dir(settings):
        if key.isupper():
            config.setdefault(key, getattr(settings, key))

    app = SuperdeskEve(
        data=superdesk.SuperdeskDataLayer,
        auth=SuperdeskTokenAuth,
        media=GridFSMediaStorage,
        settings=config,
        json_encoder=MongoJSONEncoder,
        validator=SuperdeskValidator)

    app.on_fetched_resource = signals.proxy_resource_signal('read', app)
    app.on_fetched_item = signals.proxy_item_signal('read', app)
    app.on_inserted = signals.proxy_resource_signal('created', app)

    for blueprint in superdesk.BLUEPRINTS:
        app.register_blueprint(blueprint, **blueprint.kwargs)

    @app.errorhandler(superdesk.SuperdeskError)
    def error_handler(error):
        """Return json error response.

        :param error: an instance of :attr:`superdesk.SuperdeskError` class
        """
        return send_response(None, (error.to_dict(), None, None, error.status_code))

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
    app.run(host=host, port=port, debug=debug, use_reloader=True)
