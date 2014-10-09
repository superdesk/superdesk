import logging
import superdesk
from flask import current_app as app, render_template
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.utc import utcnow
from superdesk.utils import get_random_string, get_hash
from settings import RESET_PASSWORD_TOKEN_TIME_TO_LIVE as token_ttl, ADMINS
from superdesk.emails import send_email


logger = logging.getLogger(__name__)


reset_schema = {
    'email': {'type': 'email'},
    'token': {'type': 'string'},
    'password': {'type': 'string'},
    'user': Resource.rel('users', True)
}


class ActiveTokensResource(Resource):
    internal_resource = True
    schema = reset_schema
    where_clause = '(ISODate() - this._created) / 3600000 <= %s' % token_ttl
    datasource = {
        'source': 'reset_user_password',
        'default_sort': [('_created', -1)],
        'filter': {'$where': where_clause}
    }
    resource_methods = []
    item_methods = []


class ResetPasswordResource(Resource):
    schema = reset_schema
    public_methods = ['POST']
    resource_methods = ['POST']
    item_methods = []


class ResetPasswordService(BaseService):

    def create(self, docs, **kwargs):
        for doc in docs:
            email = doc.get('email')
            key = doc.get('token')
            password = doc.get('password')

            if key and password:
                return self.reset_password(doc)
            if email:
                return self.initialize_reset_password(doc, email)
            raise superdesk.SuperdeskError(payload='Invalid request.')

    def initialize_reset_password(self, doc, email):
        user = superdesk.get_resource_service('users').find_one(req=None, email=email)
        if not user:
            logger.warning('User password reset triggered with invalid email: %s' % email)
            raise superdesk.SuperdeskError(status_code=201, message='Created')
        doc[app.config['DATE_CREATED']] = utcnow()
        doc[app.config['LAST_UPDATED']] = utcnow()
        doc['user'] = user['_id']
        doc['token'] = get_random_string()
        ids = super().create([doc])
        self.send_reset_password_email(doc)
        self.remove_private_data(doc)
        return ids

    def reset_password(self, doc):
        key = doc.get('token')
        password = doc.get('password')

        reset_request = superdesk.get_resource_service('active_tokens').find_one(req=None, token=key)
        if not reset_request:
            raise superdesk.SuperdeskError(payload='Invalid token received: %s' % key)

        user_id = reset_request['user']
        user = superdesk.get_resource_service('users').find_one(req=None, _id=user_id)
        if not user:
            raise superdesk.SuperdeskError(payload='Invalid user.')

        self.update_user_password(user_id, password)
        self.remove_all_tokens_for_email(reset_request['email'])
        self.remove_private_data(doc)
        return [reset_request['_id']]

    def remove_all_tokens_for_email(self, email):
        super().delete(lookup={'email': email})

    def update_user_password(self, user_id, password):
        updates = {}
        updates['password'] = get_hash(password, app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))
        updates[app.config['LAST_UPDATED']] = utcnow()
        superdesk.get_resource_service('users').patch(user_id, updates=updates)

    def remove_private_data(self, doc):
        self.remove_field_from(doc, 'password')
        self.remove_field_from(doc, 'token')
        self.remove_field_from(doc, 'user')

    def remove_field_from(self, doc, field_name):
        if doc and doc.get(field_name):
            del doc[field_name]

    def send_reset_password_email(self, doc):
        send_email.delay(subject='Reset password',
                         sender=ADMINS[0],
                         recipients=[doc['email']],
                         text_body=render_template("reset_password.txt", user=doc, expires=token_ttl),
                         html_body=render_template("reset_password.html", user=doc, expires=token_ttl))
