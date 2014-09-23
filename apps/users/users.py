"""Superdesk Users"""

import logging
import os
import superdesk
from superdesk.resource import Resource
from superdesk.activity import add_activity
from superdesk.services import BaseService
from superdesk.utils import is_hashed, get_hash
from flask import current_app as app


logger = logging.getLogger(__name__)


class EmptyUsernameException(Exception):
    def __str__(self):
        return """Username is empty"""


class ConflictUsernameException(Exception):
    def __str__(self):
        return "Username '%s' exists already" % self.args[0]


def get_display_name(user):
    if user.get('first_name') or user.get('last_name'):
        display_name = '%s %s' % (user.get('first_name'), user.get('last_name'))
        return display_name.strip()
    else:
        return user.get('username')


def on_read_users(data, docs):
    """Set default fields for users"""
    for doc in docs:
        doc.setdefault('display_name', get_display_name(doc))
        doc.pop('password', None)


superdesk.connect('read:users', on_read_users)
superdesk.connect('created:users', on_read_users)


class RolesResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'unique': True,
            'required': True,
        },
        'extends': {
            'type': 'objectid'
        },
        'permissions': {
            'type': 'dict'
        }
    }
    datasource = {
        'default_sort': [('_created', -1)]
    }


class UsersResource(Resource):
    readonly = False
    if 'LDAP_SERVER' in os.environ:
        readonly = True

    additional_lookup = {
        'url': 'regex("[\w]+")',
        'field': 'username'
    }

    schema = {
        'username': {
            'type': 'string',
            'unique': True,
            'required': True,
            'minlength': 1
        },
        'password': {
            'type': 'string',
            'minlength': 5,
            'readonly': readonly
        },
        'first_name': {
            'type': 'string',
            'readonly': readonly
        },
        'last_name': {
            'type': 'string',
            'readonly': readonly
        },
        'display_name': {
            'type': 'string',
            'readonly': readonly
        },
        'email': {
            'unique': True,
            'type': 'email',
            'required': True
        },
        'phone': {
            'type': 'phone_number',
            'readonly': readonly
        },
        'user_info': {
            'type': 'dict'
        },
        'picture_url': {
            'type': 'string',
        },
        'avatar': Resource.rel('upload', True),
        'role': Resource.rel('roles', True),
        'preferences': {'type': 'dict'},
        'workspace': {
            'type': 'dict'
        },
    }

    extra_response_fields = [
        'display_name',
        'username',
        'email',
        'user_info',
        'picture_url',
        'avatar',
    ]

    datasource = {
        'projection': {
            'password': 0,
            'preferences': 0
        }
    }


class UsersService(BaseService):
    readonly_fields = ['username', 'display_name', 'password', 'email',
                       'phone', 'first_name', 'last_name']

    def on_create(self, docs):
        for doc in docs:
            if doc.get('password', None) and not is_hashed(doc.get('password')):
                doc['password'] = get_hash(doc.get('password'), app.config.get('BCRYPT_GENSALT_WORK_FACTOR', 12))

    def on_created(self, docs):
        for doc in docs:
            add_activity('created user {{user}}', user=doc.get('display_name', doc.get('username')))

    def on_deleted(self, doc):
        add_activity('removed user {{user}}', user=doc.get('display_name', doc.get('username')))

    def on_fetched(self, doc):
        if 'LDAP_SERVER' in os.environ:
            for document in doc['_items']:
                document['readonly'] = UsersService.readonly_fields
