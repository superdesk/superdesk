# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

from eve.utils import config
import logging
from apps.publish.published_item import published_item_fields
from apps.packages import PackageService
from superdesk.metadata.utils import aggregations
from superdesk.metadata.item import CONTENT_TYPE, ITEM_TYPE, not_analyzed
from superdesk.metadata.packages import PACKAGE_TYPE, TAKES_PACKAGE, RESIDREF, SEQUENCE
from superdesk.notification import push_notification
from apps.archive.common import get_user, item_schema
import superdesk
from superdesk.services import BaseService
from superdesk.resource import Resource

logger = logging.getLogger(__name__)


class ArchivedResource(Resource):
    datasource = {
        'search_backend': 'elastic',
        'aggregations': aggregations,
        'default_sort': [('_updated', -1)],
        'projection': {
            'old_version': 0,
            'last_version': 0
        }
    }

    mongo_prefix = 'ARCHIVED'

    extra_fields = published_item_fields.copy()
    # item_id + _current_version will be used fetch archived item.
    extra_fields['archived_id'] = {
        'type': 'string',
        'mapping': not_analyzed
    }

    schema = item_schema(extra_fields)
    resource_methods = ['GET']
    item_methods = ['GET', 'DELETE']
    privileges = {'DELETE': 'archived'}

    additional_lookup = {
        'url': 'regex("[\w,.:-]+")',
        'field': 'archived_id'
    }


class ArchivedService(BaseService):

    def on_create(self, docs):
        package_service = PackageService()

        for doc in docs:
            doc.pop('lock_user', None)
            doc.pop('lock_time', None)
            doc.pop('lock_session', None)
            doc['archived_id'] = self._get_archived_id(doc.get('item_id'), doc.get(config.VERSION))

            if doc.get(ITEM_TYPE) == CONTENT_TYPE.COMPOSITE:
                is_takes_package = doc.get(PACKAGE_TYPE) == TAKES_PACKAGE
                for ref in package_service.get_item_refs(doc):
                    ref['location'] = 'archived'

                    if is_takes_package and not ref.get('is_published'):
                        # if take is not published
                        package_service.remove_ref_from_inmem_package(doc, ref.get(RESIDREF))

                if is_takes_package:
                    doc[SEQUENCE] = len(package_service.get_item_refs(doc))

    def on_deleted(self, doc):
        user = get_user()
        push_notification('item:deleted:archived', item=str(doc[config.ID_FIELD]), user=str(user.get(config.ID_FIELD)))

    def on_fetched_item(self, doc):
        doc['_type'] = 'archived'

    def _get_archived_id(self, item_id, version):
        return '{}:{}'.format(item_id, version)


superdesk.privilege(name='archived', label='Archived Management', description='User can remove items from the archived')
