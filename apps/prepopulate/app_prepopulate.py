import json
import os

from superdesk import get_resource_service
import superdesk
from superdesk.resource import Resource
from superdesk.services import BaseService
from superdesk.tests import drop_elastic, drop_mongo


def apply_placeholders(placeholders, text):
    if not placeholders or not text:
        return text
    for tag, value in placeholders.items():
        text = text.replace(tag, value)
    return text


def prepopulate_data(file_name):
    placeholders = {}
    file = os.path.join(os.path.abspath(os.path.dirname(__file__)), file_name)
    with open(file, 'rt') as app_prepopulation:
        json_data = json.loads(app_prepopulation.read())
        for item in json_data:
            service = get_resource_service(item.get('resource', None))
            id_name = item.get('id_name', None)
            text = json.dumps(item.get('data', None))
            text = apply_placeholders(placeholders, text)
            data = json.loads(text)
            try:
                ids = service.post([data])
                if id_name:
                    placeholders[id_name] = str(ids[0])
            except Exception as e:
                print('Exception:', e)


prepopulate_schema = {
    'profile': {
        'type': 'string',
        'required': False,
        'default': 'app_prepopulate_data'
    },
    'remove_first': {
        'type': 'boolean',
        'required': False,
        'default': True
    }
}


class PrepopulateResource(Resource):
    """Prepopulate application data."""
    schema = prepopulate_schema
    resource_methods = ['POST']


class PrepopulateService(BaseService):
    def create(self, docs, **kwargs):
        for doc in docs:
            if doc.get('remove_first'):
                drop_elastic(superdesk.app)
                drop_mongo(superdesk.app)
            prepopulate_data(doc.get('profile') + '.json')
        return ['OK']


class AppPrepopulateCommand(superdesk.Command):
    def run(self):
        prepopulate_data('app_prepopulate_data.json')


superdesk.command('app:prepopulate', AppPrepopulateCommand())
