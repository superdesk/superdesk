"""Superdesk Users"""

from app import app

class EmptyUsernameException(Exception):
    def __str__(self):
        return """Username is empty"""

class ConflictUsernameException(Exception):
    def __str__(self):
        return """Username exists already"""

def create_user(username, password=None):
    """Create a new user"""
    if not username:
        raise EmptyUsernameException()

    if app.data.driver.db.users.find_one({'username': username}):
        raise ConflictUsernameException()

    return app.data.driver.db.users.insert({'username': username, 'password': password})

def get_token(user):
    token = AuthToken(token=utils.get_random_string(40), user=user)
    token.save()
    return token

def is_valid_token(auth_token):
    try:
        token = AuthToken.objects.get(token=auth_token)
        return token.is_valid()
    except AuthToken.DoesNotExist:
        return False
