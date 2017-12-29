# -*- coding: utf-8; -*-
# This file is part of Superdesk.
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
#
# Author  : mugur
# Creation: 2017-12-13 16:07

from superdesk.commands.data_updates import DataUpdate
from apps.prepopulate.app_initialize import AppInitializeWithDataCommand


class DataUpdate(DataUpdate):

    resource = 'content_types'
    profile = 'Story'

    def forwards(self, mongodb_collection, mongodb_database):
        AppInitializeWithDataCommand().run(entity_name='vocabularies')
        content_type = mongodb_collection.find_one({'label': self.profile})
        if content_type:
            subject = content_type['schema']['subject']
            if 'schema' not in subject:
                subject['schema'] = {}
            subject['schema']['type'] = 'dict'
            if 'schema' not in subject['schema']:
                subject['schema']['schema'] = {}
            subject['schema']['schema']['qcode'] = {}
            if 'scheme' not in subject['schema']['schema']:
                subject['schema']['schema']['scheme'] = {'allowed': []}
            subject['schema']['schema']['scheme']['allowed'].append('destination')

            max_order = 0
            for options in content_type['editor'].values():
                if type(options) == dict and options.get('order', 0) > max_order:
                    max_order = options['order']
            max_order += 1
            content_type['editor']['destination'] = {'order': max_order, 'sdWidth': 'full', 'required': False}

            mongodb_collection.update(
                {'label': self.profile},
                {'$set': {'schema': content_type['schema'], 'editor': content_type['editor']}}
            )

    def backwards(self, mongodb_collection, mongodb_database):
        pass
