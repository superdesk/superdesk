import os
import json
import superdesk
import pymongo

from superdesk import get_resource_service
from flask import current_app as app


"""
App initialization information, maps resource name to the file containing the data
and the index to be created for the resource.
"""
__entities__ = {
    'roles': ('roles.json', 'name', False),
    'users': ('users.json', [('first_name', pymongo.ASCENDING),
                             ('last_name', pymongo.DESCENDING)], False),
    'desks': ('desks.json', 'incoming_stage', False),
    'stages': ('stages.json', 'desk', False),
    'groups': ('groups.json', '', False),
    'vocabularies': ('vocabularies.json', '', True),
    'validators': ('validators.json', '', True),
    'content_templates': ('content_templates.json', 'template_name', False),
    'published': (None, [('item_id', pymongo.ASCENDING),
                         ('state', pymongo.ASCENDING)], False)
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

    def run(self, entity_name=None):
        self.logger.info('Starting data import')

        if entity_name:
            (file_name, index_params, do_patch) = __entities__[entity_name]
            self.import_file(entity_name, file_name, index_params, do_patch)
            return 0

        for name, (file_name, index_params, do_patch) in __entities__.items():
            try:
                self.import_file(name, file_name, index_params, do_patch)
            except Exception as ex:
                self.logger.info('Exception loading entity {} from {}'.format(name, file_name))
                self.logger.exception(ex)

        self.logger.info('Data import finished')
        return 0

    def import_file(self, entity_name, file_name, index_params, do_patch=False):

        if file_name:
            file = os.path.join(superdesk.app.config.get('APP_ABSPATH'), 'apps', 'prepopulate', 'data_initialization',
                                file_name)
            with open(file, 'rt') as app_prepopulation:
                json_data = json.loads(app_prepopulation.read())
                service = get_resource_service(entity_name)
                data = [app.data.mongo._mongotize(item, service.datasource) for item in json_data]
                existing_data = []
                existing = service.get_from_mongo(None, {})
                if not do_patch and existing.count() > 0:
                    self.logger.info('Data already exists for {} none will be loaded'.format(entity_name))
                    return
                elif do_patch and existing.count() > 0:
                    self.logger.info('Data already exists for {} it will be updated'.format(entity_name))
                if do_patch:
                    for item in existing:
                        for loaded_item in data:
                            if '_id' in loaded_item and loaded_item['_id'] == item['_id']:
                                existing_data.append(loaded_item)
                                data.remove(loaded_item)
                if data and existing.count() == 0:
                    service.post(data)
                if existing_data and do_patch:
                    for item in existing_data:
                        service.patch(item['_id'], item)
                self.logger.info('File {} imported successfully.'.format(file_name))

        if index_params:
            app.data.mongo.pymongo(resource=entity_name).db[entity_name].create_index(index_params)
            self.logger.info('Index for {} created successfully.'.format(entity_name))


superdesk.command('app:initialize_data', AppInitializeWithDataCommand())
