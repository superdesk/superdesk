
import os
import logging
import importlib
import jinja2
import eve
import settings
import superdesk
from flask.ext.mail import Mail
from eve.io.mongo import MongoJSONEncoder
from eve.render import send_response
from superdesk import signals
from superdesk.celery_app import init_celery
from eve.auth import TokenAuth
from superdesk.storage.desk_media_storage import SuperdeskGridFSMediaStorage
from superdesk.validator import SuperdeskValidator
from raven.contrib.flask import Sentry


sentry = Sentry(register_signal=False, wrap_wsgi=False)


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

    if config['AMAZON_CONTAINER_NAME']:
        from superdesk.storage.amazon.amazon_media_storage import AmazonMediaStorage
        from superdesk.storage.amazon.import_from_amazon import ImportFromAmazonCommand
        media_storage = AmazonMediaStorage
        superdesk.command('import:amazon', ImportFromAmazonCommand())

    config['DOMAIN'] = {}

    app = eve.Eve(
        data=superdesk.SuperdeskDataLayer,
        auth=TokenAuth,
        media=media_storage,
        settings=config,
        json_encoder=MongoJSONEncoder,
        validator=SuperdeskValidator)

    custom_loader = jinja2.ChoiceLoader([
        app.jinja_loader,
        jinja2.FileSystemLoader(['superdesk/templates'])
    ])
    app.jinja_loader = custom_loader

    app.mail = Mail(app)

    app.on_fetched_resource += signals.proxy_resource_signal('read', app)
    app.on_fetched_item += signals.proxy_item_signal('read', app)
    app.on_inserted += signals.proxy_resource_signal('created', app)

    @app.errorhandler(superdesk.SuperdeskError)
    def client_error_handler(error):
        """Return json error response.

        :param error: an instance of :attr:`superdesk.SuperdeskError` class
        """
        return send_response(None, (error.to_dict(), None, None, error.status_code))

    @app.errorhandler(500)
    def server_error_handler(error):
        """Log server errors."""
        app.sentry.captureException()
        return_error = superdesk.SuperdeskError(status_code=500)
        return client_error_handler(return_error)

    init_celery(app)
    for module_name in app.config['INSTALLED_APPS']:
        app_module = importlib.import_module(module_name)
        try:
            app_module.init_app(app)
        except AttributeError:
            pass

    for resource in superdesk.DOMAIN:
        app.register_resource(resource, superdesk.DOMAIN[resource])

    for blueprint in superdesk.BLUEPRINTS:
        prefix = app.api_prefix or None
        app.register_blueprint(blueprint, url_prefix=prefix)

    # we can only put mapping when all resources are registered
    app.data.elastic.put_mapping(app)

    app.sentry = sentry
    sentry.init_app(app)

    return app

if __name__ == '__main__':

    debug = True
    port = int(os.environ.get('PORT', '5000'))
    host = '0.0.0.0'
    superdesk.logger.setLevel(logging.INFO)
    superdesk.logger.addHandler(logging.StreamHandler())

    app = get_app()
    app.run(host=host, port=port, debug=debug, use_reloader=debug)
