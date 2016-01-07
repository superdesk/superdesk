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
import logging
from superdesk import get_resource_service
from flask import current_app as app
from apps.archive.archive import SOURCE as ARCHIVE
from apps.archive.common import generate_unique_id_and_name, remove_unwanted, insert_into_versions
from superdesk.metadata.item import GUID_TAG, FAMILY_ID, ITEM_STATE, CONTENT_STATE
from superdesk.metadata.utils import generate_guid

logger = logging.getLogger(__name__)


class AppScaffoldDataCommand(superdesk.Command):
    """
    Initialize the application with some random data fetched from archived.
    Text archive dump must be restored before running this command as well as 'app:initialize_data'
    command to bootstrap the system with desks/users.
    """

    option_list = [
        superdesk.Option('--no-of-stories', '-n', dest='no_of_stories', default='200')
    ]

    def run(self, no_of_stories):
        logger.info('Starting scaffolding')
        no_of_stories = int(no_of_stories)

        desks = get_resource_service('desks').get(None, {})

        for i, desk in enumerate(desks):
            logger.info('Adding items for desk:' + str(desk['_id']))
            self.ingest_items_for(desk, no_of_stories, i + 1)
        return 0

    def ingest_items_for(self, desk, no_of_stories, skip_index):
        desk_id = desk['_id']
        stage_id = desk['incoming_stage']

        bucket_size = min(100, no_of_stories)

        no_of_buckets = len(range(0, no_of_stories, bucket_size))

        for x in range(0, no_of_buckets):
            skip = x * bucket_size * skip_index
            logger.info('Page : {}, skip: {}'.format(x + 1, skip))
            cursor = get_resource_service('published').get_from_mongo(None, {})
            cursor.skip(skip)
            cursor.limit(bucket_size)
            items = list(cursor)
            logger.info('Inserting {} items'.format(len(items)))
            archive_items = []

            for item in items:
                dest_doc = dict(item)
                new_id = generate_guid(type=GUID_TAG)
                dest_doc[app.config['ID_FIELD']] = new_id
                dest_doc['guid'] = new_id
                generate_unique_id_and_name(dest_doc)

                dest_doc[app.config['VERSION']] = 1
                dest_doc[ITEM_STATE] = CONTENT_STATE.FETCHED
                user_id = desk.get('members', [{'user': None}])[0].get('user')
                dest_doc['original_creator'] = user_id
                dest_doc['version_creator'] = user_id

                from apps.tasks import send_to
                send_to(dest_doc, desk_id=desk_id, stage_id=stage_id, user_id=user_id)
                dest_doc[app.config['VERSION']] = 1  # Above step increments the version and needs to reset
                dest_doc[FAMILY_ID] = item['_id']

                remove_unwanted(dest_doc)
                archive_items.append(dest_doc)

            get_resource_service(ARCHIVE).post(archive_items)
            for item in archive_items:
                insert_into_versions(id_=item[app.config['ID_FIELD']])


superdesk.command('app:scaffold_data', AppScaffoldDataCommand())
