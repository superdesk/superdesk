from apps.auth.auth import SuperdeskTokenAuth
from .auth import AuthUsersResource, AuthResource  # noqa
from .sessions import SesssionsResource
import superdesk
from superdesk.services import BaseService
from superdesk.resource import Resource
from settings import RESET_PASSWORD_TOKEN_TIME_TO_LIVE as token_ttl
from .db.reset_password import reset_schema  # noqa


def init_app(app):
    app.auth = SuperdeskTokenAuth()  # Overwrite the app default auth

    endpoint_name = 'auth_users'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    AuthUsersResource(endpoint_name, app=app, service=service)

    endpoint_name = 'sessions'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    SesssionsResource(endpoint_name, app=app, service=service)

    endpoint_name = 'active_tokens'
    service = BaseService(endpoint_name, backend=superdesk.get_backend())
    ActiveTokensResource(endpoint_name, app=app, service=service)


class ActiveTokensResource(Resource):
    internal_resource = True
    schema = reset_schema
    where_clause = '(ISODate() - this._created) / 3600000 <= %s' % token_ttl
    datasource = {
        'source': 'reset_user_password',
        'default_sort': [('_created', -1)],
        'filter': {'$where': where_clause}
    }
    resource_methods = []
    item_methods = []
