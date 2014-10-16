from superdesk import utils as utils
from superdesk.services import BaseService


class AuthService(BaseService):

    def authenticate(self, document):
        raise NotImplementedError()

    def on_create(self, docs):
        for doc in docs:
            user = self.authenticate(doc)

            doc['user'] = user['_id']
            doc['token'] = utils.get_random_string(40)
            del doc['password']
