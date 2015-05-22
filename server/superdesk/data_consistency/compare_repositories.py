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


class CompareRepositories(superdesk.Command):
    default_page_size = 500

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

        # get the all hits from elastic
        post_data = {'fields': '_etag'}
        response = requests.post('{}/{}/{}'.format(elasticsearch_url,
                                                   elasticsearch_index,
                                                   '_search?size=250000&q=*:*'),
                                 params=post_data)
        elastic_results = response.json()["hits"]["hits"]
        elastic_items = {elastic_item['_id']: elastic_item["fields"]['_etag'] for elastic_item in elastic_results}

        # get the records from mongo in chunks
        service = superdesk.get_resource_service(resource_name)
        cursor = service.get_from_mongo(None, {})
        count = cursor.count()
        no_of_buckets = len(range(0, count, self.default_page_size))
        mongo_items = {}
        for x in range(0, no_of_buckets):
            skip = x * self.default_page_size
            print('Page : {}, skip: {}'.format(x + 1, skip))
            # don't get any new records since the elastic items are retrieved
            cursor = service.get_from_mongo(None, {'_created': {'$lte': consistency_record['started_at']}})
            cursor.skip(skip)
            cursor.limit(self.default_page_size)
            current_mongo_items = {mongo_item['_id']: mongo_item['_etag'] for mongo_item in cursor}
            mongo_items.update(current_mongo_items)

        # form the sets
        mongo_items_set = set(mongo_items)
        elastic_items_set = set(elastic_items)

        # items that exist both in mongo and elastic with the same etags
        shared_items = mongo_items_set & elastic_items_set

        # items that exist only in mongo but not in elastic
        mongo_only = mongo_items_set - elastic_items_set

        # items that exist only in elastic but not in mongo
        elastic_only = elastic_items_set - mongo_items_set

        # items that exist both in mongo and elastic with different etags
        different_items = elastic_items_set ^ mongo_items_set

        consistency_record['completed_at'] = utcnow()
        consistency_record['resource_name'] = resource_name
        consistency_record['mongo'] = len(mongo_items)
        consistency_record['elastic'] = len(elastic_items)
        consistency_record['identical'] = len(shared_items)
        consistency_record['mongo_only'] = len(mongo_only)
        consistency_record['elastic_only'] = len(elastic_only)
        consistency_record['inconsistent'] = len(different_items)
        superdesk.get_resource_service('consistency').post([consistency_record])

        return consistency_record
