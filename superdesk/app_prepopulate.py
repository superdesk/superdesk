import json
import os

from superdesk import get_resource_service
import superdesk


def apply_placeholders(placeholders, text):
    if not placeholders or not text:
        return text
    for tag, value in placeholders.items():
        text = text.replace(tag, value)
    return text


class AppPrepopulateCommand(superdesk.Command):
    def run(self):
        placeholders = {}
        file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'app_prepopulate_data.json')
        with open(file, 'rt') as app_prepopulation:
            json_data = json.loads(app_prepopulation.read())
            for item in json_data:
                service = get_resource_service(item.get('resource', None))
                text = json.dumps(item.get('data', None))
                text = apply_placeholders(placeholders, text)
                data = json.loads(text)
                try:
                    item_id = service.post([data])
                    if 'id_name' in item:
                        placeholders[item.get('id_name')] = str(item_id[0])
                except Exception as e:
                    print(e)


superdesk.command('app:prepopulate', AppPrepopulateCommand())
