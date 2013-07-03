import utils

from models import User, AuthToken

def create_user(username, password = None):
    user = User(username=username)
    user.set_password(password)
    user.save()
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

