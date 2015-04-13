# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

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
        'privileges': {
            'type': 'dict'
        },
        'is_default': {
            'type': 'boolean'
        },
    }
    datasource = {
        'default_sort': [('_created', -1)]
    }
    privileges = {'POST': 'roles', 'DELETE': 'roles', 'PATCH': 'roles'}


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
        'role': Resource.rel('roles', True),
        'privileges': {'type': 'dict'},
        'workspace': {
            'type': 'dict'
        },
        'user_type': {
            'type': 'string',
            'allowed': ['user', 'administrator'],
            'default': 'user'
        },
        'is_active': {
            'type': 'boolean',
            'default': True
        },
        'is_enabled': {
            'type': 'boolean',
            'default': True
        },
        'needs_activation': {
            'type': 'boolean',
            'default': True
        },
        'desk': Resource.rel('desks'),  # Default desk of the user, which would be selected when logged-in.
        # Used for putting a sign-off on published content
        'sign_off': {
            'type': 'string',
            'required': True
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
        'is_enabled',
        'needs_activation',
        'desk'
    ]

    etag_ignore_fields = ['session_preferences', '_etag']

    datasource = {
        'projection': {
            'password': 0
        }
    }

    privileges = {'POST': 'users', 'DELETE': 'users', 'PATCH': 'users'}
