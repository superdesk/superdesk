# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license
import superdesk
from superdesk.commands import IndexFromMongo


def rename_genre_value(**kwargs):

    repo = kwargs.get('repo')
    if not repo:
        raise KeyError('Missing repo')

    service = superdesk.get_resource_service(repo)
    counter = 0

    for items in IndexFromMongo().get_mongo_items(repo, 500):
        print('Processing items from {} to {}'.format(counter * 500, counter * 500 + len(items)))

        for item in items:
            modified = False
            update = {}
            try:
                if item.get('genre'):
                    for g in item.get('genre'):
                        if 'value' in g:
                            g['qcode'] = g.pop('value')
                            modified = True
                    update = {'genre': item.get('genre')}
                if modified:
                    service.system_update(item['_id'], update, item)
                    print('Genre in item {} has been updated with {}'.format(item['_id'], update))
                else:
                    print('Nothing to update in item {}'.format(item['_id']))
            except Exception as ex:
                print('Error in update: {}'.format(str(ex)))

        counter += 1

name = 'rename_genre_value'
callback = rename_genre_value
access_type = 'backend'
action_type = 'background-thread'
