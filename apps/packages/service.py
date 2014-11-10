from eve.utils import ParsedRequest
from superdesk.services import BaseService
from superdesk import SuperdeskError, get_resource_service
from apps.archive.common import on_create_item


class PackageService(BaseService):

    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        return self.backend.get('packages', req=req, lookup=lookup)

    def on_create(self, docs):
        on_create_item(docs)
        self.check_package_associations(docs)

    def check_package_associations(self, docs):
        for doc in docs:
            doc['type'] = 'composite'
            associations = doc.get('associations', [])
            if len(associations) == 0:
                raise SuperdeskError(message='No content associated with the package.')

            for assoc in associations:
                self.extract_default_association_data(assoc)

    def extract_default_association_data(self, assoc):
        endpoint, item_id = assoc['itemRef'].split('/')[-2:]
        item = get_resource_service(endpoint).find_one(req=None, _id=item_id)
        if not item:
            raise SuperdeskError(message='Invalid item reference: ' + assoc['itemRef'])
        assoc['guid'] = item.get('guid', item_id)
        assoc['type'] = item.get('type')

    def on_update(self, updates, original):
        associations = updates.get('associations', [])
        for assoc in associations:
            self.extract_default_association_data(assoc)
