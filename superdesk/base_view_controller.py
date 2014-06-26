import superdesk


class BaseViewController():
    '''
    Base controller for all endpoints, defines the basic implementation
    for GET/POST/PATCH/DELETE datalayer functionality.
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

    def __init__(self, app, endpoint_schema=None):
        if not app:
            from flask import current_app as app

        self.app = app

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

        app.register_resource(self.endpoint_name, endpoint_schema)
        superdesk.apps[self.endpoint_name] = self

    def find_one(self, req=None, **lookup):
        return self.app.data._backend(self.endpoint_name).find_one(self.endpoint_name, req, **lookup)

    def get(self, req, lookup):
        cursor = self.app.data._backend(self.endpoint_name).find(self.endpoint_name, req, lookup)
        if not cursor.count():
            return cursor  # return 304 if not modified
        else:
            # but fetch without filter if there is a change
            req.if_modified_since = None
            return self.app.data._backend(self.endpoint_name).find(self.endpoint_name, req, lookup)

    def post(self, docs, **kwargs):
        return self.app.data._backend(self.endpoint_name).insert(self.endpoint_name, docs, **kwargs)

    def patch(self, id, updates):
        return self.app.data._backend(self.endpoint_name).update(self.endpoint_name, id, updates)

    def delete(self, lookup):
        return self.app.data._backend(self.endpoint_name).remove(self.endpoint_name, lookup)
