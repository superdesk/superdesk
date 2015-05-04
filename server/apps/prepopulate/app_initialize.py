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
    'roles': ('roles.json', 'name'),
    'users': ('users.json', [('first_name', pymongo.ASCENDING),
                             ('last_name', pymongo.DESCENDING)]),
    'desks': ('desks.json', 'incoming_stage'),
    'stages': ('stages.json', 'desk'),
    'groups': ('groups.json', ''),
    'vocabularies': ('vocabularies.json', ''),
    'content_templates': ('content_templates.json', 'template_name')
}


class AppInitializeWithDataCommand(superdesk.Command):
    """
    Initialize application with predifined data for various entities.
    Entities supported: [roles, users, desks, stages, groups, vocabularies, content_templates].
    If no --entity-name parameter is supplied, all the entities are inserted.
    """

    option_list = [
        superdesk.Option('--entity-name', '-n', dest='entity_name', default='')
    ]

    def run(self, entity_name=None):
        print('Starting data import')

        if entity_name:
            (file_name, index_params) = __entities__[entity_name]
            self.import_file(entity_name, file_name, index_params)
            return 0

        for name, (file_name, index_params) in __entities__.items():
            self.import_file(name, file_name, index_params)

        print('Data import finished')
        return 0

    def import_file(self, entity_name, file_name, index_params):
        file = os.path.join(superdesk.app.config.get('APP_ABSPATH'), 'apps', 'prepopulate', 'data_initialization',
                            file_name)
        with open(file, 'rt') as app_prepopulation:
            json_data = json.loads(app_prepopulation.read())
            service = get_resource_service(entity_name)
            data = [app.data.mongo._mongotize(item, service.datasource) for item in json_data]
            service.post(data)
            print('File {} imported successfully.'.format(file_name))

        if index_params:
            app.data.mongo.pymongo().db[entity_name].create_index(index_params)
            print('Index for {} created successfully.'.format(entity_name))


superdesk.command('app:initialize_data', AppInitializeWithDataCommand())
