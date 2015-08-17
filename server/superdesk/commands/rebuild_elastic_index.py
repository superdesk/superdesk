# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


from superdesk.utils import get_random_string
from elasticsearch.helpers import reindex
from eve_elastic import get_es, get_indices
from flask import current_app as app
import elasticsearch
import superdesk


class RebuildElasticIndex(superdesk.Command):
    """
    Rebuild the elastic index from existing data by creating a new index with
    the same alias as the configured index, puts the new mapping and delete the old index.
    """
    def run(self):
        index_name = app.config['ELASTICSEARCH_INDEX']
        print('Starting index rebuilding for index: ', index_name)
        try:
            es = get_es(app.config['ELASTICSEARCH_URL'])
            clone_name = index_name + '-' + get_random_string()
            print('Creating index: ', clone_name)
            get_indices(es).create(clone_name)
            print('Putting mapping for index: ', clone_name)
            app.data.elastic.put_mapping(app, clone_name)
            print('Starting index rebuilding.')
            reindex(es, index_name, clone_name)
            print('Finished index rebuilding.')
            print('Deleting index: ', index_name)
            get_indices(es).delete(index_name)
            print('Creating alias: ', index_name)
            get_indices(es).put_alias(index_name, clone_name)
            print('Alias created.')
        except elasticsearch.exceptions.NotFoundError as nfe:
            print(nfe)
        print('Index {0} rebuilt successfully.'.format(index_name))

superdesk.command('app:rebuild_elastic_index', RebuildElasticIndex())
