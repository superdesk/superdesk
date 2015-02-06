# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from .utils import get_random_string
from elasticsearch.helpers import reindex
from eve_elastic import get_es, get_indices
import elasticsearch
import superdesk


class RebuildElasticIndex(superdesk.Command):
    def run(self):
        index_name = superdesk.app.config['ELASTICSEARCH_INDEX']
        try:
            es = get_es(superdesk.app.config['ELASTICSEARCH_URL'])
            clone_name = index_name + '-' + get_random_string()
            print('Starting index rebuilding for index: ' + index_name)
            reindex(es, index_name, clone_name)
            print('Finished index rebuilding.')
            print('Deleting index: ' + index_name)
            get_indices(es).delete(index_name)
            print('Creating alias: ' + index_name)
            get_indices(es).put_alias(index_name, clone_name)
            print('Alias created.')
        except elasticsearch.exceptions.NotFoundError as nfe:
            print(nfe)
        print('Index {0} rebuilt successfully.'.format(index_name))

superdesk.command('app:rebuild_elastic_index', RebuildElasticIndex())
