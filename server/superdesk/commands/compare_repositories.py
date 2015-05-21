# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013 - 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import superdesk
from eve.utils import ParsedRequest
import json

class CompareRepositories(superdesk.Command):
    """
    Index the specified mongo collection in the specified elastic collection/type.
    This will use the default APP mongo DB to read the data and the default Elastic APP index.
    """

    default_page_size = 500
    mongo_collection_name = 'archive'

    def run(self):
        bucket_size = self.default_page_size
        print('Indexing data from mongo/{} to elastic/{}'.format(self.mongo_collection_name, self.mongo_collection_name))

        service = superdesk.get_resource_service(self.mongo_collection_name)
        cursor = service.get_from_mongo(None, {})
        count = cursor.count()
        elastic_cursor = service.get(None, {})
        elastic_ = elastic_cursor.count()
        #mongo_items = list(cursor)
        mongo_dict = {mongo_item['_id']:mongo_item['_etag'] for mongo_item in cursor}

        #ids = [item['_id'] for item in mongo_items]
        ids = list(mongo_dict.keys())

        query = {'query': {'filtered': {'filter': {'ids': {'values': ids}}}}}
        request = ParsedRequest()
        request.args = {'source': json.dumps(query)}
        elastic_items = superdesk.app.data._search_backend(self.mongo_collection_name).find(self.mongo_collection_name, request, None)

        elastic_dict = {elastic_item['_id']: elastic_item['_etag'] for elastic_item in elastic_items}

        shared_items = set(mongo_dict.items()) & set(elastic_dict.items())
        print(len(shared_items))

        # for x in range(0, no_of_buckets):
        #     skip = x * bucket_size
        #     print('Page : {}, skip: {}'.format(x + 1, skip))
        #     cursor = service.get_from_mongo(None, {})
        #     cursor.skip(skip)
        #     cursor.limit(bucket_size)
        #     mongo_items = list(cursor)
        #     ids = [item['_id'] for item in mongo_items]
        #     print('Inserting {} items'.format(len(mongo_items)))
        #     query = {'query': {'filtered': {'filter': {'ids': {'values': ids}}}}}
        #     request = ParsedRequest()
        #     request.args = {'source': json.dumps(query)}
        #     elastic_items = superdesk.app.data._search_backend(self.mongo_collection_name).find(self.mongo_collection_name, request, None)

        return 'Finished indexing collection {}'.format(self.mongo_collection_name)


superdesk.command('app:index_from_mongo', CompareRepositories())
