import logging
import os
import eve
from eve.io.mongo import MongoJSONEncoder
from eve.render import send_response
import settings
from superdesk import signals, celery_app
import superdesk
from superdesk.auth import SuperdeskTokenAuth
from superdesk.celery_app import get_celery
from superdesk.desk_media_storage import SuperdeskGridFSMediaStorage
from superdesk.validator import SuperdeskValidator
import importlib


class SuperdeskEve(eve.Eve):
    """Superdesk app"""

    def load_config(self):
        """Let us override settings withing plugins"""
        super(SuperdeskEve, self).load_config()
        self.config.from_object(superdesk)


def setup_amazon(config):
    if ('AMAZON_CONTAINER_NAME' in os.environ and
            'AMAZON_ACCESS_KEY_ID' in os.environ and
            'AMAZON_SECRET_ACCESS_KEY' in os.environ):
        config['AMAZON_CONTAINER_NAME'] = os.environ.get('AMAZON_CONTAINER_NAME')
        config['AMAZON_ACCESS_KEY_ID'] = os.environ.get('AMAZON_ACCESS_KEY_ID')
        config['AMAZON_SECRET_ACCESS_KEY'] = os.environ.get('AMAZON_SECRET_ACCESS_KEY')
        config['AMAZON_REGION'] = os.environ.get('AMAZON_REGION')


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

    media_storage = SuperdeskGridFSMediaStorage

    if 'AMAZON_CONTAINER_NAME' in config:
        from superdesk.amazon_media_storage import AmazonMediaStorage
        media_storage = AmazonMediaStorage

    app = SuperdeskEve(
        data=superdesk.SuperdeskDataLayer,
        auth=SuperdeskTokenAuth,
        media=media_storage,
        settings=config,
        json_encoder=MongoJSONEncoder,
        validator=SuperdeskValidator)

    app.on_fetched_resource = signals.proxy_resource_signal('read', app)
    app.on_fetched_item = signals.proxy_item_signal('read', app)
    app.on_inserted = signals.proxy_resource_signal('created', app)

    for blueprint in superdesk.BLUEPRINTS:
        prefix = app.api_prefix or None
        app.register_blueprint(blueprint, url_prefix=prefix)

    @app.errorhandler(superdesk.SuperdeskError)
    def error_handler(error):
        """Return json error response.

        :param error: an instance of :attr:`superdesk.SuperdeskError` class
        """
        return send_response(None, (error.to_dict(), None, None, error.status_code))

    superdesk.app = app

    celery = get_celery(app)
    celery_app.app = app
    celery_app.celery = celery
    importlib.import_module('superdesk.archive_ingest')
    app.register_resource('archive_ingest', app.config['DOMAIN']['archive_ingest'])

    return app

config = setup_amazon({})
app = get_app(config=config)
celery = celery_app.celery

if __name__ == '__main__':

    if 'PORT' in os.environ:
        port = int(os.environ.get('PORT'))
        host = '0.0.0.0'
        debug = 'SUPERDESK_DEBUG' in os.environ
    else:
        port = 5000
        host = '127.0.0.1'
        debug = True
        superdesk.logger.setLevel(logging.INFO)
        superdesk.logger.addHandler(logging.StreamHandler())

    app.run(host=host, port=port, debug=debug, use_reloader=True)
