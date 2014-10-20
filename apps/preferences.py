from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend
from eve.validation import ValidationError
import superdesk
from superdesk import get_resource_service


_preferences_key = 'preferences'
_user_preferences_key = 'user_preferences'
_session_preferences_key = 'session_preferences'


def init_app(app):
    endpoint_name = 'preferences'
    service = PreferencesService(endpoint_name, backend=get_backend())
    PreferencesResource(endpoint_name, app=app, service=service)


class PreferencesResource(Resource):
    datasource = {'source': 'auth', 'projection': {'session_preferences': 1, 'user': 1}}
    schema = {
        _session_preferences_key: {'type': 'dict', 'required': True},
        _user_preferences_key: {'type': 'dict', 'required': True}
    }
    resource_methods = []
    item_methods = ['GET', 'PATCH']

    superdesk.register_available_preference('feature:preview', {
        'type': 'bool',
        'enabled': False,
        'default': False,
        'label': 'Enable Feature Preview',
        'category': 'feature'
    })

    superdesk.register_available_preference('archive:view', {
        'type': 'string',
        'allowed': ['mgrid', 'compact'],
        'view': 'mgrid',
        'default': 'mgrid',
        'label': 'Users archive view format',
        'category': 'archive'
    })


class PreferencesService(BaseService):

    def on_update(self, updates, original):
        existing_prefs = get_resource_service('preferences').find_one(req=None, _id=original['_id'])
        existing_user_preferences = existing_prefs.get(_user_preferences_key, {})

        self.user_partial_update(updates, original, existing_user_preferences, _user_preferences_key)
        #self.partial_update(updates, original, existing_prefs.get(_session_preferences_key, {}), _session_preferences_key)

    def user_partial_update(self, updates, original, existing_prefs, key):
        if updates.get(key) is not None:
            prefs = updates.get(key, {})

            # check if the input is validated against the default values
            if key == _user_preferences_key:
                for k in ((k for k, v in prefs.items() if k not in superdesk.available_preferences)):
                    raise ValidationError('Invalid preference: %s' % k)

            # check if we have any existing values
            if existing_prefs == {}:
                # there's no existing so use the default for missing values
                for k in prefs.keys():
                    updates[key][k] = dict(list(superdesk.available_preferences[k].items()) + list(prefs[k].items()))
            else:
                # there's existing so use it for missing values
                for k in prefs.keys():
                    updates[key][k] = dict(list(existing_prefs[k].items()) + list(prefs[k].items()))


    def find_one(self, req, **lookup):
        session_doc = super().find_one(req, **lookup)
        user_doc = get_resource_service('users').find_one(req=None, _id=session_doc['user'])
        self.enhance_document_with_default_prefs(session_doc, user_doc)
        return session_doc

    def get(self, req, lookup):
        docs = super().get(req, lookup)
        for doc in docs:
            self.enhance_document_with_default_prefs(doc)
        return docs

    def enhance_document_with_default_prefs(self, session_doc, user_doc):
        orig_prefs = user_doc.get(_preferences_key, {})
        available = dict(superdesk.available_preferences)
        available.update(orig_prefs)
        session_doc[_user_preferences_key] = available

    def get_user_preference(self, user_id, preference_name):
        doc = self.find_one(req=None, _id=user_id)
        prefs = doc.get(_preferences_key, {}).get(preference_name, {})
        return prefs

    def email_notification_is_enabled(self, user_id):
        send_email = self.get_user_preference(user_id, 'email:notification')
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
