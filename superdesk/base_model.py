
import logging
from flask import current_app as app
import superdesk
from eve.utils import config


log = logging.getLogger(__name__)


def build_custom_hateoas(hateoas, doc, **values):
    values.update(doc)
    links = doc.get(config.LINKS)
    if not links:
        links = {}
        doc[config.LINKS] = links

    for link_name in hateoas.keys():
        link = hateoas[link_name]
        link = {'title': link['title'], 'href': link['href']}
        link['href'] = link['href'].format(**values)
        links[link_name] = link


class BaseModel():
    '''
    Base model for all endpoints, defines the basic implementation
    for CRUD datalayer functionality.
    '''
    endpoint_name = None
    url = None
    item_url = None
    additional_lookup = None
    schema = {}
    item_methods = None
    resource_methods = None
    public_methods = None
    extra_response_fields = None
    embedded_fields = None
    datasource = None
    versioning = None
    internal_resource = None
    resource_title = None

    def __init__(self, app, endpoint_schema=None):
        if not endpoint_schema:
            endpoint_schema = {'schema': self.schema}
            if self.additional_lookup is not None:
                endpoint_schema.update({'additional_lookup': self.additional_lookup})
            if self.extra_response_fields is not None:
                endpoint_schema.update({'extra_response_fields': self.extra_response_fields})
            if self.datasource is not None:
                endpoint_schema.update({'datasource': self.datasource})
            if self.item_methods is not None:
                endpoint_schema.update({'item_methods': self.item_methods})
            if self.resource_methods is not None:
                endpoint_schema.update({'resource_methods': self.resource_methods})
            if self.public_methods is not None:
                endpoint_schema.update({'public_methods': self.public_methods})
            if self.url is not None:
                endpoint_schema.update({'url': self.url})
            if self.item_url is not None:
                endpoint_schema.update({'item_url': self.item_url})
            if self.embedded_fields is not None:
                endpoint_schema.update({'embedded_fields': self.embedded_fields})
            if self.versioning is not None:
                endpoint_schema.update({'versioning': self.versioning})
            if self.internal_resource is not None:
                endpoint_schema.update({'internal_resource': self.internal_resource})
            if self.resource_title is not None:
                endpoint_schema.update({'resource_title': self.resource_title})

        on_insert_event = getattr(app, 'on_insert_%s' % self.endpoint_name)
        on_insert_event += self.on_create
        on_inserted_event = getattr(app, 'on_inserted_%s' % self.endpoint_name)
        on_inserted_event += self.on_created
        on_update_event = getattr(app, 'on_update_%s' % self.endpoint_name)
        on_update_event += self.on_update
        on_updated_event = getattr(app, 'on_updated_%s' % self.endpoint_name)
        on_updated_event += self.on_updated
        on_delete_event = getattr(app, 'on_delete_item_%s' % self.endpoint_name)
        on_delete_event += self.on_delete
        on_deleted_event = getattr(app, 'on_deleted_item_%s' % self.endpoint_name)
        on_deleted_event += self.on_deleted
        app.register_resource(self.endpoint_name, endpoint_schema)
        superdesk.apps[self.endpoint_name] = self

    def on_create(self, docs):
        pass

    def on_created(self, docs):
        pass

    def on_update(self, updates, original):
        pass

    def on_updated(self, updates, original):
        pass

    def on_replace(self, document, original):
        pass

    def on_replaced(self, document, original):
        pass

    def on_delete(self, doc):
        pass

    def on_deleted(self, doc):
        pass

    def find_one(self, req, **lookup):
        backend = self._lookup_backend(fallback=True)
        return backend.find_one(self.endpoint_name, req=req, **lookup)

    def get(self, req, lookup):
        backend = self._lookup_backend(fallback=True)
        cursor = backend.find(self.endpoint_name, req, lookup)
        if not cursor.count():
            return cursor  # return 304 if not modified
        else:
            # but fetch without filter if there is a change
            req.if_modified_since = None
            return backend.find(self.endpoint_name, req, lookup)

    def create(self, docs, trigger_events=None, **kwargs):
        if trigger_events:
            self.on_create(docs)
        backend = self._backend()
        ids = backend.insert(self.endpoint_name, docs, **kwargs)
        search_backend = self._lookup_backend()
        if search_backend:
            search_backend.insert(self.endpoint_name, docs, **kwargs)
        if trigger_events:
            self.on_created(docs)
        return ids

    def update(self, id, updates, trigger_events=None):
        if trigger_events:
            original = self.find_one(req=None, _id=id)
            self.on_update(updates, original)

        backend = self._backend()
        res = backend.update(self.endpoint_name, id, updates)
        search_backend = self._lookup_backend()
        if search_backend is not None:
            all_updates = backend.find_one(self.endpoint_name, req=None, _id=id)
            search_backend.update(self.endpoint_name, id, all_updates)
        if trigger_events:
            self.on_updated(updates, original)
        return res

    def replace(self, id, document, trigger_events=None):
        if trigger_events:
            original = self.find_one(req=None, _id=id)
            self.on_replace(document, original)

        backend = self._backend()
        res = backend.replace(self.endpoint_name, id, document)

        search_backend = self._lookup_backend()
        if search_backend is not None:
            search_backend.update(self.endpoint_name, id, document)
        if trigger_events:
            self.on_replaced(document, original)
        return res

    def delete(self, lookup, trigger_events=None):
        if trigger_events:
            doc = self.find_one(req=None, lookup=lookup)
            self.on_delete(doc)
        backend = self._backend()
        res = backend.remove(self.endpoint_name, lookup)
        search_backend = self._lookup_backend()
        if search_backend is not None:
            try:
                search_backend.remove(self.endpoint_name, lookup)
            except ValueError:
                pass
        if trigger_events:
            self.on_deleted(doc)
        return res

    @staticmethod
    def rel(resource, embeddable=False, required=False, type='objectid'):
        return {
            'type': type,
            'required': required,
            'data_relation': {'resource': resource, 'field': '_id', 'embeddable': embeddable}
        }

    def _datasource(self):
        return app.data._datasource(self.endpoint_name)[0]

    def _backend(self):
        return app.data._backend(self.endpoint_name)

    def _lookup_backend(self, fallback=False):
        backend = app.data._search_backend(self.endpoint_name)
        if backend is None and fallback:
            backend = app.data._backend(self.endpoint_name)
        return backend
