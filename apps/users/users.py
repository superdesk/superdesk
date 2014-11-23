"""Superdesk Users"""
from settings import LDAP_SERVER
from superdesk.resource import Resource


class RolesResource(Resource):
    schema = {
        'name': {
            'type': 'string',
            'iunique': True,
            'required': True,
        },
        'description': {
            'type': 'string'
        },
        'permissions': {
            'type': 'dict'
        },
        'is_default': {
            'type': 'boolean'
        }
    }
    datasource = {
        'default_sort': [('_created', -1)]
    }


class UsersResource(Resource):
    readonly = True if LDAP_SERVER else False

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
        'roles': {
            'type': 'list'
        },
        'preferences': {'type': 'dict'},
        'workspace': {
            'type': 'dict'
        },
        'user_type': {
            'type': 'string',
            'allowed': ['user', 'manager', 'administrator'],
            'default': 'administrator',
            'required': True
        },
        'is_active': {
            'type': 'boolean',
            'default': True
        },
        'needs_activation': {
            'type': 'boolean',
            'default': True
        }
    }

    extra_response_fields = [
        'display_name',
        'username',
        'email',
        'user_info',
        'picture_url',
        'avatar',
        'is_active',
        'needs_activation'
    ]

    datasource = {
        'projection': {
            'password': 0
        }
    }
