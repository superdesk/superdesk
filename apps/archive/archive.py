from superdesk.models import BaseModel
from .common import base_schema, extra_response_fields, item_url, facets
from .common import on_create_item, on_create_media_archive, on_update_media_archive, on_delete_media_archive
from .common import get_user
from flask import current_app as app
from werkzeug.exceptions import NotFound
from superdesk.utc import utcnow
from eve.versioning import resolve_document_version
import superdesk
from apps.activity import add_activity


def get_subject(doc1, doc2=None):
    for key in ('headline', 'subject', 'slugline'):
        value = doc1.get(key)
        if not value and doc2:
            value = doc2.get(key)
        if value:
            return value


class ArchiveVersionsModel(BaseModel):
    endpoint_name = 'archive_versions'
    schema = base_schema
    extra_response_fields = extra_response_fields
    item_url = item_url
    resource_methods = []
    internal_resource = True

    def on_create(self, docs):
        for doc in docs:
            doc['versioncreated'] = utcnow()


class ArchiveModel(BaseModel):
    endpoint_name = 'archive'
    schema = {
        'old_version': {
            'type': 'number',
        },
        'last_version': {
            'type': 'number',
        }
    }
    schema.update(base_schema)
    extra_response_fields = extra_response_fields
    item_url = item_url
    datasource = {
        'search_backend': 'elastic',
        'facets': facets,
        'projection': {
            'old_version': 0,
            'last_version': 0
        },
        'default_sort': [('_updated', -1)],
    }
    resource_methods = ['GET', 'POST', 'DELETE']
    versioning = True

    def on_create(self, docs):
        on_create_item(docs)

    def on_created(self, docs):
        on_create_media_archive()
        for doc in docs:
            add_activity('added new item {{ type }} about {{ subject }}',
                         type=doc['type'], subject=get_subject(doc))

    def on_update(self, updates, original):
        user = get_user()
        lock_user = original.get('lock_user', None)
        if lock_user and str(lock_user) != str(user['_id']):
            raise superdesk.SuperdeskError(payload='The item was locked by another user')
        updates['versioncreated'] = utcnow()
        updates['version_creator'] = str(user.get('_id'))

    def on_updated(self, updates, original):
        on_update_media_archive()

        if '_version' in updates:
            add_activity('created new version {{ version }} for item {{ type }} about {{ subject }}',
                         version=updates['_version'], subject=get_subject(updates, original))

    def on_replaced(self, document, original):
        on_update_media_archive()

    def on_delete(self, doc):
        '''Delete associated binary files.'''
        if doc and doc.get('renditions'):
            for _name, ref in doc['renditions'].items():
                try:
                    app.media.delete(ref['media'])
                except (KeyError, NotFound):
                    pass

    def on_deleted(self, doc):
        on_delete_media_archive()
        add_activity('removed item {{ type }} about {{ subject }}',
                     type=doc['type'], subject=get_subject(doc))

    def replace(self, id, document, trigger_events=None):
        return self.restore_version(id, document) or \
            super().replace(id, document, trigger_events=trigger_events)

    def restore_version(self, id, doc):
        item_id = id
        old_version = int(doc.get('old_version', 0))
        last_version = int(doc.get('last_version', 0))
        if(not all([item_id, old_version, last_version])):
            return None

        old = app.data.find_one('archive_versions', req=None, _id_document=item_id, _version=old_version)
        if old is None:
            raise superdesk.SuperdeskError(payload='Invalid version %s' % old_version)

        curr = app.data.find_one('archive', req=None, _id=item_id)
        if curr is None:
            raise superdesk.SuperdeskError(payload='Invalid item id %s' % item_id)

        if curr['_version'] != last_version:
            raise superdesk.SuperdeskError(payload='Invalid last version %s' % last_version)
        old['_id'] = old['_id_document']
        old['_updated'] = old['versioncreated'] = utcnow()
        del old['_id_document']

        resolve_document_version(old, 'archive', 'PATCH', curr)
        res = super().replace(id=item_id, document=old, trigger_events=True)
        del doc['old_version']
        del doc['last_version']
        doc.update(old)
        return res


class AutoSaveModel(BaseModel):
    endpoint_name = 'autosave'
    resource_title = endpoint_name
    url = '{0}/<{1}:guid>/autosave'.format(ArchiveModel.endpoint_name, item_url)
    schema = {k: base_schema[k] for k in ('headline', 'byline', 'slugline', 'keywords', 'body_html', 'guid')}
    resource_methods = ['POST']
    item_methods = []
    datasource = {'source': 'archive'}

    def create(self, docs, **kwargs):
        doc = docs.pop()
        doc.pop('_created')
        guid = doc.pop('guid')
        return self.update(guid, doc)
