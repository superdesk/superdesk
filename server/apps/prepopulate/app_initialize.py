import os
import json
import superdesk
import pymongo
import settings
import logging

from superdesk import get_resource_service
from flask import current_app as app
from re import findall

logger = logging.getLogger(__name__)

"""
App initialization information, maps resource name to the file containing the data
and the index to be created for the resource and the boolean flag to update the
resource or not.
__entities__ = {
    "resource_name": ("file_name", "index_params", "do_patch")
}
"file_name" (str): name of the file containing seed data
"index_params list: List of key (field or List of tuple as required by pymongo create_index function.
http://api.mongodb.org/python/current/api/pymongo/collection.html
For example:
[[("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING)], "username"] will create two indexes
- composite index of "first_name", "last_name" field.
- index on username field.
Alternatively index param can be specified as
[[("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING)], [("username", pymongo.ASCENDING)]]
Options can be sent to index creation and in this case the last element in the list is the options
dictionary:
[[("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING)], {'sparse': True}]]
"""
__entities__ = {
    'roles': ('roles.json', ['name'], False),
    'users': ('users.json', [[('first_name', pymongo.ASCENDING),
                             ('last_name', pymongo.DESCENDING)],
                             'username'], False),
    'desks': ('desks.json', ['incoming_stage'], False),
    'stages': ('stages.json', ['desk'], False),
    'groups': ('groups.json', '', False),
    'vocabularies': ('vocabularies.json', '', True),
    'validators': ('validators.json', '', True),
    'content_templates': ('content_templates.json', ['template_name'], False),
    'ingest_providers': ('ingest_providers.json', '', True),
    'published': (None, [[('expiry', pymongo.ASCENDING),
                          ('_created', pymongo.ASCENDING),
                          ('state', pymongo.ASCENDING)],
                         [('item_id', pymongo.ASCENDING),
                          ('state', pymongo.ASCENDING)],
                         [('publish_schedule', pymongo.ASCENDING),
                          ('state', pymongo.ASCENDING)]], False),
    'activity': (None, [[('_created', pymongo.DESCENDING),
                         {'expireAfterSeconds': 86400}],
                        [('item', pymongo.ASCENDING),
                         ('read', pymongo.ASCENDING),
                         ('user', pymongo.ASCENDING)],
                        [('resource', pymongo.ASCENDING),
                         ('data.provider_id', pymongo.ASCENDING)]], False),
    'archive': (None, [[('_updated', pymongo.ASCENDING)],
                       [('expiry', pymongo.ASCENDING),
                        ('state', pymongo.ASCENDING)],
                       [('type', pymongo.ASCENDING)],
                       [('groups.refs.residRef', pymongo.ASCENDING), {'sparse': True}],
                       [('publish_schedule', pymongo.ASCENDING),
                        ('state', pymongo.ASCENDING)],
                       [('unique_name', pymongo.ASCENDING)]], False),
    'archive_versions': (None, [[('_id_document', pymongo.ASCENDING),
                                 ('_current_version', pymongo.ASCENDING)]], False),
    'ingest': (None, [[('expiry', pymongo.ASCENDING),
                       ('ingest_provider', pymongo.ASCENDING)],
                      [('guid', pymongo.ASCENDING)]], False),
    'publish_queue': (None, [[('_created', pymongo.DESCENDING),
                              ('state', pymongo.ASCENDING),
                              ('destination.delivery_type', pymongo.ASCENDING)],
                             [('item_id', pymongo.ASCENDING),
                              ('item_version', pymongo.ASCENDING)],
                             [('state', pymongo.ASCENDING),
                              ('destination.delivery_type', pymongo.ASCENDING)],
                             [('subscriber_id', pymongo.ASCENDING)],
                             [('_updated', pymongo.DESCENDING)]], False),
    'archived': (None, [[('archived_id', pymongo.ASCENDING), {'unique': True}]], False),
    'legal_archive_versions': (None, [[('_id_document', pymongo.ASCENDING),
                                       ('_current_version', pymongo.ASCENDING)]], False),
    'legal_publish_queue': (None, [[('_updated', pymongo.DESCENDING)]], False)
}


class AppInitializeWithDataCommand(superdesk.Command):
    """
    Initialize application with predefined data for various entities.
    Entities supported: [roles, users, desks, stages, groups, vocabularies, validators, content_templates].
    If no --entity-name parameter is supplied, all the entities are inserted.
    The entities [vocabularies, validators] will be updated with the predefined data if it already exists,
    no action will be taken for the other entities.
    """

    option_list = [
        superdesk.Option('--entity-name', '-n', dest='entity_name', default='')
    ]

    def run(self, entity_name=None, index_only='false'):
        logger.info('Starting data import')
        if entity_name:
            (file_name, index_params, do_patch) = __entities__[entity_name]
            self.import_file(entity_name, file_name, index_params, do_patch)
            return 0

        for name, (file_name, index_params, do_patch) in __entities__.items():
            try:
                self.import_file(name, file_name, index_params, do_patch)
            except Exception as ex:
                logger.info('Exception loading entity {} from {}'.format(name, file_name))
                logger.exception(ex)

        logger.info('Data import finished')
        return 0

    def import_file(self, entity_name, file_name, index_params, do_patch=False):
        """
        imports seed data based on the entity_name (resource name) from the file_name specified.
        index_params use to create index for that entity/resource
        :param str entity_name: name of the resource
        :param str file_name: file name that contains seed data
        :param list index_params: list of indexes that is created on that entity.
        For example:
        [[("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING)], "username"] will create two indexes
        - composite index of "first_name", "last_name" field.
        - index on username field.
        Alternatively index param can be specified as
        [[("first_name", pymongo.ASCENDING), ("last_name", pymongo.ASCENDING)], [("username", pymongo.ASCENDING)]]
        Refer to pymongo create_index documentation for more information.
        http://api.mongodb.org/python/current/api/pymongo/collection.html
        :param bool do_patch: if True then patch the document else don't patch.
        """
        print('Config: ', app.config['APP_ABSPATH'])
        if file_name:
            file_path = os.path.join(app.config.get('APP_ABSPATH'), 'apps', 'prepopulate', 'data_initialization',
                                     file_name)
            print('Got file path: ', file_path)
            with open(file_path, 'rt') as app_prepopulation:
                service = get_resource_service(entity_name)
                json_data = json.loads(app_prepopulation.read())
                data = [fillEnvironmentVariables(item) for item in json_data]
                data = [app.data.mongo._mongotize(item, service.datasource) for item in data if item]
                existing_data = []
                existing = service.get_from_mongo(None, {})
                update_data = True
                if not do_patch and existing.count() > 0:
                    logger.info('Data already exists for {} none will be loaded'.format(entity_name))
                    update_data = False
                elif do_patch and existing.count() > 0:
                    logger.info('Data already exists for {} it will be updated'.format(entity_name))

                if update_data:
                    if do_patch:
                        for item in existing:
                            for loaded_item in data:
                                if '_id' in loaded_item and loaded_item['_id'] == item['_id']:
                                    existing_data.append(loaded_item)
                                    data.remove(loaded_item)

                    if data:
                        service.post(data)

                    if existing_data and do_patch:
                        for item in existing_data:
                            service.patch(item['_id'], item)

                logger.info('File {} imported successfully.'.format(file_name))

        if index_params:
            for index in index_params:
                crt_index = list(index) if isinstance(index, list) else index
                options = crt_index.pop() if isinstance(crt_index[-1], dict) and isinstance(index, list) else {}
                collection = app.data.mongo.pymongo(resource=entity_name).db[entity_name]
                index_name = collection.create_index(crt_index, cache_for=300, **options)
                logger.info('Index: {} for collection {} created successfully.'.format(index_name, entity_name))


def fillEnvironmentVariables(item):
    variables = {}
    text = json.dumps(item)

    for variable in findall('#ENV_([^#"]+)#', text):
        value = settings.env(variable, None)
        if not value:
            return None
        else:
            variables[variable] = value

    for name in variables:
        text = text.replace('#ENV_%s#' % name, variables[name])

    return json.loads(text)


superdesk.command('app:initialize_data', AppInitializeWithDataCommand())
