from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk import get_backend
from eve.validation import ValidationError
import superdesk


_preferences_key = 'preferences'


def init_app(app):
    endpoint_name = 'preferences'
    service = PreferencesService(endpoint_name, backend=get_backend())
    PreferencesResource(endpoint_name, app=app, service=service)


class PreferencesResource(Resource):
    datasource = {'source': 'users', 'projection': {'preferences': 1}}
    schema = {
        _preferences_key: {'type': 'dict', 'required': True}
    }
    resource_methods = []
    item_methods = ['GET', 'PATCH']


class PreferencesService(BaseService):

    def on_update(self, updates, original):
        prefs = updates.get(_preferences_key, {})
        for k in ((k for k, v in prefs.items() if k not in superdesk.available_preferences)):
            raise ValidationError('Invalid preference: %s' % k)

    def find_one(self, req, **lookup):
        doc = super().find_one(req, **lookup)
        self.enhance_document_with_default_prefs(doc)
        return doc

    def get(self, req, lookup):
        docs = super().get(req, lookup)
        for doc in docs:
            self.enhance_document_with_default_prefs(doc)
        return docs

    def enhance_document_with_default_prefs(self, doc):
        orig_prefs = doc.get(_preferences_key, {})
        available = dict(superdesk.available_preferences)
        available.update(orig_prefs)
        doc[_preferences_key] = available

    def get_user_preference(self, user_id, preference_name):
        doc = self.find_one(req=None, _id=user_id)
        prefs = doc.get(_preferences_key, {}).get(preference_name, {})
        return prefs
