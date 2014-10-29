import superdesk

from .app_prepopulate import PrepopulateService, \
    PrepopulateResource


def init_app(app):
    if superdesk.app.config.get('TESTING', False):
        endpoint_name = 'prepopulate'
        service = PrepopulateService(endpoint_name, backend=superdesk.get_backend())
        PrepopulateResource(endpoint_name, app=app, service=service)
