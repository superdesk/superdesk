from datetime import datetime

from flask import request, url_for

from superdesk.types import Resource
from superdesk.users import get_token
from superdesk.auth.decorators import auth_required
from superdesk import models

def get_date(date):
    return date.isoformat()

def get_list_item(item):
    return {
        'self_url': url_for('item', id=item.guid),
        'guid': item.guid,
        'version': item.version,
        'urgency': item.urgency,
        'slugline': item.slugline,
        'headline': item.headline,
        'first_created': get_date(item.firstCreated),
        'version_created': get_date(item.versionCreated),
    }

class ItemList(Resource):
    """Item List Resource"""

    method_decorators = [auth_required]

    def get(self):
        query = models.Item.objects.order_by('-firstCreated').limit(25)
        return [get_list_item(item) for item in query]

    def post(self):
        data = request.form.to_dict()
        item = models.Item(**data)
        item.firstCreated = datetime.utcnow()
        item.versionCreated = datetime.utcnow()
        item.save()
        return get_list_item(item), 201

class Item(Resource):
    """Item Resource"""

    def get(self, id):
        pass

class Auth(Resource):
    """Auth Resource"""

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
