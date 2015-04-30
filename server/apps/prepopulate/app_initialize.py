import os
import json
import superdesk
import pymongo

from superdesk import get_resource_service
from flask import current_app as app


class AppInitializeWithDataCommand(superdesk.Command):

    def run(self):
        print('Starting data import')
        service = get_resource_service('roles')
        self.import_file('roles.json', service)

        service = get_resource_service('users')
        self.import_file('users.json', service)

        service = get_resource_service('desks')
        self.import_file('desks.json', service)

        service = get_resource_service('stages')
        self.import_file('stages.json', service)

        service = get_resource_service('groups')
        self.import_file('groups.json', service)

        service = get_resource_service('vocabularies')
        self.import_file('vocabularies.json', service)

        service = get_resource_service('content_templates')
        self.import_file('content_templates.json', service)

        print('Data import finished')

        print('Starting indexes creation')
        app.data.mongo.pymongo().db['roles'].create_index('name')
        app.data.mongo.pymongo().db['users'].create_index([('first_name', pymongo.ASCENDING),
                                                           ('last_name', pymongo.DESCENDING)])
        app.data.mongo.pymongo().db['desks'].create_index('incoming_stage')
        app.data.mongo.pymongo().db['stages'].create_index('desk')
        print('Finished index creation')

        return 0

    def import_file(self, file_name, service):
        file = os.path.join(superdesk.app.config.get('APP_ABSPATH'), 'apps', 'prepopulate', 'data_initialization',
                            file_name)
        with open(file, 'rt') as app_prepopulation:
            json_data = json.loads(app_prepopulation.read())
            data = [app.data.mongo._mongotize(item, service.datasource) for item in json_data]
            service.post(data)
        print('File imported successfully:', file_name)


superdesk.command('app:initialize_data', AppInitializeWithDataCommand())
