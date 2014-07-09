import superdesk
from flask import current_app as app


class BaseModel():
    '''
    Base model for all endpoints, defines the basic implementation
    for CRUD datalayer functionality.
    '''
    endpoint_name = str()
    url = str()
    item_url = str()
    additional_lookup = {}
    schema = {}
    item_methods = []
    resource_methods = []
    public_methods = []
    extra_response_fields = []
    embedded_fields = []
    datasource = {}
    versioning = False

    def __init__(self, app, endpoint_schema=None):

        if not endpoint_schema:
            endpoint_schema = {'schema': self.schema}
            if self.additional_lookup:
                endpoint_schema.update({'additional_lookup': self.additional_lookup})
            if self.extra_response_fields:
                endpoint_schema.update({'extra_response_fields': self.extra_response_fields})
            if self.datasource:
                endpoint_schema.update({'datasource': self.datasource})
            if self.item_methods:
                endpoint_schema.update({'item_methods': self.item_methods})
            if self.resource_methods:
                endpoint_schema.update({'resource_methods': self.resource_methods})
            if self.public_methods:
                endpoint_schema.update({'public_methods': self.public_methods})
            if self.url:
                endpoint_schema.update({'url': self.url})
            if self.item_url:
                endpoint_schema.update({'item_url': self.item_url})
            if self.embedded_fields:
                endpoint_schema.update({'embedded_fields': self.embedded_fields})
            if self.versioning:
                endpoint_schema.update({'versioning': self.versioning})

        on_insert_event = getattr(app, 'on_insert_%s' % self.endpoint_name)
        on_insert_event += self.on_create
        on_update_event = getattr(app, 'on_update_%s' % self.endpoint_name)
        on_update_event += self.on_update
        on_delete_event = getattr(app, 'on_delete_item_%s' % self.endpoint_name)
        on_delete_event += self.on_delete
        app.register_resource(self.endpoint_name, endpoint_schema)
        superdesk.apps[self.endpoint_name] = self

    def on_create(self, docs):
        pass

    def on_update(self, updates, original):
        pass

    def on_delete(self, doc):
        pass

    def find_one(self, req, **lookup):
        return app.data._backend(self.endpoint_name).find_one(self.endpoint_name, req=req, **lookup)

    def get(self, req, lookup):
        backend = app.data._search_backend(self.endpoint_name)
        if backend is None:
            backend = app.data._backend(self.endpoint_name)
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
        ids = app.data._backend(self.endpoint_name).insert(self.endpoint_name, docs, **kwargs)
        search_backend = app.data._search_backend(self.endpoint_name)
        if search_backend:
            for _id in ids:
                inserted = self.find_one(req=None, _id=_id)
                search_backend.insert(self.endpoint_name, [inserted], **kwargs)
        return ids

    def update(self, id, updates, trigger_events=None):
        if trigger_events:
            original = self.find_one(req=None, _id=id)
            self.on_update(updates, original)

        res = app.data._backend(self.endpoint_name).update(self.endpoint_name, id, updates)

        search_backend = app.data._search_backend(self.endpoint_name)
        if search_backend is not None:
            all_updates = self.find_one(req=None, _id=id)
            search_backend.update(self.endpoint_name, id, all_updates)
        return res

    def delete(self, lookup, trigger_events=None):
        if trigger_events:
            doc = self.find_one(req=None, lookup=lookup)
            self.on_delete(doc)
        res = app.data._backend(self.endpoint_name).remove(self.endpoint_name, lookup)
        search_backend = app.data._search_backend(self.endpoint_name)
        if search_backend is not None:
            try:
                search_backend.remove(self.endpoint_name, lookup)
            except ValueError:
                pass
        return res
