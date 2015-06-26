import superdesk

from superdesk import get_resource_service
from flask import current_app as app
from apps.tasks import send_to
from apps.archive.archive import SOURCE as ARCHIVE
from apps.archive.common import generate_guid, GUID_TAG, generate_unique_id_and_name, FAMILY_ID, \
    remove_unwanted, insert_into_versions


class AppScaffoldDataCommand(superdesk.Command):
    """
    Initialize the application with some random data fetchem from text_archive.
    Text archive dump must be restored before running this command as well as 'app:initialize_data'
    command to bootstrap the system with desks/users.
    """

    option_list = [
        superdesk.Option('--no-of-stories', '-n', dest='no_of_stories', default='200')
    ]

    def run(self, no_of_stories):
        self.logger.info('Starting scaffolding')
        no_of_stories = int(no_of_stories)

        desks = get_resource_service('desks').get(None, {})

        for i, desk in enumerate(desks):
            self.logger.info('Adding items for desk:' + str(desk['_id']))
            self.ingest_items_for(desk, no_of_stories, i + 1)
        return 0

    def ingest_items_for(self, desk, no_of_stories, skip_index):
        desk_id = desk['_id']
        stage_id = desk['incoming_stage']

        bucket_size = min(100, no_of_stories)

        no_of_buckets = len(range(0, no_of_stories, bucket_size))

        for x in range(0, no_of_buckets):
            skip = x * bucket_size * skip_index
            self.logger.info('Page : {}, skip: {}'.format(x + 1, skip))
            cursor = get_resource_service('text_archive').get_from_mongo(None, {})
            cursor.skip(skip)
            cursor.limit(bucket_size)
            items = list(cursor)
            self.logger.info('Inserting {} items'.format(len(items)))
            archive_items = []

            for item in items:
                dest_doc = dict(item)
                new_id = generate_guid(type=GUID_TAG)
                dest_doc['_id'] = new_id
                dest_doc['guid'] = new_id
                generate_unique_id_and_name(dest_doc)

                dest_doc[app.config['VERSION']] = 1
                dest_doc['state'] = 'fetched'
                user_id = desk.get('members', [{'user': None}])[0].get('user')
                dest_doc['original_creator'] = user_id
                dest_doc['version_creator'] = user_id
                send_to(dest_doc, desk_id=desk_id, stage_id=stage_id, user_id=user_id)
                dest_doc[FAMILY_ID] = item['_id']

                remove_unwanted(dest_doc)
                archive_items.append(dest_doc)

            get_resource_service(ARCHIVE).post(archive_items)
            for item in archive_items:
                insert_into_versions(id_=item['_id'])


superdesk.command('app:scaffold_data', AppScaffoldDataCommand())
