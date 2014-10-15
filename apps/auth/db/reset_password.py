import logging
import superdesk
from datetime import timedelta
from flask import current_app as app, render_template
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.utc import utcnow
from superdesk.utils import get_random_string
from settings import RESET_PASSWORD_TOKEN_TIME_TO_LIVE as token_ttl, ADMINS, CLIENT_URL
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
    where_clause = 'this.expire_time >= ISODate()'
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

    def store_reset_password_token(self, doc, email, days_alive=token_ttl):
        user = superdesk.get_resource_service('users').find_one(req=None, email=email)
        if not user:
            logger.warning('User password reset triggered with invalid email: %s' % email)
            raise superdesk.SuperdeskError(status_code=201, message='Created')
        now = utcnow()
        doc[app.config['DATE_CREATED']] = now
        doc[app.config['LAST_UPDATED']] = now
        doc['expire_time'] = now + timedelta(days=token_ttl)
        doc['user'] = user['_id']
        doc['token'] = get_random_string()
        ids = super().create([doc])
        return ids

    def initialize_reset_password(self, doc, email):
        ids = self.store_reset_password_token(doc, email)
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

        superdesk.get_resource_service('users').update_password(user_id, password)
        self.remove_all_tokens_for_email(reset_request['email'])
        self.remove_private_data(doc)
        return [reset_request['_id']]

    def remove_all_tokens_for_email(self, email):
        super().delete(lookup={'email': email})

    def remove_private_data(self, doc):
        self.remove_field_from(doc, 'password')
        self.remove_field_from(doc, 'token')
        self.remove_field_from(doc, 'user')

    def remove_field_from(self, doc, field_name):
        if doc and doc.get(field_name):
            del doc[field_name]

    def send_reset_password_email(self, doc):
        url = '{}/#/reset-password?token={}'.format(CLIENT_URL, doc['token'])
        hours = token_ttl * 24
        text_body = render_template("reset_password.txt", email=doc['email'], expires=hours, url=url)
        html_body = render_template("reset_password.html", email=doc['email'], expires=hours, url=url)
        send_email.delay(subject='Reset password', sender=ADMINS[0], recipients=[doc['email']],
                         text_body=text_body, html_body=html_body)
