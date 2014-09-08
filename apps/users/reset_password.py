import superdesk
from flask import current_app as app
from superdesk.models import BaseModel
from superdesk.utils import get_random_string
from superdesk.emails import send_email
from settings import RESET_PASSWORD_TOKEN_TIME_TO_LIVE as token_ttl
import logging
from .users import hash_password
from superdesk.utc import utcnow


logger = logging.getLogger(__name__)
reset_schema = {
    'email': {'type': 'email'},
    'token': {'type': 'string'},
    'password': {'type': 'string'},
    'user': BaseModel.rel('users', True)
}


def send_reset_password_email(doc):
    from settings import ADMINS, RESET_PASSWORD_TOKEN_TIME_TO_LIVE as expiration_time
    from flask import render_template
    send_email.delay(subject='Reset password',
                     sender=ADMINS[0],
                     recipients=[doc['email']],
                     text_body=render_template("reset_password.txt", user=doc, expires=expiration_time),
                     html_body=render_template("reset_password.html", user=doc, expires=expiration_time))


class ActiveTokensModel(BaseModel):
    endpoint_name = 'active_tokens'
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


class ResetPasswordModel(BaseModel):
    endpoint_name = 'reset_user_password'
    schema = reset_schema
    public_methods = ['POST']
    resource_methods = ['POST']
    item_methods = []

    def create(self, docs, trigger_events=None, **kwargs):
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
        user = app.data.find_one('users', req=None, email=email)
        if not user:
            logger.warning('User password reset triggered with invalid email: %s' % email)
            raise superdesk.SuperdeskError(status_code=201, message='Created')
        doc[app.config['DATE_CREATED']] = utcnow()
        doc[app.config['LAST_UPDATED']] = utcnow()
        doc['user'] = user['_id']
        doc['token'] = get_random_string()
        ids = super().create([doc])
        send_reset_password_email(doc)
        self.remove_private_data(doc)
        return ids

    def reset_password(self, doc):
        key = doc.get('token')
        password = doc.get('password')

        reset_request = superdesk.apps['active_tokens'].find_one(req=None, token=key)
        if not reset_request:
            raise superdesk.SuperdeskError(payload='Invalid token received: %s' % key)

        user_id = reset_request['user']
        user = app.data.find_one('users', req=None, _id=user_id)
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
        hashed = hash_password(password)
        updates['password'] = hashed
        updates[app.config['LAST_UPDATED']] = utcnow()
        superdesk.apps['users'].update(id=user_id, updates=updates, trigger_events=True)

    def remove_private_data(self, doc):
        self.remove_field_from(doc, 'password')
        self.remove_field_from(doc, 'token')
        self.remove_field_from(doc, 'user')

    def remove_field_from(self, doc, field_name):
        if doc and doc.get(field_name):
            del doc[field_name]
