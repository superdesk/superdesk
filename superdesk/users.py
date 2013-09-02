"""Superdesk Users"""

from superdesk import mongo

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

    if mongo.db.users.find_one({'username': username}):
        raise ConflictUsernameException()

    user = {'username': username, 'password': password}
    mongo.db.users.insert(user)
    return user

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
