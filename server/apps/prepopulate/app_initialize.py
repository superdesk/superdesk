import os
import json
import superdesk

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

        print('Data import finished')

    def import_file(self, file_name, service):
        file = os.path.join(superdesk.app.config.get('APP_ABSPATH'), 'apps', 'prepopulate', 'data_initialization',
                            file_name)
        with open(file, 'rt') as app_prepopulation:
            json_data = json.loads(app_prepopulation.read())
            data = [app.data.mongo._mongotize(item, service.datasource) for item in json_data]
            service.post(data)
        print('File imported successfully:', file_name)


superdesk.command('app:initialize_data', AppInitializeWithDataCommand())
