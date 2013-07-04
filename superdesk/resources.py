from flask import request
from types import Resource
from users import get_token
from auth.decorators import auth_required

import models

def get_date(date):
    return date.isoformat()

def get_list_item(item):
    return {
        'guid': item.guid,
        'version': item.version,
        'urgency': item.urgency,
        'slugline': item.slugline,
        'headline': item.headline,
        'first_created': get_date(item.firstCreated),
        'version_created': get_date(item.versionCreated),
    }

class Items(Resource):
    '''Items resource.'''

    method_decorators = [auth_required]

    def get(self):
        query = models.Item.objects.order_by('-firstCreated').limit(25)
        return [get_list_item(item) for item in query]

class Auth(Resource):
    """Auth resource."""

    def post(self):
        try:
            user = models.User.objects.get(username=request.form.get('username'))
        except models.User.DoesNotExist:
            return {'username': 'does not exist'}, 400

        if user.test_password(request.form.get('password')):
            return {
                'auth_token': get_token(user).token
            }, 201
        else:
            return {'password': 'not valid'}, 400
