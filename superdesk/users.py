"""Superdesk Users"""

from superdesk import mongo

class EmptyUsernameException(Exception):
    def __str__(self):
        return """Username is empty"""

class ConflictUsernameException(Exception):
    def __str__(self):
        return "Username '%s' exists already" % self.args[0]

def create_user(userdata):
    """Create a new user"""
    if not userdata.get('username'):
        raise EmptyUsernameException()

    conflict_user = mongo.db.users.find_one({'username': userdata.get('username')})
    if conflict_user:
        print(conflict_user)
        raise ConflictUsernameException(userdata.get('username'))

    return mongo.db.users.insert(userdata)

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
