import logging
from flask import json
import superdesk

logger = logging.getLogger(__name__)


class AuthRequiredError(superdesk.SuperdeskError):
    """Auth required error."""
    status_code = 401
    payload = {'auth': 1}


class AuthError(superdesk.SuperdeskError):
    """Base Auth Error"""
    status_code = 400
    payload = {'credentials': 1}


class NotFoundAuthError(AuthError):
    """Username Not Found Auth Error"""
    pass


class CredentialsAuthError(AuthError):
    """Credentials Not Match Auth Exception"""
    pass


class ForbiddenError(superdesk.SuperdeskError):
    status_code = 403


class UserInactiveError(ForbiddenError):
    """User is inactive, access restricted"""
    payload = {'status': 'inactive'}
    message = 'Account suspended, access restricted.'


def raiseCredentialsAuthError(credentials):
    logger.warning("Login failure: %s" % json.dumps(credentials))
    raise CredentialsAuthError()
