
from superdesk.services import BaseService
from superdesk import SuperdeskError, get_resource_service
from apps.archive.common import on_create_item


class PackageService(BaseService):

    def on_create(self, docs):
        on_create_item(docs)

        for doc in docs:
            associations = doc.get('associations', [])
            if len(associations) == 0:
                raise SuperdeskError(message='No content associated with the package.')

            for assoc in associations:
                self.extract_default_association_data(assoc)

            doc['type'] = 'composite' if len(associations) > 1 else associations[0].get('type')

    def extract_default_association_data(self, assoc):
        endpoint, item_id = assoc['itemRef'].split('/')[-2:]
        item = get_resource_service(endpoint).find_one(req=None, _id=item_id)
        if not item:
            raise SuperdeskError(message='Invalid item reference: ' + assoc['itemRef'])
        assoc['guid'] = item.get('guid', item_id)
        assoc['type'] = item.get('type')
