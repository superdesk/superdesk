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
import requests
from superdesk.utc import utcnow
from eve.utils import ParsedRequest
import json


class CompareRepositories(superdesk.Command):
    default_page_size = 500

    def get_mongo_items(self, consistency_record, resource_name):
        # get the records from mongo in chunks
        superdesk.resources['archive'].endpoint_schema['datasource']['projection'] = None
        service = superdesk.get_resource_service(resource_name)
        cursor = service.get_from_mongo(None, {})
        count = cursor.count()
        no_of_buckets = len(range(0, count, self.default_page_size))
        mongo_items = []
        updated_mongo_items = []
        request = ParsedRequest()
        request.projection = json.dumps({'_etag': 1, '_updated': 1})
        for x in range(0, no_of_buckets):
            skip = x * self.default_page_size
            print('Page : {}, skip: {}'.format(x + 1, skip))
            # don't get any new records since the elastic items are retrieved
            cursor = service.get_from_mongo(request, {'_created': {'$lte': consistency_record['started_at']}})
            cursor.skip(skip)
            cursor.limit(self.default_page_size)
            cursor = list(cursor)
            mongo_items.extend([(str(mongo_item['_id']), mongo_item['_etag']) for mongo_item in cursor])
            updated_mongo_items.extend([mongo_item['_id'] for mongo_item in cursor
                                       if mongo_item['_updated'] > consistency_record['started_at']])

        return mongo_items, updated_mongo_items

    def get_elastic_items(self, resource_name, elasticsearch_index, elasticsearch_url):
        # get the all hits from elastic
        post_data = {'fields': '_etag'}
        response = requests.post('{}/{}/{}/{}'.format(elasticsearch_url,
                                 elasticsearch_index,
                                 resource_name,
                                 '_search?size=250000&q=*:*'),
                                 params=post_data)
        elastic_results = response.json()["hits"]["hits"]
        elastic_items = [(str(elastic_item['_id']), elastic_item.get('fields', {}).get('_etag', [0])[0])
                         for elastic_item in elastic_results]
        return elastic_items

    def process_results(self, consistency_record, elastic_items, mongo_items, updated_mongo_items):
        # form the sets
        mongo_item_ids = list(map(list, zip(*mongo_items)))[0]
        mongo_item_ids_set = set(mongo_item_ids)
        elastic_item_ids = list(map(list, zip(*elastic_items)))[0]
        elastic_item_ids_set = set(elastic_item_ids)
        mongo_items_set = set(mongo_items)
        elastic_items_set = set(elastic_items)
        updated_mongo_items_set = set(updated_mongo_items)

        # items that exist both in mongo and elastic with the same etags
        shared_items = mongo_items_set & elastic_items_set
        # items that exist only in mongo but not in elastic
        mongo_only = mongo_item_ids_set - elastic_item_ids_set
        # items that exist only in elastic but not in mongo
        elastic_only = elastic_item_ids_set - mongo_item_ids_set
        # items that exist both in mongo and elastic with different etags
        # filter out the ones that has been updated since elastic is queried
        different_items = (elastic_items_set ^ mongo_items_set) - updated_mongo_items_set
        if len(different_items) > 0:
            different_items = set(list(map(list, zip(*list(different_items))))[0]) \
                - updated_mongo_items_set \
                - mongo_only \
                - elastic_only

        consistency_record['completed_at'] = utcnow()
        consistency_record['mongo'] = len(mongo_items)
        consistency_record['elastic'] = len(elastic_items)
        consistency_record['identical'] = len(shared_items)
        consistency_record['mongo_only'] = len(mongo_only)
        consistency_record['elastic_only'] = len(elastic_only)
        consistency_record['inconsistent'] = len(different_items)

        records = {}
        if len(mongo_only) > 0:
            records['mongo_only'] = list(mongo_only)
        if len(elastic_only) > 0:
            records['elastic_only'] = list(elastic_only)
        if len(different_items) > 0:
            records['inconsistent'] = list(different_items)

        consistency_record['records'] = records

    def run(self, resource_name, elasticsearch_url, elasticsearch_index):
        """
        Compares the records in mongo and elastic for a given collection
        Saves the results to "consistency" collection
        :param resource_name: Name of the collection i.e. ingest, archive, published, text_archive
        :param elasticsearch_url: url of the elasticsearch
        :param elasticsearch_index: name of the index
        :return: dictionary of findings
        """

        print('Comparing data in mongo:{} and elastic:{}'.format(resource_name, resource_name))
        consistency_record = {}
        consistency_record['started_at'] = utcnow()
        consistency_record['resource_name'] = resource_name

        elastic_items = self.get_elastic_items(resource_name, elasticsearch_index, elasticsearch_url)
        mongo_items, updated_mongo_items = self.get_mongo_items(consistency_record, resource_name)
        self.process_results(consistency_record, elastic_items, mongo_items, updated_mongo_items)
        superdesk.get_resource_service('consistency').post([consistency_record])

        return consistency_record
