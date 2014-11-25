from collections import Counter
from eve.utils import ParsedRequest, config
from eve.validation import ValidationError
from superdesk.services import BaseService
from superdesk import SuperdeskError, get_resource_service
from apps.archive.common import on_create_item
from apps.content import LINKED_IN_PACKAGES
ASSOCIATIONS = 'refs'
ITEM_REF = 'residRef'
ID_REF = 'idRef'


class PackageService(BaseService):

    def get(self, req, lookup):
        if req is None:
            req = ParsedRequest()
        return self.backend.get('packages', req=req, lookup=lookup)

    def on_create(self, docs):
        on_create_item(docs)
        self.check_package_associations(docs)

    def on_created(self, docs):
        for (doc, assoc) in [(doc, assoc) for doc in docs
                             for assoc in self._get_associations(doc)]:
            self.update_link(doc[config.ID_FIELD], assoc)

    def on_update(self, updates, original):
        associations = self._get_associations(updates)
        self.check_for_duplicates(original, associations)
        for assoc in associations:
            self.extract_default_association_data(original, assoc)

    def on_updated(self, updates, original):
        for assoc in self._get_associations(updates):
            self.update_link(original[config.ID_FIELD], assoc)

    def on_deleted(self, doc):
        for assoc in self._get_associations(doc):
            self.update_link(doc[config.ID_FIELD], assoc, delete=True)

    def check_package_associations(self, docs):
        for (doc, group) in [(doc, group) for doc in docs for group in doc.get('groups', [])]:
            associations = group.get(ASSOCIATIONS, [])
            if len(associations) == 0:
                raise SuperdeskError(message='No content associated with the package.')

            self.check_for_duplicates(doc, associations)
            for assoc in associations:
                self.extract_default_association_data(group, assoc)

    def extract_default_association_data(self, package, assoc):
        if assoc.get(ID_REF):
            return

        item, item_id, endpoint = self.get_associated_item(assoc)
        self.check_for_circular_reference(package, item_id)
        assoc['guid'] = item.get('guid', item_id)
        assoc['type'] = item.get('type')

    def get_associated_item(self, assoc):
        endpoint, item_id = assoc[ITEM_REF].split('/')[-2:]
        item = get_resource_service(endpoint).find_one(req=None, _id=item_id)
        if not item:
            raise SuperdeskError(message='Invalid item reference: ' + assoc['itemRef'])
        return item, item_id, endpoint

    def update_link(self, package_id, assoc, delete=False):
        if assoc.get(ID_REF):
            return

        item, item_id, endpoint = self.get_associated_item(assoc)
        two_way_links = [d for d in item.get(LINKED_IN_PACKAGES, []) if not d['package'] == package_id]

        if not delete:
            two_way_links.append({'package': package_id})

        item[LINKED_IN_PACKAGES] = two_way_links
        del item[config.ID_FIELD]
        get_resource_service(endpoint).patch(item_id, item)

    def check_for_duplicates(self, package, associations):
        counter = Counter()
        package_id = package[config.ID_FIELD]
        for itemRef in [assoc[ITEM_REF] for assoc in associations if assoc.get(ITEM_REF)]:
            if itemRef == package_id:
                raise SuperdeskError(message='Trying to self reference as an association.')
            counter[itemRef] += 1

        if any(itemRef for itemRef, value in counter.items() if value > 1):
            raise SuperdeskError(message='Content associated multiple times')

    def check_for_circular_reference(self, package, item_id):
        if any(d for d in package.get(LINKED_IN_PACKAGES, []) if d['package'] == item_id):
            raise ValidationError('Trying to create a circular reference to: ' + item_id)

    def _get_associations(self, doc):
        return [assoc for group in doc.get('groups', [])
                for assoc in group.get(ASSOCIATIONS, [])]
