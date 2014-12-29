from flask import g, current_app as app
from eve.validation import ValidationError
from eve.utils import parse_request, document_etag

import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend
from superdesk import get_resource_service
from superdesk.utils import last_updated
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

    superdesk.intrinsic_privilege(resource_name=endpoint_name, method=['PATCH'])


class PreferencesResource(Resource):
    datasource = {'source': 'auth', 'projection': {'session_preferences': 1, 'user': 1}}
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

    superdesk.register_default_session_preference('scratchpad:items', [])
    superdesk.register_default_session_preference('desk:items', [])
    superdesk.register_default_session_preference('stage:items', [])
    superdesk.register_default_session_preference('pinned:items', [])


class PreferencesService(BaseService):

    def on_update(self, updates, original):
        existing_prefs = self.find_one(req=None, _id=original['_id'])
        existing_user_preferences = existing_prefs.get(_user_preferences_key, {})
        existing_session_preferences = existing_prefs.get(_session_preferences_key, {})

        self.partial_update(updates, existing_user_preferences, superdesk.default_user_preferences,
                            _user_preferences_key)
        self.partial_update(updates, existing_session_preferences, superdesk.default_session_preferences,
                            _session_preferences_key)

    def partial_update(self, updates, existing_preferences, default_preferences, key):
        if updates.get(key) is not None:
            prefs = updates.get(key, {})

            # check if the input is validated against the default values
            for k in ((k for k, v in prefs.items() if k not in default_preferences)):
                raise ValidationError('Invalid preference: %s' % k)

            if key == _user_preferences_key:
                for k in existing_preferences.keys():
                    updates[key][k] = dict(list(existing_preferences.get(k, {}).items())
                                           + list(prefs.get(k, {}).items()))
            else:
                for k in existing_preferences.keys():
                    if prefs.get(k, []) == []:
                        updates[key][k] = existing_preferences.get(k, [])

    def find_one(self, req, **lookup):
        session_doc = super().find_one(req, **lookup)
        user_doc = get_resource_service('users').find_one(req=None, _id=session_doc['user'])
        self.enhance_document_with_default_prefs(session_doc, user_doc)
        self.enhance_document_with_user_privileges(session_doc, user_doc)
        session_doc[_action_key] = get_privileged_actions(session_doc[_privileges_key])
        if req is None:
            req = parse_request('auth')
            session_doc['_etag'] = req.if_match
        else:
            session_doc['_etag'] = document_etag(session_doc)
        return session_doc

    def get(self, req, lookup):
        docs = super().get(req, lookup)
        for doc in docs:
            self.enhance_document_with_default_prefs(doc)
        return docs

    def enhance_document_with_default_prefs(self, session_doc, user_doc):
        orig_user_prefs = user_doc.get(_preferences_key, {})
        available = dict(superdesk.default_user_preferences)
        available.update(orig_user_prefs)
        session_doc[_user_preferences_key] = available

        orig_session_prefs = session_doc.get(_session_preferences_key, {})
        available = dict(superdesk.default_session_preferences)
        available.update(orig_session_prefs)
        session_doc[_session_preferences_key] = available

    def enhance_document_with_user_privileges(self, session_doc, user_doc):
        role_doc = get_resource_service('users').get_role(user_doc)
        get_resource_service('users').set_privileges(user_doc, role_doc)
        session_doc[_privileges_key] = user_doc.get(_privileges_key, {})
        # set last_updated to max for session/user/role so that client will fetch changes
        # after a change to any of those
        session_doc[app.config['LAST_UPDATED']] = last_updated(session_doc, user_doc, role_doc)

    def enhance_document_with_default_user_prefs(self, user_doc):
        orig_user_prefs = user_doc.get(_preferences_key, {})
        available = dict(superdesk.default_user_preferences)
        available.update(orig_user_prefs)
        user_doc[_user_preferences_key] = available

    def get_user_preference(self, user_id):
        """
        This function returns preferences for the user.
        """
        doc = get_resource_service('users').find_one(req=None, _id=user_id)
        self.enhance_document_with_default_user_prefs(user_doc=doc)
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

    def update(self, id, updates):

        if updates.get(_user_preferences_key) is not None:
            # update User
            user_doc = get_resource_service('auth').find_one(req=None, _id=id)
            user_preference = {}
            user_preference['preferences'] = updates.get('user_preferences')
            get_resource_service('users').update(user_doc['user'], user_preference)
            del updates[_user_preferences_key]

        res = self.backend.update(self.datasource, id, updates)
        return res

    def is_authorized(self, **kwargs):
        """
        Returns False if logged-in user is trying to update other user's or session's privileges.

        :param kwargs:
        :return: True if authorized, False otherwise
        """

        if kwargs.get("user_id") is None:
            return False

        session = self.find_one(_id=kwargs.get("user_id"), req=None)
        return str(g.user['_id']) == str(session.get("user"))
