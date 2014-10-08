from superdesk import utils as utils
from apps.auth.errors import UserInactiveError
from superdesk.services import BaseService


class AuthService(BaseService):

    def authenticate(self, document):
        pass

    def on_create(self, docs):
        for doc in docs:
            user = self.authenticate(doc)

            if user.get('status', 'active') == 'inactive':
                raise UserInactiveError()

            doc['user'] = user['_id']
            doc['token'] = utils.get_random_string(40)
            del doc['password']
