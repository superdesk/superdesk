
import logging
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


class Resource():
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
    service = None
    endpoint_schema = None
    resource_preferences = None

    def __init__(self, endpoint_name, app, service, endpoint_schema=None):
        self.endpoint_name = endpoint_name
        self.service = service
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
        self.endpoint_schema = endpoint_schema
        app.register_resource(self.endpoint_name, endpoint_schema)
        superdesk.resources[self.endpoint_name] = self
        if self.resource_preferences is not None:
            self.resource_preferences.update({'resource_name': self.endpoint_name})
            superdesk.resource_preferences.append(self.resource_preferences)

    @staticmethod
    def rel(resource, embeddable=True, required=False, type='objectid'):
        return {
            'type': type,
            'required': required,
            'data_relation': {'resource': resource, 'field': '_id', 'embeddable': embeddable}
        }
