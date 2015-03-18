# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

import logging
import superdesk
from datetime import timedelta
from flask import current_app as app
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.utc import utcnow
from superdesk.utils import get_random_string
from superdesk.emails import send_reset_password_email
from superdesk.errors import SuperdeskApiError


logger = logging.getLogger(__name__)


reset_schema = {
    'email': {'type': 'email'},
    'token': {'type': 'string'},
    'password': {'type': 'string'},
    'expire_time': {'type': 'datetime'},
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

    def check_if_valid_token(self, token):
        reset_request = superdesk.get_resource_service('active_tokens').find_one(req=None, token=token)
        if not reset_request:
            logger.warning('Invalid token received: %s' % token)
            raise SuperdeskApiError.unauthorizedError('Invalid token received')

        return reset_request

    def create(self, docs, **kwargs):
        for doc in docs:
            email = doc.get('email')
            key = doc.get('token')
            password = doc.get('password')

            if key and password:
                return self.reset_password(doc)
            if email:
                return self.initialize_reset_password(doc, email)
            if key:
                token_req = self.check_if_valid_token(key)
                return [token_req.get('_id')]

            raise SuperdeskApiError.badRequestError('Either key:password or email must be provided')

    def store_reset_password_token(self, doc, email, days_alive, user_id):
        token_ttl = app.config['RESET_PASSWORD_TOKEN_TIME_TO_LIVE']
        now = utcnow()
        doc[app.config['DATE_CREATED']] = now
        doc[app.config['LAST_UPDATED']] = now
        doc['expire_time'] = now + timedelta(days=token_ttl)
        doc['user'] = user_id
        doc['token'] = get_random_string()
        ids = super().create([doc])
        return ids

    def initialize_reset_password(self, doc, email):
        token_ttl = app.config['RESET_PASSWORD_TOKEN_TIME_TO_LIVE']

        user = superdesk.get_resource_service('users').find_one(req=None, email=email)
        if not user:
            logger.warning('User password reset triggered with invalid email: %s' % email)
            raise SuperdeskApiError.badRequestError('Invalid email')

        if not user.get('is_enabled', False):
            logger.warning('User password reset triggered for an disabled user')
            raise SuperdeskApiError.forbiddenError('User not enabled')

        if not user.get('is_active', False):
            logger.warning('User password reset triggered for an inactive user')
            raise SuperdeskApiError.forbiddenError('User not active')

        ids = self.store_reset_password_token(doc, email, token_ttl, user['_id'])
        send_reset_password_email(doc)
        self.remove_private_data(doc)
        return ids

    def reset_password(self, doc):
        key = doc.get('token')
        password = doc.get('password')

        reset_request = self.check_if_valid_token(key)

        user_id = reset_request['user']
        user = superdesk.get_resource_service('users').find_one(req=None, _id=user_id)
        if not user.get('is_active'):
            logger.warning('Try to set password for an inactive user')
            raise SuperdeskApiError.forbiddenError('User not active')

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
