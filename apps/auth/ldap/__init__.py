import superdesk
from apps.auth import AuthResource
from .ldap import LdapAuthService, ADAuth  # noqa
from .commands import ImportUserProfileFromADCommand  # noqa


def init_app(app):
    endpoint_name = 'auth'
    service = LdapAuthService(endpoint_name, backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)
