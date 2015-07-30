# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


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
    public_item_methods = None
    extra_response_fields = None
    embedded_fields = None
    datasource = None
    versioning = None
    internal_resource = None
    resource_title = None
    service = None
    endpoint_schema = None
    resource_preferences = None
    etag_ignore_fields = []
    mongo_prefix = None
    auth_field = None

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
            if self.public_item_methods is not None:
                endpoint_schema.update({'public_item_methods': self.public_item_methods})
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
            if self.etag_ignore_fields:
                endpoint_schema.update({'etag_ignore_fields': self.etag_ignore_fields})
            if self.mongo_prefix:
                endpoint_schema.update({'mongo_prefix': self.mongo_prefix})
            if self.auth_field:
                endpoint_schema.update({'auth_field': self.auth_field})

        self.endpoint_schema = endpoint_schema

        on_fetched_resource = getattr(app, 'on_fetched_resource_%s' % self.endpoint_name)
        on_fetched_resource -= service.on_fetched
        on_fetched_resource += service.on_fetched

        on_fetched_item = getattr(app, 'on_fetched_item_%s' % self.endpoint_name)
        on_fetched_item -= service.on_fetched_item
        on_fetched_item += service.on_fetched_item

        on_insert_event = getattr(app, 'on_insert_%s' % self.endpoint_name)
        on_insert_event -= service.on_create
        on_insert_event += service.on_create

        on_inserted_event = getattr(app, 'on_inserted_%s' % self.endpoint_name)
        on_inserted_event -= service.on_created
        on_inserted_event += service.on_created

        on_update_event = getattr(app, 'on_update_%s' % self.endpoint_name)
        on_update_event -= service.on_update
        on_update_event += service.on_update

        on_updated_event = getattr(app, 'on_updated_%s' % self.endpoint_name)
        on_updated_event -= service.on_updated
        on_updated_event += service.on_updated

        on_delete_event = getattr(app, 'on_delete_item_%s' % self.endpoint_name)
        on_delete_event -= service.on_delete
        on_delete_event += service.on_delete

        on_deleted_event = getattr(app, 'on_deleted_item_%s' % self.endpoint_name)
        on_deleted_event -= service.on_deleted
        on_deleted_event += service.on_deleted

        app.register_resource(self.endpoint_name, endpoint_schema)
        superdesk.resources[self.endpoint_name] = self

    @staticmethod
    def rel(resource, embeddable=True, required=False, type='objectid', nullable=False):
        return {
            'type': type,
            'required': required,
            'nullable': nullable,
            'data_relation': {'resource': resource, 'field': '_id', 'embeddable': embeddable}
        }
