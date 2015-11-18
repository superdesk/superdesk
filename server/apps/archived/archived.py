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

from apps.publish.published_item import PublishedItemResource, PublishedItemService
from superdesk.metadata.utils import aggregations
from superdesk.notification import push_notification
from apps.archive.common import get_user
import superdesk
from superdesk.utc import utcnow

query_filters = [{'allow_post_publish_actions': False}, {'can_be_removed': False}]


class ArchivedResource(PublishedItemResource):
    datasource = {
        'source': 'published',
        'search_backend': 'elastic',
        'aggregations': aggregations,
        'elastic_filter': {'and': [{'term': query_filters[0]}, {'term': query_filters[1]}]},
        'default_sort': [('_updated', -1)],
        'projection': {
            'old_version': 0,
            'last_version': 0
        }
    }

    resource_methods = ['GET']
    item_methods = ['GET', 'DELETE']

    privileges = {'DELETE': 'archived'}


class ArchivedService(PublishedItemService):

    def find_by_item_ids(self, item_ids):
        """
        Fetches items whose item_id is passed in item_ids

        :param item_ids: list of item_id
        :return: items from archived collection
        """

        query = {'$and': [{'item_id': {'$in': item_ids}}, query_filters[0], query_filters[1]]}
        return super().get_from_mongo(req=None, lookup=query)

    def on_delete(self, doc):
        """
        This method throws exception when invoked on PublishedItemService. Overriding to avoid that.
        """

        pass

    def delete(self, lookup):
        super().patch(lookup[config.ID_FIELD], {'can_be_removed': True, '_updated': utcnow()})

    def on_deleted(self, doc):
        user = get_user()
        push_notification('item:deleted:archived', item=str(doc[config.ID_FIELD]), user=str(user.get(config.ID_FIELD)))


superdesk.privilege(name='archived', label='Archived Management', description='User can remove items from the archived')
