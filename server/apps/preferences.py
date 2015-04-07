# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from flask import g, request
from eve.validation import ValidationError

import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend
from superdesk import get_resource_service
from superdesk.workflow import get_privileged_actions


_preferences_key = 'preferences'
_user_preferences_key = 'user_preferences'
_session_preferences_key = 'session_preferences'
_privileges_key = 'active_privileges'
_action_key = 'allowed_actions'


def init_app(app):
    endpoint_name = 'preferences'
    service = PreferencesService(endpoint_name, backend=get_backend())
    PreferencesResource(endpoint_name, app=app, service=service)
    app.on_session_end -= service.on_session_end
    app.on_session_end += service.on_session_end

    superdesk.intrinsic_privilege(resource_name=endpoint_name, method=['PATCH'])


class PreferencesResource(Resource):
    datasource = {
        'source': 'users',
        'projection': {
            _session_preferences_key: 1,
            _user_preferences_key: 1,
            _privileges_key: 1,
            _action_key: 1,
            '_etag': 1
        }
    }
    schema = {
        _session_preferences_key: {'type': 'dict', 'required': True},
        _user_preferences_key: {'type': 'dict', 'required': True},
        _privileges_key: {'type': 'dict'},
        _action_key: {'type': 'list'}
    }
    resource_methods = []
    item_methods = ['GET', 'PATCH']

    superdesk.register_default_user_preference('feature:preview', {
        'type': 'bool',
        'enabled': False,
        'default': False,
        'label': 'Enable Feature Preview',
        'category': 'feature'
    })

    superdesk.register_default_user_preference('archive:view', {
        'type': 'string',
        'allowed': ['mgrid', 'compact'],
        'view': 'mgrid',
        'default': 'mgrid',
        'label': 'Users archive view format',
        'category': 'archive'
    })

    superdesk.register_default_user_preference('editor:theme', {
        'type': 'string',
        'theme': '',
        'label': 'Users article edit screen editor theme',
        'category': 'editor'
    })

    superdesk.register_default_user_preference('workqueue:items', {
        'items': []
    })

    superdesk.register_default_user_preference('dashboard:ingest', {
        'providers': []
    })

    superdesk.register_default_user_preference('agg:view', {
        'active': {},
    })

    superdesk.register_default_session_preference('scratchpad:items', [])
    superdesk.register_default_session_preference('desk:last_worked', '')
    superdesk.register_default_session_preference('desk:items', [])
    superdesk.register_default_session_preference('stage:items', [])
    superdesk.register_default_session_preference('pinned:items', [])


class PreferencesService(BaseService):

    def on_session_end(self, user_id, session_id):
        service = get_resource_service('users')
        user_doc = service.find_one(req=None, _id=user_id)
        session_prefs = user_doc.get(_session_preferences_key, {}).copy()

        if not isinstance(session_id, str):
            session_id = str(session_id)

        if session_id in session_prefs:
            del session_prefs[session_id]
            service.patch(user_id, {_session_preferences_key: session_prefs})

    def set_session_based_prefs(self, session_id, user_id):
        user_doc = get_resource_service('users').find_one(req=None, _id=user_id)
        updates = {}
        if _user_preferences_key not in user_doc:
            orig_user_prefs = user_doc.get(_preferences_key, {})
            available = dict(superdesk.default_user_preferences)
            available.update(orig_user_prefs)
            updates[_user_preferences_key] = available

        session_prefs = user_doc.get(_session_preferences_key, {})
        available = dict(superdesk.default_session_preferences)
        if available.get('desk:last_worked') == '' and user_doc.get('desk'):
            available['desk:last_worked'] = user_doc.get('desk')

        session_prefs.setdefault(str(session_id), available)
        updates[_session_preferences_key] = session_prefs

        self.backend.update(self.datasource, user_id, updates, user_doc)

    def set_user_initial_prefs(self, user_doc):
        if _user_preferences_key not in user_doc:
            orig_user_prefs = user_doc.get(_preferences_key, {})
            available = dict(superdesk.default_user_preferences)
            available.update(orig_user_prefs)
            user_doc[_user_preferences_key] = available

    def find_one(self, req, **lookup):
        session = get_resource_service('sessions').find_one(req=None, _id=lookup['_id'])
        _id = session['user'] if session else lookup['_id']
        doc = get_resource_service('users').find_one(req, _id=_id)
        if doc:
            doc['_id'] = session['_id'] if session else _id
        return doc

    def on_fetched_item(self, doc):
        session_id = request.view_args['_id']
        session_prefs = doc.get(_session_preferences_key, {}).get(session_id, {})
        doc[_session_preferences_key] = session_prefs

        self.enhance_document_with_user_privileges(doc)

    def on_update(self, updates, original):
        # Beware, dragons ahead
        existing_user_preferences = original.get(_user_preferences_key, {}).copy()
        existing_session_preferences = original.get(_session_preferences_key, {}).copy()

        self.update_user_prefs(updates, existing_user_preferences)
        session_id = request.view_args['_id']
        self.update_session_prefs(updates, existing_session_preferences, session_id)

    def update_session_prefs(self, updates, existing_session_preferences, session_id):
        session_prefs = updates.get(_session_preferences_key)
        if session_prefs is not None:
            for k in (k for k, v in session_prefs.items() if k not in superdesk.default_session_preferences):
                raise ValidationError('Invalid preference: %s' % k)

            existing = existing_session_preferences.get(session_id, {})
            existing.update(session_prefs)
            existing_session_preferences[session_id] = existing
            updates[_session_preferences_key] = existing_session_preferences

    def update_user_prefs(self, updates, existing_user_preferences):
        user_prefs = updates.get(_user_preferences_key)
        if user_prefs is not None:
            # check if the input is validated against the default values
            for k in ((k for k, v in user_prefs.items() if k not in superdesk.default_user_preferences)):
                raise ValidationError('Invalid preference: %s' % k)

            existing_user_preferences.update(user_prefs)
            updates[_user_preferences_key] = existing_user_preferences

    def update(self, id, updates, original):
        session = get_resource_service('sessions').find_one(req=None, _id=original['_id'])
        original_unpatched = self.backend.find_one(self.datasource, req=None, _id=session['user'])
        updated = original_unpatched.copy()
        updated.update(updates)
        del updated['_id']
        res = self.backend.update(self.datasource, original_unpatched['_id'], updated, original_unpatched)
        updates.update(updated)
        # Return only the patched session prefs
        session_prefs = updates.get(_session_preferences_key, {}).get(str(original['_id']), {})
        updates[_session_preferences_key] = session_prefs
        self.enhance_document_with_user_privileges(updates)
        return res

    def enhance_document_with_default_prefs(self, session_doc, user_doc):
        orig_user_prefs = user_doc.get(_preferences_key, {})
        available = dict(superdesk.default_user_preferences)
        available.update(orig_user_prefs)
        session_doc[_user_preferences_key] = available

        orig_session_prefs = session_doc.get(_session_preferences_key, {})
        available = dict(superdesk.default_session_preferences)
        available.update(orig_session_prefs)

        if available.get('desk:last_worked') == '' and user_doc.get('desk'):
            available['desk:last_worked'] = user_doc.get('desk')

        session_doc[_session_preferences_key] = available

    def enhance_document_with_user_privileges(self, user_doc):
        role_doc = get_resource_service('users').get_role(user_doc)
        get_resource_service('users').set_privileges(user_doc, role_doc)
        user_doc[_action_key] = get_privileged_actions(user_doc[_privileges_key])

    def get_user_preference(self, user_id):
        """
        This function returns preferences for the user.
        """
        doc = get_resource_service('users').find_one(req=None, _id=user_id)
        prefs = doc.get(_user_preferences_key, {})
        return prefs

    def email_notification_is_enabled(self, user_id=None, preferences=None):
        """
        This function checks if email notification is enabled or not based on the preferences.
        """
        if user_id:
            preferences = self.get_user_preference(user_id)
        send_email = preferences.get('email:notification', {}) if isinstance(preferences, dict) else {}
        return send_email and send_email.get('enabled', False)

    def is_authorized(self, **kwargs):
        """
        Returns False if logged-in user is trying to update other user's or session's privileges.

        :param kwargs:
        :return: True if authorized, False otherwise
        """

        if kwargs.get("user_id") is None:
            return False

        session = get_resource_service('sessions').find_one(req=None, _id=kwargs.get('user_id'))
        if not session:
            return False
        authorized = str(g.user['_id']) == str(session.get("user"))
        return authorized
