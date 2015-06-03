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
from superdesk.errors import BulkIndexError


class IndexFromMongo(superdesk.Command):
    """
    Index the specified mongo collection in the specified elastic collection/type.
    This will use the default APP mongo DB to read the data and the default Elastic APP index.
    """
    option_list = [
        superdesk.Option('--from', '-f', dest='mongo_collection_name', required=True),
        superdesk.Option('--page-size', '-p', dest='page_size')
    ]
    default_page_size = 500

    def run(self, mongo_collection_name, page_size):
        bucket_size = int(page_size) if page_size else self.default_page_size
        print('Indexing data from mongo/{} to elastic/{}'.format(mongo_collection_name, mongo_collection_name))

        service = superdesk.get_resource_service(mongo_collection_name)
        cursor = service.get_from_mongo(None, {})
        count = cursor.count()
        no_of_buckets = len(range(0, count, bucket_size))
        print('Number of items to index: {}, pages={}'.format(count, no_of_buckets))

        for x in range(0, no_of_buckets):
            skip = x * bucket_size
            print('Page : {}, skip: {}'.format(x + 1, skip))
            cursor = service.get_from_mongo(None, {})
            cursor.skip(skip)
            cursor.limit(bucket_size)
            items = list(cursor)
            print('Inserting {} items'.format(len(items)))
            success, failed = superdesk.app.data._search_backend(mongo_collection_name).bulk_insert(
                mongo_collection_name, items)
            print('Inserted {} items'.format(success))
            if failed:
                print('Failed to do bulk insert of items {}. Errors: {}'.format(len(failed), failed))
                raise BulkIndexError(resource=mongo_collection_name, errors=failed)

        return 'Finished indexing collection {}'.format(mongo_collection_name)


superdesk.command('app:index_from_mongo', IndexFromMongo())
