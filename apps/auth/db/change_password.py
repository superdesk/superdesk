import logging
import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.errors import SuperdeskApiError
from superdesk import get_resource_service


logger = logging.getLogger(__name__)


class ChangePasswordResource(Resource):
    schema = {
        'username': {
            'type': 'string',
            'required': True
        },
        'old_password': {
            'type': 'string',
            'required': True
        },
        'new_password': {
            'type': 'string',
            'required': True
        },
    }
    public_methods = ['POST']
    resource_methods = ['POST']
    item_methods = []


class ChangePasswordService(BaseService):

    def create(self, docs, **kwargs):
        for doc in docs:
            username = doc['username']
            try:
                get_resource_service('auth').authenticate({'username': username, 'password': doc['old_password']})
            except Exception:
                raise SuperdeskApiError.unauthorizedError('The provided old password is not correct.')

            user = superdesk.get_resource_service('users').find_one(req=None, username=username)
            superdesk.get_resource_service('users').update_password(user['_id'], doc['new_password'])
            del doc['old_password']
            del doc['new_password']
            return [user['_id']]
