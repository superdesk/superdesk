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


def clean_keywords(**kwargs):

    repo = kwargs.get('repo')
    if not repo:
        raise KeyError('Missing repo')

    service = superdesk.get_resource_service(repo)
    counter = 0

    for items in IndexFromMongo().get_mongo_items(repo, 500):
        print('Processing items from {} to {}'.format(counter * 500, counter * 500 + len(items)))

        for item in items:
            if item.get('guid', '').find('aapimage-') >= 0:
                try:
                    service.system_update(item['_id'], {'keywords': []}, item)
                    print('Keywords in item {} has been updated'.format(item['_id']))
                except Exception as ex:
                    print('Error in update: {}'.format(str(ex)))
            else:
                print('Nothing to update in item {}'.format(item['_id']))

        counter += 1

name = 'clean_keywords'
callback = clean_keywords
access_type = 'backend'
action_type = 'direct'
