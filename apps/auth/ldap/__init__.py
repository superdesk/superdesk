import superdesk
from apps.auth import AuthResource
from .ldap import LdapAuthService, authenticate, ADAuth  # noqa
from .commands import ImportUserProfileFromADCommand

def init_app(app):
    endpoint_name = 'auth'
    service = LdapAuthService(endpoint_name, backend=superdesk.get_backend())
    AuthResource(endpoint_name, app=app, service=service)
