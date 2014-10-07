from superdesk.activity import add_activity
from superdesk.services import BaseService
from superdesk.utils import is_hashed, get_hash
from flask import current_app as app


def add_created_user_activity(user_docs):
    for user_doc in user_docs:
        add_activity('created user {{user}}', user=user_doc.get('display_name', user_doc.get('username')))


def add_deleted_user_activity(user_doc):
    add_activity('removed user {{user}}', user=user_doc.get('display_name', user_doc.get('username')))


class DBUsersService(BaseService):
    """
    Service class for UsersResource and should be used when AD is inactive.
    """

    def on_create(self, docs):
        for doc in docs:
            if doc.get('password', None) and not is_hashed(doc.get('password')):
                doc['password'] = get_hash(doc.get('password'), app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))

    def on_created(self, docs):
        add_created_user_activity(docs)

    def on_deleted(self, doc):
        add_deleted_user_activity(doc)


class ADUsersService(BaseService):
    """
    Service class for UsersResource and should be used when AD is active.
    """

    readonly_fields = ['username', 'display_name', 'password', 'email', 'phone', 'first_name', 'last_name']

    def on_created(self, docs):
        add_created_user_activity(docs)

    def on_fetched(self, doc):
        for document in doc['_items']:
            document['_readonly'] = ADUsersService.readonly_fields

    def on_deleted(self, doc):
        add_deleted_user_activity(doc)
